from pydantic import BaseModel, Field
from typing import List, Optional, Union 

# --- Schema Definitions ---

class EducationEntry(BaseModel):
    degree: Optional[str] = Field(None, description="Degree obtained (e.g., 'Bachelor of Science', 'PhD', 'High School Diploma').")
    major: Optional[str] = Field(None, description="Major or field of study (e.g., 'Computer Science', 'Psychology').")
    institution: Optional[str] = Field(None, description="Name of the educational institution (e.g., 'University of XYZ', 'Online Course Platform').")
    start_date: Optional[str] = Field(None, description="Start date of education (e.g., 'YYYY-MM', 'YYYY').")
    end_date: Optional[str] = Field(None, description="End date of education (e.g., 'YYYY-MM', 'YYYY', 'Present').")
    details: Optional[str] = Field(None, description="Any additional relevant details about the education (e.g., honors, thesis title, relevant coursework).")

class WorkExperienceEntry(BaseModel):
    title: Optional[str] = Field(None, description="Job title held (e.g., 'Software Engineer', 'Project Manager').")
    company: Optional[str] = Field(None, description="Name of the company or organization.")
    location: Optional[str] = Field(None, description="Location of the work (city, country).")
    start_date: Optional[Union[str, int]] = Field(None, description="Start date of the role (e.g., 'YYYY-MM', 'YYYY').")
    end_date: Optional[Union[str, int]] = Field(None, description="End date of the role (e.g., 'YYYY-MM', 'YYYY', 'Present').")
    responsibilities: List[str] = Field(default_factory=list, description="Key responsibilities and duties in this role. List format.")
    achievements_in_role: List[str] = Field(default_factory=list, description="Specific achievements or quantifiable impacts in this role. List format.")
    projects_involved: List[str] = Field(default_factory=list, description="List of key projects worked on within this role, summarized (e.g., 'Led development of new payment system').")

class ProjectEntry(BaseModel):
    name: Optional[str] = Field(None, description="Name of the personal project or initiative.")
    description: Optional[str] = Field(None, description="Brief description of the project and its significance/purpose.")
    technologies_used: List[str] = Field(default_factory=list, description="List of technologies, tools, or languages used in the project.")
    link: Optional[str] = Field(None, description="Link to the project (e.g., GitHub, portfolio, live demo).")

class PublicationEntry(BaseModel):
    title: Optional[str] = Field(None, description="Title of the publication or research work.")
    journal_or_conference: Optional[str] = Field(None, description="Journal, conference, or platform where the work was published.")
    publication_date: Optional[str] = Field(None, description="Date of publication (e.g., 'YYYY-MM', 'YYYY').")
    authors: List[str] = Field(default_factory=list, description="List of authors, if applicable.")
    abstract_summary: Optional[str] = Field(None, description="Brief summary or abstract of the publication/research.")
    link: Optional[str] = Field(None, description="Link to the publication (e.g., DOI, arXiv, publisher link).")

class SkillEntry(BaseModel):
    name: Optional[str] = Field(None, description="Name of the skill or core competency (e.g., 'Python', 'Leadership').")
    proficiency: Optional[str] = Field(None, description="Proficiency level (e.g., 'Beginner', 'Intermediate', 'Advanced', 'Expert').")
    category: Optional[str] = Field(None, description="Category of the skill (e.g., 'Programming Language', 'Soft Skill', 'Framework', 'Tool').")

class CertificationEntry(BaseModel):
    name: Optional[str] = Field(None, description="Name of the certification or professional qualification.")
    issuing_organization: Optional[str] = Field(None, description="Organization that issued the certification.")
    date_obtained: Optional[str] = Field(None, description="Date the certification was obtained (e.g., 'YYYY-MM', 'YYYY').")
    link: Optional[str] = Field(None, description="Link to the certification credential, if available.")

class AchievementEntry(BaseModel):
    description: Optional[str] = Field(None, description="Detailed description of the achievement or award.")
    date: Optional[str] = Field(None, description="Date of the achievement or when the award was received (e.g., 'YYYY-MM', 'YYYY').")
    awarding_organization: Optional[str] = Field(None, description="Organization that recognized or awarded the achievement, if applicable.")
    type: Optional[str] = Field(None, description="Type of achievement (e.g., 'Award', 'Promotion', 'Key Project Success', 'Patent', 'Nobel Prize').")
    is_major_achievement: bool = Field(False, description="Set to True if this is a highly significant or prestigious achievement (e.g., Nobel Prize, major industry award, groundbreaking patent).")

