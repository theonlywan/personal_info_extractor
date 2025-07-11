import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
import re
import json
from typing import List, Union
from pydantic import BaseModel

# Ensure the environment variables are loaded
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY environment variable not set. Please set it in your .env file or system environment.")
    st.stop()

# Import the app and schema components
try:
    from app import app
    from schema.personal_profile import (
        State, PersonalProfile,
        EducationEntry, WorkExperienceEntry, ProjectEntry, PublicationEntry,
        SkillEntry, CertificationEntry, AchievementEntry, ChallengeEntry,
        StrengthEntry, WeaknessEntry, GoalEntry, MotivationEntry, ValueEntry,
        ContactInfoEntry, WorkPreferences, SocialEngagement 
    )
    from utils.chroma_utils import get_all_profiles_from_chroma, get_chroma_collection
except ImportError as e:
    st.error(f"Failed to import backend components. Ensure 'app.py' and 'schema/personal_profile.py' are correctly defined and in your PYTHONPATH. Error: {e}")
    st.stop()

st.set_page_config(page_title="Personal Data Extractor", layout="centered")

st.title("🗣️ Personal Data & Preferences Extractor")
st.write("This tool uses advanced AI models to analyze conversations and extract structured personal profiles. It can handle audio files, text transcripts, and URLs to relevant pages (e.g., Wikipedia, YouTube). It extracts information such as name, age, location, education, work experience, skills, and more. The extracted data is stored in a structured format for easy access and analysis. Navigate to the 'View Profiles' tab to take a look at all the profiles that are stored and organized.")
st.markdown("---")

# --- File Uploader Section ---
uploaded_file = None
input_url = None
st.session_state.setdefault('processing_status', None)
st.session_state.setdefault('final_state', None)

st.subheader("📂 Upload Input Data")
st.markdown("Upload an audio file (e.g., .mp3, .wav, .m4a) or a text transcript (e.g., .txt, .pdf). Alternatively, you can provide a URL to a relevant page (e.g., Wikipedia, YouTube).")

uploaded_file = st.file_uploader(
    "Choose an audio file (.mp3, .wav, .m4a) or a text transcript (.txt, .pdf):",
    type=["mp3", "wav", "m4a", "txt", "pdf"],
    label_visibility="collapsed",
)

st.markdown("--- OR ---")
input_url = st.text_input("Enter a URL", key="url_input")

if uploaded_file is not None or input_url:
    file_extension = uploaded_file.name.split('.')[-1].lower() if uploaded_file else None

    if file_extension in ["mp3", "wav", "m4a"]:
        input_type = "audio"
    elif file_extension == "txt":
        input_type = "text"
    elif file_extension == "pdf":
        input_type = "pdf"
    elif input_url:
        if re.match(r"https?://\S+", input_url):
            input_type = 'url'
        else:
            st.error("Please enter a valid URL (starting with http:// or https://).")
            st.stop()
    else:
        st.error(f"Unsupported file type: .{file_extension}. Please upload an audio file (.mp3, .wav, .m4a) or a text transcript (.txt, .pdf).")
        st.session_state['processing_status'] = "Unsupported file type."
        st.session_state['final_state'] = None
        st.stop()

    temp_file_path = None
    
    with st.spinner("Saving uploaded file temporarily..."):
        try:
            if uploaded_file:
                temp_dir = tempfile.gettempdir()
                temp_file_path = os.path.join(temp_dir, f"uploaded_file_{os.urandom(8).hex()}.{file_extension}")
                
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                st.session_state['processing_status'] = f"File saved temporarily at: {temp_file_path}"
                st.success(f"{input_type} file uploaded and saved successfully.")

            elif input_url:
                temp_file_path = input_url
                st.session_state['processing_status'] = f"Input URL set: {temp_file_path}"
                st.success("Input URL set successfully.")

        except Exception as e:
            st.error(f"Failed to save uploaded file: {e}")
            st.session_state['processing_status'] = f"Error saving file: {e}"
            st.session_state['final_state'] = None
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            st.stop()

