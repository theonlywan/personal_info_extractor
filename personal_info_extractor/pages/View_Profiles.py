import streamlit as st
from typing import List, Any

# Import all necessary schema components, including nested models
from schema.personal_profile import (
    PersonalProfile,
    EducationEntry, WorkExperienceEntry, ProjectEntry, PublicationEntry,
    SkillEntry, CertificationEntry, AchievementEntry, ChallengeEntry,
    StrengthEntry, WeaknessEntry, GoalEntry, MotivationEntry, ValueEntry,
    ContactInfoEntry, WorkPreferences, SocialEngagement
)
from utils.chroma_utils import get_all_profiles_from_chroma

st.set_page_config(page_title="View Stored Profiles", layout="wide")

st.title("💾 Stored Personal Profiles")
st.markdown("View all extracted and stored personal profiles in a neat and organized format. You can also find the profiles in their respective raw JSON formats for easy export.")

# --- Load and Display Profiles ---
@st.cache_data(ttl=5)
def load_profiles() -> List[PersonalProfile]:
    """Loads all PersonalProfile objects from ChromaDB."""
    return get_all_profiles_from_chroma()

all_profiles = load_profiles()

if not all_profiles:
    st.info("No profiles found in the database yet. Extract some profiles on the main page!")
else:
    st.success(f"Found {len(all_profiles)} profile(s) in the database.")

    # --- Display Each Profile ---
    for i, profile in enumerate(all_profiles):
        st.markdown(f"---")
        profile_name = profile.name if profile.name else 'Unnamed Profile'
        st.subheader(f"Profile {i+1}: {profile_name}")
        
        with st.expander("View Raw JSON"):
            st.json(profile.model_dump(exclude_none=True))

        st.markdown("## 📊 Detailed Profile Overview")

        def render_list_of_models(title: str, items: List[Any], key_field: str = None):
            if items:
                with st.expander(f"📚 {title} ({len(items)} entries)"):
                    for idx, item in enumerate(items):
                        st.markdown(f"**Entry {idx+1}:**")
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
                        elif isinstance(item, str):
                            st.markdown(f"- {item}")
                        else:
                            st.json(item.model_dump(exclude_none=True))
            else:
                st.markdown(f"*{title}*: N/A")


        # --- General Information ---
        st.subheader("General Information")
        col1, col2 = st.columns(2)
        col1.write(f"**Name:** {profile.name if profile.name else 'N/A'}")
        col2.write(f"**Age:** {profile.age if profile.age else 'N/A'}")
        col1.write(f"**Location:** {profile.location if profile.location else 'N/A'}")
        col2.write(f"**Gender:** {profile.gender if profile.gender else 'N/A'}")
        col1.write(f"**Nationality:** {profile.nationality if profile.nationality else 'N/A'}")
        col2.write(f"**Ethnicity:** {profile.ethnicity if profile.ethnicity else 'N/A'}")
        col1.write(f"**Marital Status:** {profile.marital_status if profile.marital_status else 'N/A'}")
        col2.write(f"**Visa/Work Permit:** {profile.visa_or_work_permit_status if profile.visa_or_work_permit_status else 'N/A'}")
        st.write(f"**Current Occupation:** {profile.current_occupation if profile.current_occupation else 'N/A'}")
        st.write(f"**Professional Summary:** {profile.professional_background_summary if profile.professional_background_summary else 'N/A'}")
        st.write("**All Dialogue Types:** " + (", ".join([str(item) for item in profile.dialogue_type]) if profile.dialogue_type else "N/A"))

        # --- ACHIEVEMENTS (Special Handling for Notable) ---
        st.subheader("🏆 Achievements")
        if profile.achievements:
            notable_achievements = [ach for ach in profile.achievements if ach.is_major_achievement]
            regular_achievements = [ach for ach in profile.achievements if not ach.is_major_achievement]

            if notable_achievements:
                st.markdown("#### 🌟 Notable Achievements")
                for idx, ach in enumerate(notable_achievements):
                    st.markdown(f"**{idx+1}.** **{ach.description}**")
                    if ach.type: st.markdown(f"   - *Type:* {ach.type}")
                    if ach.awarding_organization: st.markdown(f"   - *Awarded By:* {ach.awarding_organization}")
                    if ach.date: st.markdown(f"   - *Date:* {ach.date}")
            else:
                st.markdown("No notable achievements found.")
            
            if regular_achievements:
                st.markdown("#### Other Achievements")
                for idx, ach in enumerate(regular_achievements):
                    st.markdown(f"**{idx+1}.** {ach.description}")
                    if ach.type: st.markdown(f"   - *Type:* {ach.type}")
                    if ach.awarding_organization: st.markdown(f"   - *Awarded By:* {ach.awarding_organization}")
                    if ach.date: st.markdown(f"   - *Date:* {ach.date}")
            else:
                st.markdown("No other achievements found.")
        else:
            st.markdown("No achievements found.")

        # --- Other Structured Lists ---
        render_list_of_models("Education", profile.education, "degree")
        render_list_of_models("Work Experience", profile.work_experience, "title")
        render_list_of_models("Personal Projects", profile.personal_projects, "name")
        render_list_of_models("Publications & Research", profile.publications_or_research, "title")
        render_list_of_models("Skills", profile.skills, "name")
        render_list_of_models("Certifications", profile.certifications, "name")
        render_list_of_models("Languages Spoken", profile.languages_spoken)
        render_list_of_models("Tools & Technologies Used", profile.tools_or_technologies_used)
        render_list_of_models("Past Challenges", profile.past_challenges, "description")
        render_list_of_models("Strengths", profile.strengths, "description")
        render_list_of_models("Weaknesses", profile.weaknesses, "description")
        render_list_of_models("Goals", profile.goals, "description")
        render_list_of_models("Motivations", profile.motivations, "description")
        render_list_of_models("Values", profile.values, "name")
        render_list_of_models("Interests", profile.interests)
        render_list_of_models("Contact Info", profile.contact_info, "type")


        # --- Nested Objects (Work Preferences, Social Engagement) ---
        st.subheader("💼 Work Preferences")
        if profile.work_preferences:
            prefs = profile.work_preferences
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
        if profile.social_engagement:
            social = profile.social_engagement
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
        st.markdown(f"**Personality Traits:** {'; '.join(profile.personality_traits) if profile.personality_traits else 'N/A'}")
        st.markdown(f"**Communication Style:** {profile.communication_style if profile.communication_style else 'N/A'}")
        st.markdown(f"**Preferred Learning Style:** {profile.preferred_learning_style if profile.preferred_learning_style else 'N/A'}")

# Footer
st.markdown("---")
st.caption("Powered by Streamlit and ChromaDB.")