class ChallengeEntry(BaseModel):
    description: Optional[str] = Field(None, description="Brief description of the past challenge or obstacle faced.")
    how_overcome: Optional[str] = Field(None, description="Explanation of how the challenge was addressed and overcome.")
    lessons_learned: List[str] = Field(default_factory=list, description="Key lessons learned from the challenge.")

class StrengthEntry(BaseModel):
    description: Optional[str] = Field(None, description="Brief description of the personal strength or quality.")
    examples: List[str] = Field(default_factory=list, description="Specific examples or scenarios demonstrating this strength.")

class WeaknessEntry(BaseModel):
    description: Optional[str] = Field(None, description="Brief description of the personal weakness or area for improvement.")
    steps_to_address: List[str] = Field(default_factory=list, description="Steps being taken to address or mitigate this weakness.")

class GoalEntry(BaseModel):
    description: Optional[str] = Field(None, description="Brief description of the personal or professional goal.")
    timeframe: Optional[str] = Field(None, description="Expected timeframe for achieving the goal (e.g., 'short-term', 'long-term', 'next 2 years').")
    relevance: Optional[str] = Field(None, description="Why this goal is important to the individual.")

class MotivationEntry(BaseModel):
    description: Optional[str] = Field(None, description="Brief description of what motivates the person.")
    source: Optional[str] = Field(None, description="Source or origin of this motivation (e.g., 'passion for impact', 'intellectual curiosity').")

class ValueEntry(BaseModel):
    name: Optional[str] = Field(None, description="Name of the core value (e.g., 'Integrity', 'Collaboration').")
    significance: Optional[str] = Field(None, description="Explanation of why this value is important to the person.")

class ContactInfoEntry(BaseModel):
    type: Optional[str] = Field(None, description="Type of contact information (e.g., 'email', 'phone', 'LinkedIn URL', 'website').")
    value: Optional[str] = Field(None, description="The contact detail itself.")

class WorkPreferences(BaseModel):
    team_vs_individual: Optional[str] = Field(None, description="Preference for working in a team or individually (e.g., 'Prefers team environment', 'Prefers individual work with collaborative aspects').")
    remote_vs_onsite: Optional[str] = Field(None, description="Preference for remote work, onsite work, or hybrid (e.g., 'Strongly prefers remote', 'Open to hybrid').")
    preferred_industry: Optional[str] = Field(None, description="Preferred industry or sector for work (e.g., 'Fintech', 'Renewable Energy', 'Healthcare IT').")
    ideal_role: Optional[str] = Field(None, description="Ideal job role or position the person aspires to, including preferred responsibilities or scope.")
    company_size_preference: Optional[str] = Field(None, description="Preferred size of company (e.g., 'startup', 'mid-sized', 'large enterprise').")
    work_life_balance_importance: Optional[str] = Field(None, description="Importance of work-life balance (e.g., 'Very important', 'Flexible').")
    learning_growth_opportunities: Optional[str] = Field(None, description="Preference for learning and growth opportunities in a role (e.g., 'High importance on continuous learning').")

class SocialEngagement(BaseModel):
    volunteering_experience: List[str] = Field(default_factory=list, description="List of volunteering experiences of the person being interviewed. Each entry should describe the experience (e.g., 'Taught coding to underprivileged youth at Code Club, 2022').")
    community_involvement: List[str] = Field(default_factory=list, description="List of community involvement activities of the person being interviewed. Each entry should describe the activity (e.g., 'Organized local charity run for cancer research, 2023').")


# --- Main PersonalProfile Model ---

