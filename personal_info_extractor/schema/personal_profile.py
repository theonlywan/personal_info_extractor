from pydantic import BaseModel, Field
from typing import List, Optional

class LabeledString(BaseModel):
    value: Optional[str]
    sentiment: Optional[str] = None
    confidence: Optional[float] = None

class LabeledInt(BaseModel):
    value: Optional[int]
    sentiment: Optional[str] = None
    confidence: Optional[float] = None

class LabeledList(BaseModel):
    values: Optional[List[str]]
    sentiment: Optional[str] = None
    confidence: Optional[float] = None

class PersonalProfile(BaseModel):
    name: Optional[str] = Field(None, description="Name of the person being interviewed.")
    age: Optional[int] = Field(None, description="Age of the person being interviewed.")
    location: Optional[str] = Field(None, description="Location of the person being interviewed, including city and country (if possible).")
    education: Optional[LabeledString] = Field(None, description="Field of education of the person being interviewed and where they received it and its associated sentiment/confidence. If it is professional, it should be in the format 'Psychology, University of XYZ'. If it is non-professional, it should include the mode of learning and be in the format 'Psychology, Online Course'.")
    work_experience: Optional[LabeledList] = Field(None, description="List of work experiences of the person being interviewed and their associated sentiment/confidence. Each entry should include the job title, company, and duration.")
    interests: Optional[LabeledList] = Field(None, description="List of interests or hobbies of the person being interviewed and their associated sentiment/confidence.")
    personality_traits: List[str] = Field(None, description="List of personality traits of the person being interviewed to be inferred from their tone and content.")
    skills: Optional[LabeledList] = Field(None, description="List of skills/core competencies of the person being interviewed and their associated sentiment/confidence. Each entry should include the skill name and proficiency level (e.g., 'Python - Advanced').")
    languages_spoken: Optional[LabeledList] = Field(None, description="List of languages spoken by the person being interviewed and their associated sentiment/confidence. Each entry should include the language name and proficiency level (e.g., 'English - Fluent').")
    achievements: Optional[LabeledList] = Field(None, description="List of notable achievements or awards received by the person being interviewed and their associated sentiment/confidence. Each entry should include the achievement name, date and organisation that awarded the achievement (if applicable).")
    contact_info: List[str] = Field(None, description="Contact information of the person being interviewed, such as email or phone number. This should be provided only if explicitly mentioned in the interview.")

class State(BaseModel):
    input_type: Optional[str] = Field(None, description="Type of input data: 'audio' or 'text'.")
    input_data: Optional[str] = Field(None, description="Input data as a string, either audio file path or text.")
    input_path: Optional[str] = Field(None, description="Path to the input file.")
    preprocessed_text: Optional[str] = Field(None, description="Preprocessed text extracted from the input data.")
    extracted_info: Optional[PersonalProfile] = Field(None, description="Extracted personal profile information.")
    validation_errors: List[str] = Field(default_factory=list, description="List of validation errors found during processing.")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered during processing.")
    current_state: str = Field(default="initial", description="Current state of the processing pipeline.")