# --- New Profile or Update Existing Section ---
if st.session_state.get('processing_status') is not None:
    target_profile_id = None
    st.markdown("---")
    st.subheader("👤 Profile Selection")
    st.markdown("Select an existing profile to update or create a new one. If you choose to update, the existing profile will be modified with the new data extracted from the dialogue.")

    # Load existing profiles for the dropdown
    @st.cache_data(ttl=5)
    def get_cached_profiles():
        profiles = get_all_profiles_from_chroma()
        
        profile_options = [
            (f"{p.name if p.name else 'Unnamed Profile'} (ID: {idx})", f"{p.name if p.name else 'Unnamed Profile'} - {idx}")
            for idx, p in enumerate(profiles) 
        ]
        
        st.session_state['existing_profiles_for_update'] = profiles
        return ["Create New Profile"] + [option[0] for option in profile_options]

    existing_profiles = get_cached_profiles()
    selected_option = st.selectbox(
        "Select an existing profile to update or create a new one:",
        options=existing_profiles,
        index=0,
        key="profile_selection",
        label_visibility="collapsed"
    )

    if selected_option == "Create New Profile":
        st.session_state['selected_profile'] = None
        st.success("You have chosen to create a new profile.")
        target_profile_id = None
        st.session_state['processing_status'] = "Creating a new profile. Please upload your data."

    else:
        st.session_state['selected_profile'] = selected_option
        st.session_state['processing_status'] = f"Selected profile for update: {selected_option}"

        match = re.search(r'\(ID: (\d+)\)', selected_option)
        if match:
            original_index = int(match.group(1))
            
            if original_index < len(st.session_state['existing_profiles_for_update']):
                selected_profile_obj = st.session_state['existing_profiles_for_update'][original_index]
                
                collection = get_chroma_collection()
                if collection:
                    all_chroma_docs = collection.get(ids=None, include=['metadatas'])
                    for idx, meta in enumerate(all_chroma_docs['metadatas']):
                        try:
                            stored_profile_dict = json.loads(meta['profile_data'])
                            if stored_profile_dict.get('name') == selected_profile_obj.name and \
                                stored_profile_dict.get('location') == selected_profile_obj.location:
                                target_profile_id = all_chroma_docs['ids'][idx]
                                break
                        except Exception:
                            pass
                
                if target_profile_id:
                    st.info(f"Selected profile for update: **{selected_profile_obj.name if selected_profile_obj.name else 'Unnamed'}**")
                else:
                    st.warning("Could not find matching ChromaDB ID for selected profile. A new profile will be created.")
            else:
                st.warning("Selected profile not found in cache. A new profile will be created.")

