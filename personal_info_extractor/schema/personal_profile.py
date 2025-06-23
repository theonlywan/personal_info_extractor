from pydantic import BaseModel, Field
from typing import List, Optional

class PersonalProfile(BaseModel):
    name: Optional[str] = Field(None, description="Full name of the interviewee.")
    age: Optional[int] = Field(None, description="Age of the interviewee.")
    location: Optional[str] = Field(None, description="Location of the interviewee, including city and country (if possible).")
    education: Optional[str] = Field(None, description="Field of education of the interviewee and where they received it. This should be in the format 'Psychology, University of XYZ'.")
    interests: Optional[List[str]] = Field(None, description="List of interests or hobbies of the interviewee.")
    personality_traits: Optional[List[str]] = Field(None, description="List of personality traits inferred from the interviewee's tone or content.")

class State(BaseModel):
    input_type: Optional[str] = Field(None, description="Type of input data: 'audio' or 'text'.")
    input_data: Optional[str] = Field(None, description="Input data as a string, either audio file path or text.")
    input_path: Optional[str] = Field(None, description="Path to the input file.")
    preprocessed_text: Optional[str] = Field(None, description="Preprocessed text extracted from the input data.")
    extracted_info: Optional[PersonalProfile] = Field(None, description="Extracted personal profile information.")
    validation_errors: List[str] = Field(default_factory=list, description="List of validation errors found during processing.")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered during processing.")
    current_state: str = Field(default="initial", description="Current state of the processing pipeline.")