import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
import pandas as pd

# Ensure the environment variables are loaded
# This will load variables from a .env file if it exists, or from the system environment
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY environment variable not set. Please set it in your .env file or system environment.")
    st.stop()

# Import the app and schema components
try:
    from app import app
    from schema.personal_profile import State, PersonalProfile, LabeledString, LabeledInt, LabeledList
except ImportError as e:
    st.error(f"Failed to import backend components. Ensure 'app.py' and 'schema/personal_profile.py' are correctly defined and in your PYTHONPATH. Error: {e}")
    st.stop()

st.set_page_config(page_title="Personal Data Extractor", layout="centered")

st.title("🗣️ Personal Data & Preferences Extractor")
st.markdown("Upload an interview audio or text transcript to extract structured personal data and preferences.")

# --- File Uploader Section ---
st.subheader("1. Upload Interview Data")

uploaded_file = st.file_uploader(
    "Choose an audio file (.mp3, .wav, .m4a) or a text transcript (.txt)",
    type=["mp3", "wav", "m4a", "txt", "pdf"],
)

if 'processing_status' not in st.session_state:
    st.session_state['processing_status'] = ""
if 'final_state' not in st.session_state:
    st.session_state['final_state'] = None

if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension in ["mp3", "wav", "m4a"]:
        input_type = "audio"
    elif file_extension == "txt":
        input_type = "text"
    elif file_extension == "pdf":
        input_type = "pdf"
    else:
        st.error(f"Unsupported file type: .{file_extension}. Please upload an audio file (.mp3, .wav, .m4a) or a text transcript (.txt).")
        st.session_state['processing_status'] = "Unsupported file type."
        st.session_state['final_state'] = None
        st.stop()

    st.info(f"File type detected: {input_type} ({file_extension.upper()})")

    temp_file_path = None
    
    with st.spinner("Saving uploaded file temporarily..."):
        try:
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, f"uploaded_file_{os.urandom(8).hex()}.{file_extension}")
            
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            st.session_state['processing_status'] = f"File saved temporarily at: {temp_file_path}"
            st.success("File uploaded and saved successfully.")

        except Exception as e:
            st.error(f"Failed to save uploaded file: {e}")
            st.session_state['processing_status'] = f"Error saving file: {e}"
            st.session_state['final_state'] = None
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            st.stop()

# --- Extraction Section ---
if uploaded_file is not None and temp_file_path:
    st.markdown("---")
    st.subheader("2. Run Extraction")
    if st.button("Extract Data", use_container_width=True):
        st.session_state['processing_status'] = "Starting data extraction..."
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        initial_state = State(
            input_path=temp_file_path,
            input_type=input_type,
            input_data=None, 
            preprocessed_text=None,
            extracted_info=None,
            validation_errors=[],
            errors=[],
            current_state="initial",
            messages=[]
        )

        try:
            status_text.text("Running LangGraph pipeline (Preprocessing, Extraction, Validation)...")
            progress_bar.progress(25)
            
            st.session_state['final_state'] = app.invoke(initial_state)

            progress_bar.progress(100)
            status_text.text("LangGraph pipeline completed!")
            st.session_state['processing_status'] = "Extraction complete."

        except Exception as e:
            st.error(f"An unexpected error occurred during pipeline execution: {e}")
            st.session_state['processing_status'] = f"Pipeline failed: {e}"

            if st.session_state['final_state'] is None:
                 st.session_state['final_state'] = {"errors": [f"Unexpected error: {e}"], "current_state": "unexpected_error"}
            else:
                 st.session_state['final_state']['errors'] = st.session_state['final_state'].get('errors', []) + [f"Unexpected error: {e}"]

        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    print(f"Cleaned up temporary file: {temp_file_path}")
                except OSError as e:
                    print(f"Error cleaning up temporary file {temp_file_path}: {e}")