# --- Extraction Section ---
if (uploaded_file is not None and temp_file_path) or (input_url and temp_file_path):
    st.markdown("---")
    st.subheader("🛠️ Extraction")
    st.markdown("Click 'Extract Data' to begin the extraction process. The final pipeline step, raw text and preprocessed text for extraction are provided as well.")

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
            target_profile_id=target_profile_id
        )

        current_accumulated_dict_state = initial_state.model_dump()
        
        try:
            status_text.text("Running LangGraph pipeline (Preprocessing, Extraction, Validation, Storage)...")
            progress_bar.progress(10)

            for s in app.stream(initial_state):
                if s:
                    current_node_name = list(s.keys())[0]
                    node_output = s[current_node_name]
                    
                    for k, v in node_output.items():
                        if isinstance(v, dict) and k in current_accumulated_dict_state and \
                        isinstance(current_accumulated_dict_state[k], dict):
                            current_accumulated_dict_state[k].update(v)
                        else:
                            current_accumulated_dict_state[k] = v

                    status_text.text(f"{current_node_name.replace('_', ' ').title()}...")
                    
                    if current_node_name == "preprocess":
                        progress_bar.progress(25)
                    elif current_node_name == "extract":
                        progress_bar.progress(50)
                    elif current_node_name == "validate":
                        progress_bar.progress(75)
                    elif current_node_name == "vector_db":
                        progress_bar.progress(90)
                else:
                    status_text.text("Processing...")
                    progress_bar.progress(min(99, progress_bar.value + 5))

            # Final state should be a Pydantic object
            st.session_state['final_state'] = State.model_validate(current_accumulated_dict_state)
            
            progress_bar.progress(100)
            status_text.text("LangGraph pipeline completed!")
            st.session_state['processing_status'] = "Extraction complete."

        except Exception as e:
            st.error(f"An unexpected error occurred during pipeline execution: {e}")
            st.session_state['processing_status'] = f"Pipeline failed: {e}"
            current_accumulated_dict_state['errors'] = current_accumulated_dict_state.get('errors', []) + [f"Unexpected error: {e}"]
            current_accumulated_dict_state['current_state'] = "pipeline_error"

            try:
                st.session_state['final_state'] = State.model_validate(current_accumulated_dict_state)
            except Exception as validation_e:
                st.error(f"Could not reconstruct final state for display due to validation error after pipeline error: {validation_e}. Raw state dict: {current_accumulated_dict_state}")
                st.session_state['final_state'] = current_accumulated_dict_state

        finally:
            if temp_file_path and os.path.exists(temp_file_path) and not input_url:
                try:
                    os.remove(temp_file_path)
                    print(f"Cleaned up temporary file: {temp_file_path}")
                except OSError as e:
                    print(f"Error cleaning up temporary file {temp_file_path}: {e}")

if st.session_state['final_state'] is not None:
    final_state = st.session_state['final_state']
    personal_profile = None
    
    if isinstance(final_state, dict):
        try:
            final_state = State.model_validate(final_state)
        except Exception as e:
            st.error(f"Failed to validate final state for display: {e}. Displaying raw data.")
            st.json(final_state)
            st.stop()

    st.markdown(f"**Final Pipeline Step:** `{final_state.current_state}`")

    if final_state.input_data:
        with st.expander("View Raw Input Data"):
            st.markdown(f"<div style='font-size: 0.85em'>{final_state.input_data}</div>", unsafe_allow_html=True)

    if final_state.preprocessed_text:
        with st.expander("View Preprocessed Text"):
            st.markdown(f"<div style='font-size: 0.85em'>{final_state.preprocessed_text}</div>", unsafe_allow_html=True)

    if final_state.target_profile_id:
        collection = get_chroma_collection()
        results = collection.get(ids=[final_state.target_profile_id], include=['metadatas'])

        if results and results['metadatas'] and len(results['metadatas']) > 0:
            profile_json_string = results['metadatas'][0].get('profile_data')
            if profile_json_string:
                try:
                    personal_profile_dict = json.loads(profile_json_string)
                    personal_profile = PersonalProfile.model_validate(personal_profile_dict)
                    st.success(f"Profile successfully updated.")
                except Exception as e:
                    st.error(f"Error validating profile from DB: {e}. Displaying raw DB data.")
                    st.json(personal_profile_dict)
    
    if personal_profile is None:
        personal_profile = final_state.extracted_info
        st.success("New profile extracted successfully from the dialogue.")

