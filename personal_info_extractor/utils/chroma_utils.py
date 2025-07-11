import chromadb
import os
import json
from schema.personal_profile import PersonalProfile
from typing import List

CHROMA_DB_PATH = "chroma_db"
COLLECTION_NAME = "personal_profiles"

_client = None
_collection = None

def get_chroma_collection():
    global _client, _collection
    if _client is None:
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
        _client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    try:
        _collection = _client.get_or_create_collection(name=COLLECTION_NAME)
        
    except Exception as e:
        print(f"Error getting/creating ChromaDB collection: {e}")
        if _client:
            try:
                _client.delete_collection(name=COLLECTION_NAME)
                _collection = _client.get_or_create_collection(name=COLLECTION_NAME)
                print("ChromaDB collection reset and recreated.")
            except Exception as e_retry:
                print(f"Failed to reset and recreate ChromaDB collection: {e_retry}")
                _collection = None
        else:
            _collection = None

    return _collection

def get_all_profiles_from_chroma() -> List[PersonalProfile]:

    collection = get_chroma_collection()
    if collection is None:
        return []

    try:
        results = collection.get(
            ids=None,
            include=['metadatas', 'documents']
        )

        profiles: List[PersonalProfile] = []
        if results and results['metadatas']:
            for metadata_item in results['metadatas']:
                profile_json_string = metadata_item.get('profile_data')
                if profile_json_string:
                    try:
                        profile_dict = json.loads(profile_json_string)
                        
                        profile_fields = PersonalProfile.model_fields.items()

                        for field_name, field_info in profile_fields:
                            if field_name in profile_dict and isinstance(profile_dict[field_name], dict) and not profile_dict[field_name]:
                                if field_info.annotation.__origin__ is list:
                                    profile_dict[field_name] = []
                                else:
                                    profile_dict[field_name] = None
                            elif field_name in profile_dict and isinstance(profile_dict[field_name], dict) and "values" in profile_dict[field_name] and not profile_dict[field_name]['values']:
                                profile_dict[field_name]['values'] = []

                        profile_obj = PersonalProfile.model_validate(profile_dict)
                        profiles.append(profile_obj)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON from ChromaDB metadata: {e}")
                    except Exception as e:
                        print(f"Error validating Pydantic model from ChromaDB data: {e}")

        return profiles
    
    except Exception as e:
        print(f"Error retrieving profiles from ChromaDB: {e}")
        return []
