from typing import Dict, Any
from schema.personal_profile import PersonalProfile, State

def validate_extracted_info(state: State) -> Dict[str, Any]:

    # Initialize validation error lists
    current_validation_errors = state.validation_errors
    current_errors = state.errors

    # Check if the extracted_info is present and is of type PersonalProfile
    if state.target_profile_id:
        return {
            "current_state": "validation_complete",
            "validation_errors": [],
            "errors": current_errors
        }
    else:
        extracted_profile = state.extracted_info
        if not isinstance(extracted_profile, PersonalProfile):
            current_validation_errors.append("Extracted information is not a valid PersonalProfile object or is missing.")
            return {
                "current_state": "validation_failed",
                "validation_errors": current_validation_errors,
                "errors": current_errors
            }

    # Other validation checks based on the extracted profile
    try:
        if extracted_profile.name is None or extracted_profile.name.strip() == "":
            current_validation_errors.append("Extracted 'name' is missing or empty. Cannot store profile.")

        if extracted_profile.age is not None and (extracted_profile.age < 0 or extracted_profile.age > 120):
            current_validation_errors.append(f"Extracted 'age' ({extracted_profile.age}) is outside typical human range (0-120).")
        
        if current_validation_errors:
            return {
                "current_state": "validation_failed",
                "validation_errors": current_validation_errors,
                "errors": current_errors
            }
        else:
            return {
                "current_state": "validation_complete",
                "validation_errors": [], 
                "errors": current_errors
            }
        
    except Exception as e:
        current_errors.append(f"Error during validation: {str(e)}")
        return {
            "current_state": "validation_error",
            "validation_errors": current_validation_errors,
            "errors": current_errors
        }