# --- Display Results Section ---
    if personal_profile:
        st.write("---")
        st.subheader("📊 Detailed Profile Overview")
        st.markdown("Here is the structured profile extracted from the data input provided. Below you will find the data in a resume format organised by the respective fields as well as in a raw JSON format for easy export. If you wish to take a look at other profiles, please navigate to the 'View Profiles' tab.")
        with st.expander("View Raw JSON"):
            st.json(personal_profile.model_dump(exclude_none=True))

        # --- Basic Information ---
        st.subheader("General Information")
        col1, col2 = st.columns(2)
        col1.write(f"**Name:** {personal_profile.name if personal_profile.name else 'N/A'}")
        col2.write(f"**Age:** {personal_profile.age if personal_profile.age else 'N/A'}")
        col1.write(f"**Location:** {personal_profile.location if personal_profile.location else 'N/A'}")
        col2.write(f"**Gender:** {personal_profile.gender if personal_profile.gender else 'N/A'}")
        col1.write(f"**Nationality:** {personal_profile.nationality if personal_profile.nationality else 'N/A'}")
        col2.write(f"**Ethnicity:** {personal_profile.ethnicity if personal_profile.ethnicity else 'N/A'}")
        col1.write(f"**Marital Status:** {personal_profile.marital_status if personal_profile.marital_status else 'N/A'}")
        col2.write(f"**Visa/Work Permit:** {personal_profile.visa_or_work_permit_status if personal_profile.visa_or_work_permit_status else 'N/A'}")
        st.write(f"**Current Occupation:** {personal_profile.current_occupation if personal_profile.current_occupation else 'N/A'}")
        st.write(f"**Professional Summary:** {personal_profile.professional_background_summary if personal_profile.professional_background_summary else 'N/A'}")
        st.write(f"**Current Dialogue Type:** {personal_profile.dialogue_type[-1] if personal_profile.dialogue_type and personal_profile.dialogue_type[-1] else 'N/A'}")

        # --- Structured Lists (Education, Work Experience etc.) ---
        def render_list_of_models(title: str, items: List[BaseModel], key_field: str):
            if items:
                with st.expander(f"📚 {title} ({len(items)} entries)"):
                    for i, item in enumerate(items):
                        st.markdown(f"**Entry {i+1}:**")

                        if isinstance(item, EducationEntry):
                            st.markdown(f"- **Degree:** {item.degree} in {item.major} from {item.institution} ({item.start_date} - {item.end_date})")
                            if item.details: st.markdown(f"  - *Details:* {item.details}")
                        elif isinstance(item, WorkExperienceEntry):
                            st.markdown(f"- **Title:** {item.title} at {item.company} ({item.start_date} - {item.end_date})")
                            if item.location: st.markdown(f"  - *Location:* {item.location}")
                            if item.responsibilities: st.markdown(f"  - *Responsibilities:* {'; '.join(item.responsibilities)}")
                            if item.achievements_in_role: st.markdown(f"  - *Achievements in Role:* {'; '.join(item.achievements_in_role)}")
                            if item.projects_involved: st.markdown(f"  - *Projects:* {'; '.join(item.projects_involved)}")
                        elif isinstance(item, ProjectEntry):
                            st.markdown(f"- **Project Name:** {item.name}")
                            st.markdown(f"  - *Description:* {item.description}")
                            if item.technologies_used: st.markdown(f"  - *Tech Used:* {'; '.join(item.technologies_used)}")
                            if item.link: st.markdown(f"  - *Link:* {item.link}")
                        elif isinstance(item, PublicationEntry):
                            st.markdown(f"- **Title:** {item.title}")
                            st.markdown(f"  - *Published In:* {item.journal_or_conference} ({item.publication_date})")
                            if item.authors: st.markdown(f"  - *Authors:* {'; '.join(item.authors)}")
                            if item.abstract_summary: st.markdown(f"  - *Summary:* {item.abstract_summary}")
                            if item.link: st.markdown(f"  - *Link:* {item.link}")
                        elif isinstance(item, SkillEntry):
                            st.markdown(f"- **Skill:** {item.name} ({item.proficiency}) - *Category:* {item.category}")
                        elif isinstance(item, CertificationEntry):
                            st.markdown(f"- **Certification:** {item.name} from {item.issuing_organization} ({item.date_obtained})")
                            if item.link: st.markdown(f"  - *Link:* {item.link}")
                        elif isinstance(item, ChallengeEntry):
                            st.markdown(f"- **Challenge:** {item.description}")
                            if item.how_overcome: st.markdown(f"  - *Overcome By:* {item.how_overcome}")
                            if item.lessons_learned: st.markdown(f"  - *Lessons Learned:* {'; '.join(item.lessons_learned)}")
                        elif isinstance(item, StrengthEntry):
                            st.markdown(f"- **Strength:** {item.description}")
                            if item.examples: st.markdown(f"  - *Examples:* {'; '.join(item.examples)}")
                        elif isinstance(item, WeaknessEntry):
                            st.markdown(f"- **Weakness:** {item.description}")
                            if item.steps_to_address: st.markdown(f"  - *Addressing By:* {'; '.join(item.steps_to_address)}")
                        elif isinstance(item, GoalEntry):
                            st.markdown(f"- **Goal:** {item.description}")
                            if item.timeframe: st.markdown(f"  - *Timeframe:* {item.timeframe}")
                            if item.relevance: st.markdown(f"  - *Relevance:* {item.relevance}")
                        elif isinstance(item, MotivationEntry):
                            st.markdown(f"- **Motivation:** {item.description}")
                            if item.source: st.markdown(f"  - *Source:* {item.source}")
                        elif isinstance(item, ValueEntry):
                            st.markdown(f"- **Value:** {item.name}")
                            if item.significance: st.markdown(f"  - *Significance:* {item.significance}")
                        elif isinstance(item, ContactInfoEntry):
                            st.markdown(f"- **{item.type.title() if item.type else 'Contact'}:** {item.value}")
                        elif isinstance(item, List):
                            st.markdown(f"- **{item.name if hasattr(item, 'name') else 'Item'}:** {item.value if hasattr(item, 'value') else item}")
                        elif isinstance(item, str) or isinstance(item, int):
                            st.markdown(f"- {item}")
                        else:
                            st.json(item.model_dump())
            else:
                st.markdown(f"*{title}*: N/A")

        # --- ACHIEVEMENTS (Special Handling for Notable) ---
        st.subheader("🏆 Achievements")
        notable_achievements = [ach for ach in personal_profile.achievements if ach.is_major_achievement]
        regular_achievements = [ach for ach in personal_profile.achievements if not ach.is_major_achievement]

        if notable_achievements:
            st.markdown("#### 🌟 Notable Achievements")
            for i, ach in enumerate(notable_achievements):
                st.markdown(f"**{i+1}.** **{ach.description}**")
                if ach.type: st.markdown(f"   - *Type:* {ach.type}")
                if ach.awarding_organization: st.markdown(f"   - *Awarded By:* {ach.awarding_organization}")
                if ach.date: st.markdown(f"   - *Date:* {ach.date}")
        else:
            st.markdown("No notable achievements found.")
        
        if regular_achievements:
            st.markdown("#### Other Achievements")
            for i, ach in enumerate(regular_achievements):
                st.markdown(f"**{i+1}.** {ach.description}")
                if ach.type: st.markdown(f"   - *Type:* {ach.type}")
                if ach.awarding_organization: st.markdown(f"   - *Awarded By:* {ach.awarding_organization}")
                if ach.date: st.markdown(f"   - *Date:* {ach.date}")
        else:
            st.markdown("No other achievements found.")

        # --- Other Structured Lists ---
        st.subheader("📚 Attributes")
        render_list_of_models("Education", personal_profile.education, "degree")
        render_list_of_models("Work Experience", personal_profile.work_experience, "title")
        render_list_of_models("Personal Projects", personal_profile.personal_projects, "name")
        render_list_of_models("Publications & Research", personal_profile.publications_or_research, "title")
        render_list_of_models("Skills", personal_profile.skills, "name")
        render_list_of_models("Certifications", personal_profile.certifications, "name")
        render_list_of_models("Languages Spoken", personal_profile.languages_spoken, "name")
        render_list_of_models("Tools & Technologies Used", personal_profile.tools_or_technologies_used, "name")
        render_list_of_models("Past Challenges", personal_profile.past_challenges, "description")
        render_list_of_models("Strengths", personal_profile.strengths, "description")
        render_list_of_models("Weaknesses", personal_profile.weaknesses, "description")
        render_list_of_models("Goals", personal_profile.goals, "description")
        render_list_of_models("Motivations", personal_profile.motivations, "description")
        render_list_of_models("Values", personal_profile.values, "name")
        render_list_of_models("Interests", personal_profile.interests, "name")
        render_list_of_models("Contact Info", personal_profile.contact_info, "type")


        # --- Nested Objects (Work Preferences, Social Engagement) ---
        st.subheader("💼 Work Preferences")
        if personal_profile.work_preferences:
            prefs = personal_profile.work_preferences
            st.markdown(f"- **Team vs. Individual:** {prefs.team_vs_individual if prefs.team_vs_individual else 'N/A'}")
            st.markdown(f"- **Remote vs. Onsite:** {prefs.remote_vs_onsite if prefs.remote_vs_onsite else 'N/A'}")
            st.markdown(f"- **Preferred Industry:** {prefs.preferred_industry if prefs.preferred_industry else 'N/A'}")
            st.markdown(f"- **Ideal Role:** {prefs.ideal_role if prefs.ideal_role else 'N/A'}")
            st.markdown(f"- **Company Size Preference:** {prefs.company_size_preference if prefs.company_size_preference else 'N/A'}")
            st.markdown(f"- **Work-Life Balance Importance:** {prefs.work_life_balance_importance if prefs.work_life_balance_importance else 'N/A'}")
            st.markdown(f"- **Learning & Growth:** {prefs.learning_growth_opportunities if prefs.learning_growth_opportunities else 'N/A'}")
        else:
            st.markdown("Work preferences: N/A")

        st.subheader("🤝 Social Engagement")
        if personal_profile.social_engagement:
            social = personal_profile.social_engagement
            if social.volunteering_experience:
                st.markdown("**Volunteering Experience:**")
                for entry in social.volunteering_experience:
                    st.markdown(f"- {entry}")
            else:
                st.markdown("Volunteering Experience: N/A")
            
            if social.community_involvement:
                st.markdown("**Community Involvement:**")
                for entry in social.community_involvement:
                    st.markdown(f"- {entry}")
            else:
                st.markdown("Community Involvement: N/A")
        else:
            st.markdown("Social Engagement: N/A")

        st.subheader("🧠 Personality & Communication")
        st.markdown(f"**Personality Traits:** {'; '.join(personal_profile.personality_traits) if personal_profile.personality_traits else 'N/A'}")
        st.markdown(f"**Communication Style:** {personal_profile.communication_style if personal_profile.communication_style else 'N/A'}")
        st.markdown(f"**Preferred Learning Style:** {personal_profile.preferred_learning_style if personal_profile.preferred_learning_style else 'N/A'}")


    elif final_state.current_state != "validation_failed_and_ended" and not final_state.errors:
        st.warning("No personal profile could be extracted. This might be due to a lack of relevant information in the dialogue or a subtle processing issue.")
    
    validation_errors = final_state.validation_errors
    if validation_errors:
        st.markdown("#### 🚨 Validation Errors:")
        for error in validation_errors:
            st.error(error)
        st.warning("Please review the input or prompt if validation errors persist.")
    
    general_errors = final_state.errors
    if general_errors:
        st.markdown("#### 🚫 General Processing Errors:")
        for error in general_errors:
            st.exception(error)
        st.error("An error occurred during pipeline execution. Please check the logs.")

st.markdown("---")
st.caption("Powered by OpenAI GPT-4o, LangChain, LangGraph, and Streamlit.")