class PersonalProfile(BaseModel):
    name: Optional[str] = Field(None, description="Full name of the person being interviewed.")
    age: Optional[int] = Field(None, description="Age of the person being interviewed. Extract as an integer.")
    location: Optional[str] = Field(None, description="Current primary location of the person being interviewed, including city and country (if possible), e.g., 'Singapore, Singapore'.")
    gender: Optional[str] = Field(None, description="Gender of the person being interviewed (e.g., 'Male', 'Female', 'Non-binary'). Infer from context only if highly confident, otherwise null.")
    nationality: Optional[str] = Field(None, description="Nationality of the person being interviewed (e.g., 'Singaporean', 'American').")
    ethnicity: Optional[str] = Field(None, description="Ethnicity of the person being interviewed (e.g., 'Asian', 'Caucasian', 'Hispanic'). Infer from context only if highly confident, otherwise null.")
    marital_status: Optional[str] = Field(None, description="Marital status of the person being interviewed (e.g., 'Single', 'Married', 'Divorced', 'Widowed').")
    visa_or_work_permit_status: Optional[str] = Field(None, description="Visa or work permit status of the person being interviewed. This should include details about their legal right to work in a specific location, if applicable (e.g., 'H-1B visa holder', 'Permanent resident', 'Citizen').")

    education: List[EducationEntry] = Field(default_factory=list, description="List of educational backgrounds. Each entry includes degree, major, institution, dates, and details.")
    work_experience: List[WorkExperienceEntry] = Field(default_factory=list, description="List of professional work experiences. Each entry includes job title, company, dates, responsibilities, achievements, and projects within that role.")
    personal_projects: List[ProjectEntry] = Field(default_factory=list, description="List of personal projects undertaken, including name, description, technologies, and links.")
    publications_or_research: List[PublicationEntry] = Field(default_factory=list, description="List of publications or research work, including title, publication details, and links.")
    certifications: List[CertificationEntry] = Field(default_factory=list, description="List of certifications or professional qualifications, including name, issuing organization, date obtained, and links.")
    achievements: List[AchievementEntry] = Field(default_factory=list, description="List of notable achievements or awards, including description, date, awarding body, and type.")
    past_challenges: List[ChallengeEntry] = Field(default_factory=list, description="List of past challenges faced, including description, how it was overcome, and lessons learned.")
    strengths: List[StrengthEntry] = Field(default_factory=list, description="List of personal strengths, including description and specific examples.")
    weaknesses: List[WeaknessEntry] = Field(default_factory=list, description="List of personal weaknesses, including description and steps being taken to address them.")
    goals: List[GoalEntry] = Field(default_factory=list, description="List of personal or professional goals, including description, timeframe, and relevance.")
    motivations: List[MotivationEntry] = Field(default_factory=list, description="List of driving motivations, including description and source.")
    values: List[ValueEntry] = Field(default_factory=list, description="List of core values, including name and significance.")
    contact_info: List[ContactInfoEntry] = Field(default_factory=list, description="Contact information, such as email, phone, or LinkedIn URL, provided as type-value pairs.")

    interests: List[str] = Field(default_factory=list, description="List of interests or hobbies of the person being interviewed (e.g., 'Hiking', 'Reading science fiction').")
    skills: List[SkillEntry] = Field(default_factory=list, description="List of skills/core competencies, including name, proficiency level, and category.")
    tools_or_technologies_used: List[str] = Field(default_factory=list, description="List of tools or technologies used (e.g., 'Jira', 'Docker', 'Google Cloud Platform').")
    languages_spoken: List[str] = Field(default_factory=list, description="List of languages spoken by the person being interviewed, including language name and proficiency level (e.g., 'English - Fluent', 'Mandarin - Conversational').")

    professional_background_summary: Optional[str] = Field(None, description="A brief, high-level summary of the individual's entire career path, including key expertise areas and overall professional journey. This is a narrative summary, distinct from the detailed 'work_experience' list.")
    current_occupation: Optional[str] = Field(None, description="Current occupation of the person being interviewed. This should include their job title and a brief description of their current role and responsibilities. Only one entry. If currently unemployed, state 'Unemployed'.")
    communication_style: Optional[str] = Field(None, description="General communication style (e.g., 'Direct and concise', 'Empathetic and collaborative', 'Formal and detailed').")
    preferred_learning_style: Optional[str] = Field(None, description="Preferred learning style (e.g., 'Visual learner', 'Hands-on practical learner', 'Prefers structured courses').")
    personality_traits: List[str] = Field(default_factory=list, description="List of personality traits inferred from their tone, content, and behaviors described (e.g., 'Analytical', 'Proactive', 'Empathetic').")
    work_preferences: Optional[WorkPreferences] = Field(None, description="Detailed work preferences of the person being interviewed.")
    social_engagement: Optional[SocialEngagement] = Field(None, description="Social engagement activities, including volunteering and community involvement.")
    dialogue_type: List[str] = Field(None, description="Type/context of the current interview dialogue (e.g., 'Technical Interview', 'Behavioral Interview', 'HR Screening', 'Executive Interview', 'Performance Review'). The LLM should classify the current input.")


# --- State Model ---

class State(BaseModel):
    input_type: Optional[str] = Field(None, description="Type of input data: 'audio', 'text', 'pdf', 'url'.")
    input_data: Optional[str] = Field(None, description="Input data as a string, either audio file path or text content.")
    input_path: Optional[str] = Field(None, description="Path to the input file or URL.")
    preprocessed_text: Optional[str] = Field(None, description="Preprocessed text extracted from the input data.")
    extracted_info: Optional[PersonalProfile] = Field(None, description="Extracted personal profile information.")
    validation_errors: List[str] = Field(default_factory=list, description="List of validation errors found during processing.")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered during processing.")
    current_state: str = Field(default="initial", description="Current state of the processing pipeline.")
    target_profile_id: Optional[str] = Field(None, description="Target profile ID for vector database operations.")