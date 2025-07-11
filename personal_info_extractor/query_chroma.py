import chromadb
import os
import json
from schema.personal_profile import PersonalProfile

CHROMA_DB_PATH = "chroma_db"
COLLECTION_NAME = "personal_profiles"

def view_chroma_profiles():
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
    except Exception as e:
        print(f"Error connecting to ChromaDB: {e}")
        print("Ensure the 'chroma_db' directory exists and is not locked.")
        return

    print(f"\n--- Contents of ChromaDB Collection: '{COLLECTION_NAME}' ---")
    print(f"Total documents in collection: {collection.count()}")

    if collection.count() == 0:
        print("No profiles found in the database.")
        return

    results = collection.get(
        ids=None,        
        limit=None,       
        include=['metadatas', 'documents']
    )

    if not results or not results['metadatas']:
        print("No results or metadatas found.")
        return

    print("\n--- Retrieved Profiles ---")
    for i, metadata_item in enumerate(results['metadatas']):
        doc_id = results['ids'][i]
        
        profile_json_string = metadata_item.get('profile_data')
        
        if profile_json_string:
            try:
                profile_dict = json.loads(profile_json_string)
                
                profile_fields = PersonalProfile.model_fields.items()

                for field_name, field_info in profile_fields:
                    if field_name in profile_dict and isinstance(profile_dict[field_name], dict) and not profile_dict[field_name]:
                        if field_info.annotation == list:
                            profile_dict[field_name] = []
                        else:
                            profile_dict[field_name] = None
                    elif field_name in profile_dict and isinstance(profile_dict[field_name], dict) and "values" in profile_dict[field_name] and not profile_dict[field_name]['values']:
                        profile_dict[field_name]['values'] = []

                profile_obj = PersonalProfile.model_validate(profile_dict) # For Pydantic v2
                # profile_obj = PersonalProfile.parse_obj(profile_dict) # For Pydantic v1
                
                print(f"\nProfile ID: {doc_id}")
                print(f"  Name: {profile_obj.name if profile_obj.name else 'N/A'}")
                print(f"  Age: {profile_obj.age if profile_obj.age is not None else 'N/A'}")
                print(f"  Location: {profile_obj.location if profile_obj.location else 'N/A'}")
                print(f"  Education: {profile_obj.education if profile_obj.education else 'N/A'}")
                print(f"  Work Experience: {', '.join(profile_obj.work_experience) if profile_obj.work_experience else 'N/A'}")
                print(f"  Interests: {', '.join(profile_obj.interests) if profile_obj.interests else 'N/A'}")
                print(f"  Personality Traits: {', '.join(profile_obj.personality_traits) if profile_obj.personality_traits else 'N/A'}")
                print(f"  Skills: {', '.join(profile_obj.skills) if profile_obj.skills else 'N/A'}")
                print(f"  Languages Spoken: {', '.join(profile_obj.languages_spoken) if profile_obj.languages_spoken else 'N/A'}")
                print(f"  Achievements: {', '.join(profile_obj.achievements) if profile_obj.achievements else 'N/A'}")
                print(f"  Contact Info: {', '.join(profile_obj.contact_info) if profile_obj.contact_info else 'N/A'}")
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for profile ID {doc_id}: {e}")
            except Exception as e:
                print(f"Error processing profile ID {doc_id}: {e}")
        else:
            print(f"Profile ID: {doc_id} - No 'profile_data' found in metadata.")

if __name__ == "__main__":
    view_chroma_profiles()