# --- Display Results Section ---
if uploaded_file is not None and st.session_state['final_state'] is not None:
    final_state = st.session_state['final_state']
    st.markdown("---")
    st.subheader("3. Extraction Results")
    st.markdown(f"**Final Pipeline Step:** `{final_state.get('current_state', 'Unknown')}`")

    if final_state.get('input_data'):
        st.markdown("#### Raw Input Data:")
        st.text_area("Raw Input Data", final_state['input_data'], height=150, key="raw_output_display")
    
    if final_state.get('preprocessed_text'):
        st.markdown("#### Preprocessed Text (sent to LLM):")
        st.text_area("Preprocessed Text", final_state['preprocessed_text'], height=150, key="cleaned_output_display")


    personal_profile = final_state.get('extracted_info')
    if personal_profile and isinstance(personal_profile, PersonalProfile):
        st.markdown("#### ✅ Extracted Personal Profile:")
        st.json(personal_profile.model_dump())
        
        st.write("---")
        st.markdown("##### Detailed Profile Fields:")
        
        display_rows = []
        field_order = [
            "name", "age", "location", "education", "work_experience", "interests",
            "personality_traits", "skills", "languages_spoken", "achievements",
            "contact_info"
        ]

        for field_name in field_order:
            field_obj = getattr(personal_profile, field_name, None)
            
            value = "N/A"
            sentiment = "N/A"
            confidence = "N/A"

            if field_obj is None:
                pass 
            elif isinstance(field_obj, str):
                value = field_obj if field_obj is not None else "N/A"
            elif isinstance(field_obj, int):
                value = str(field_obj) if field_obj is not None else "N/A"
            elif isinstance(field_obj, list):
                value = "; ".join(field_obj) if field_obj else "N/A"
            elif isinstance(field_obj, (LabeledString, LabeledInt)):
                value = field_obj.value if field_obj.value is not None else "N/A"
                sentiment = field_obj.sentiment if field_obj.sentiment is not None else "N/A"
                confidence = f"{field_obj.confidence:.0%}" if field_obj.confidence is not None else "N/A"
            elif isinstance(field_obj, LabeledList):
                value = "; ".join(field_obj.values) if field_obj.values else "N/A"
                sentiment = field_obj.sentiment if field_obj.sentiment is not None else "N/A"
                confidence = f"{field_obj.confidence:.0%}" if field_obj.confidence is not None else "N/A"
            
            if field_name in ["name", "age", "location", "contact_info"]: 
                display_rows.append({
                    "Field": field_name.replace('_', ' ').title(),
                    "Value": value
                })
            else:
                display_rows.append({
                    "Field": field_name.replace('_', ' ').title(),
                    "Value": value,
                    "Sentiment": sentiment,
                    "Confidence": confidence
                })
        
        df_columns = ["Field", "Value"]
        if any(row.get("Sentiment") != "N/A" for row in display_rows):
            df_columns.extend(["Sentiment", "Confidence"])
            
        processed_display_rows = []
        for row in display_rows:
            new_row = {}
            for col in df_columns:
                new_row[col] = row.get(col, "N/A")
            processed_display_rows.append(new_row)

        df = pd.DataFrame(processed_display_rows, columns=df_columns)
        st.dataframe(df, hide_index=True, use_container_width=True)

        if final_state.get('current_state') == "vector_db_complete":
            st.success("Profile successfully embedded and stored in vector database.")

    elif final_state.get('current_state') != "validation_failed_and_ended" and not final_state.get('errors'):
        st.warning("No personal profile could be extracted. This might be due to a lack of relevant information in the dialogue or a subtle processing issue.")
    
    validation_errors = final_state.get('validation_errors')
    if validation_errors:
        st.markdown("#### 🚨 Validation Errors:")
        for error in validation_errors:
            st.error(error)
        st.warning("Please review the input or prompt if validation errors persist.")
    
    general_errors = final_state.get('errors')
    if general_errors:
        st.markdown("#### 🚫 General Processing Errors:")
        for error in general_errors:
            st.exception(error)
        st.error("An error occurred during pipeline execution. Please check the logs.")

st.markdown("---")
st.caption("Powered by OpenAI GPT-4o, LangChain, LangGraph, and Streamlit.")