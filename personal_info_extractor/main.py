from app import app
from schema.personal_profile import State, PersonalProfile
import os
from dotenv import load_dotenv

def run(file: str) -> PersonalProfile:
    load_dotenv()

    # Check if the OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set. Please set it in your .env file or system environment.")
        exit(1)

    # Validate the input file path
    if not file:
        state.errors.append("File path cannot be empty.")
        raise ValueError("File path cannot be empty.")

    # Get the file extension to determine input type
    try:
        input_type = file.split('.')[-1]
    except IndexError:
        state.errors.append("File path must include an extension to determine input type.")
        raise ValueError("File path must include an extension to determine input type.")
    
    if input_type == 'wav' or input_type == 'mp3' or input_type == 'm4a':
        input_type = 'audio'
    elif input_type == 'txt':
        input_type = 'text'
    else:
        state.errors.append("Unsupported input type. Use 'audio' or 'text'.")
        raise ValueError("Unsupported input type. Use 'audio' or 'text'.")

    # Initialize the state
    state = State(
        input_type=input_type,
        input_data=None,
        input_path=file,
        preprocessed_text=None,
        extracted_info=None,
        validation_errors=[],
        errors=[],
        current_state="initial"
    )

    result = app.invoke(state)

    # Check for errors in the result
    if result["current_state"] != "vector_db_complete" and result["current_state"] != "validation_failed":
        result["errors"].append("Processing did not complete successfully.")
        raise RuntimeError("Processing did not complete successfully. State: " + str(result["current_state"]) + " Errors: " + str(result["errors"]))

    if result["validation_errors"]:
        raise ValueError(f"Validation errors found: {result['validation_errors']}")

    return result["extracted_info"]

extracted_info = run("input/text8.txt")
print("Extraction complete. Extracted profile:")
print(extracted_info)