from typing import Dict, Any, List
from schema.personal_profile import State, PersonalProfile
from langchain_openai import OpenAIEmbeddings
import chromadb
import os
import json
from utils.profile_to_text import convert_profile_to_embeddable_text
from utils.chroma_utils import get_chroma_collection
from utils.profile_merger import merge_personal_profiles
import uuid

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
        _client.delete_collection(name=COLLECTION_NAME)
        _collection = _client.get_or_create_collection(name=COLLECTION_NAME)
    
    return _collection

try:
    _embeddings_model = OpenAIEmbeddings(model="text-embedding-ada-002")
except Exception as e:
    print(f"Warning: Could not initialize OpenAIEmbeddings. Ensure OPENAI_API_KEY is set. Error: {e}")
    _embeddings_model = None

def embed_and_store_profile(state: State) -> Dict[str, Any]:
    current_errors = list(state.errors)
    current_validation_errors = list(state.validation_errors)

    profile = state.extracted_info

    if (not profile or not isinstance(profile, PersonalProfile)) and not state.target_profile_id:
        current_errors.append("No valid PersonalProfile found for embedding and storage.")
        return {
            "current_state": "vector_db_error",
            "errors": current_errors,
            "validation_errors": current_validation_errors
        }
    
    if _embeddings_model is None:
        current_errors.append("Embedding model not initialized. Cannot store profile in vector DB.")
        return {
            "current_state": "vector_db_error",
            "errors": current_errors,
            "validation_errors": current_validation_errors
        }

    try:
        doc_id = state.target_profile_id
        operation_type = "added"

        if doc_id is not None:

            collection = get_chroma_collection()
            if collection is None:
                raise RuntimeError("ChromaDB collection could not be initialized for update operation.")
            
            results = collection.get(ids=[doc_id], include=['metadatas'])

            existing_profile_dict = None
            if results and results['metadatas'] and len(results['metadatas']) > 0:
                profile_json_string = results['metadatas'][0].get('profile_data')
                if profile_json_string:
                    existing_profile_dict = json.loads(profile_json_string)
            
            if existing_profile_dict:
                existing_profile_obj = PersonalProfile.model_validate(existing_profile_dict)
                print(f"Found existing profile '{existing_profile_obj.name if existing_profile_obj.name else 'Unnamed'}' with ID {doc_id}. Merging new data.")

                profile = merge_personal_profiles(existing_profile_obj, profile)
                operation_type = "updated"

            else:
                current_errors.append(f"Warning: Target profile with ID '{doc_id}' not found for update. Adding as a new profile instead.")
                doc_id = str(uuid.uuid4())
                operation_type = "added (fallback)"

        else:
            doc_id = str(uuid.uuid4())
            operation_type = "embedded and stored"

        profile_text = convert_profile_to_embeddable_text(profile)
        
        if not profile_text.strip():
            current_errors.append("Generated empty text for profile embedding. Skipping vector DB storage.")
            return {
                "current_state": "vector_db_complete",
                "errors": current_errors,
                "validation_errors": current_validation_errors
            }

        embedding = _embeddings_model.embed_query(profile_text)

        collection = get_chroma_collection()
        if collection is None:
            current_errors.append("ChromaDB collection could not be initialized. Skipping vector DB storage.")
            return {
                "current_state": "vector_db_error",
                "errors": current_errors,
                "validation_errors": current_validation_errors
            }

        profile_json_string = json.dumps(profile.model_dump(exclude_none=True), ensure_ascii=False)

        if doc_id is not None and operation_type == "updated":
            collection.update(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[profile_text],
                metadatas=[{"profile_data": profile_json_string}]
            )
        else:
            collection.add(
                embeddings=[embedding],
                documents=[profile_text],
                metadatas=[{"profile_data": profile_json_string}],
                ids=[doc_id]
            )
        print(f"Successfully {operation_type} profile with ID: {doc_id}")

        return {
            "current_state": "vector_db_complete",
            "errors": current_errors,
            "validation_errors": current_validation_errors
        }

    except Exception as e:
        current_errors.append(f"Error embedding or storing profile in vector DB: {e}")
        return {
            "current_state": "vector_db_error",
            "errors": current_errors,
            "validation_errors": current_validation_errors
        }