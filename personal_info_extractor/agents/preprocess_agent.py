from typing import Dict
from schema.personal_profile import State
from openai import OpenAI
import re
import os

def preprocess(state: State) -> Dict[str, any]:

    # Check input path
    if not os.path.exists(state.input_path):
        state.errors.append(f"Input file not found: {state.input_path}")
        raise FileNotFoundError(f"Input file not found: {state.input_path}")
    
    # Read input data based on type
    if state.input_type == "audio":
        client = OpenAI()

        try:
            with open(state.input_path, "rb") as file:
                text = client.audio.transcriptions.create(
                    file=file,
                    model="whisper-1",
                    response_format="text"
                )
                
        except Exception as e:
            state.errors.append(f"Error transcribing audio: {e}")
            raise RuntimeError(f"Error transcribing audio: {e}")
    
    elif state.input_type == "text":
        with open(state.input_path, "r") as file:
            text = file.read()

    # Basic preprocessing
    preprocessed_text = remove_timestamps(text)
    preprocessed_text = remove_noise_annotations(preprocessed_text)
    preprocessed_text = remove_interviewer_dialogue(preprocessed_text)
    preprocessed_text = normalize_whitespace(preprocessed_text)

    return {
        "input_data": text,
        "preprocessed_text": preprocessed_text,
        "current_state": "preprocessing_complete",
        "errors": state.errors,
    }

def remove_timestamps(text: str) -> str:
    text = re.sub(r'\[\s*\d+m\d+s\d+ms\s*-\s*\d+m\d+s\d+ms\s*\]', '', text)
    text = re.sub(r'\(\d{2}:\d{2}\)|\s*\[\d+:\d+\]', '', text)
    return text

def remove_noise_annotations(text: str) -> str:
    text = re.sub(r'\[[^\]]*?\]', '', text)
    text = re.sub(r'\([^)]*\)', '', text)
    return text

def remove_interviewer_dialogue(text:str, interviewer_labels=["Interviewer:", "Q:", "Speaker 1:"]) -> str:
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        line_stripped = line.strip()
        is_interviewer = False

        for label in interviewer_labels:
            if line_stripped.lower().startswith(label.lower()):
                is_interviewer = True
                cleaned_lines.append(re.sub(r'^{}'.format(re.escape(label)), '', line_stripped, flags=re.IGNORECASE).strip())
                break

        if not is_interviewer:
            line = re.sub(r'^(candidate|speaker \d+):', '', line_stripped, flags=re.IGNORECASE).strip()
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)

def normalize_whitespace(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    text = '\n'.join([line.strip() for line in text.strip().split('\n')])
    return text