from typing import Dict, Any, Optional, List, Tuple
from schema.personal_profile import State
from openai import OpenAI
import re
import os
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
import yt_dlp
import tempfile
from pydub import AudioSegment
from pydub.utils import mediainfo

def preprocess(state: State) -> Dict[str, Any]:

    temp_files = []
    text = ""
    current_validation_errors = state.validation_errors
    current_errors = state.errors
    MAX_LLM_INPUT_SIZE_BYTES = 25 * 1024 * 1024
    MAX_WHISPER_AUDIO_SIZE_BYTES = 25 * 1024 * 1024
    MAX_CHUNK_DURATION_SECONDS = 15 * 60

    # Check input path
    if state.input_type in ["audio", "text", "pdf"] and not os.path.exists(state.input_path):
        state.errors.append(f"Input path/link not found: {state.input_path}")
        raise FileNotFoundError(f"Input path/link not found: {state.input_path}")
    
    # Read input data based on type
    try:
        if state.input_type == "audio":
            text, audio_cleanup_files = process_audio_for_transcription(state.input_path, MAX_WHISPER_AUDIO_SIZE_BYTES, MAX_CHUNK_DURATION_SECONDS)
            temp_files.extend(audio_cleanup_files)
        
        elif state.input_type == "text":
            with open(state.input_path, "r") as file:
                text = file.read()

        elif state.input_type == "pdf":
            try:
                reader = PdfReader(state.input_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            except Exception as e:
                state.errors.append(f"Error reading PDF: {e}")
                raise RuntimeError(f"Error reading PDF: {e}")
        
        elif state.input_type == "url":
            if "youtube.com/watch" in state.input_path or "youtu.be/" in state.input_path:
                print(f"Detected YouTube URL: {state.input_path}")
                audio_path = download_youtube_audio(state.input_path)

                if not audio_path:
                    state.errors.append("Failed to download audio from YouTube URL.")
                    raise RuntimeError("Failed to download audio from YouTube URL.")

                text, audio_cleanup_files = process_audio_for_transcription(audio_path, MAX_WHISPER_AUDIO_SIZE_BYTES, MAX_CHUNK_DURATION_SECONDS)
                temp_files.extend(audio_cleanup_files)

            else:
                print(f"Detected general web URL: {state.input_path}")
                text = fetch_web_content(state.input_path)
                if not text:
                    state.errors.append("Failed to fetch content from the provided URL.")
                    raise RuntimeError("Failed to fetch content from the provided URL.")

    except FileNotFoundError as e:
        error_msg = f"Preprocessing failed: {e}"
        current_errors.append(error_msg)
        return {
            "errors": current_errors,
            "current_state": "preprocessing_failed",
            "validation_errors": current_validation_errors
        }
    
    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    current_errors.append(f"Error removing temporary file: {e}")

    # Basic preprocessing
    preprocessed_text = remove_timestamps(text)
    preprocessed_text = remove_noise_annotations(preprocessed_text)
    # preprocessed_text = remove_interviewer_dialogue(preprocessed_text)
    preprocessed_text = normalize_whitespace(preprocessed_text)
    preprocessed_text = truncate_text(preprocessed_text, MAX_LLM_INPUT_SIZE_BYTES)

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

def truncate_text(text: str, MAX_LLM_INPUT_SIZE_BYTES: int) -> str:

    print(f"Original text length: {len(text.encode('utf-8'))} bytes")

    if len(text.encode('utf-8')) > MAX_LLM_INPUT_SIZE_BYTES:
        original_length = len(text.encode('utf-8'))
        truncated_bytes = text.encode('utf-8')[:MAX_LLM_INPUT_SIZE_BYTES]
        truncated_text = truncated_bytes.decode('utf-8', errors='ignore')

        text = truncated_text
        print(f"Warning: Preprocessed text truncated to fit within LLM input limits. Some information may be lost. Original: {original_length} bytes, New: {len(text.encode('utf-8'))} bytes.")

    return text

def process_audio_for_transcription(audio_file_path: str, MAX_WHISPER_AUDIO_SIZE_BYTES: int, MAX_CHUNK_DURATION_SECONDS: int) -> Tuple[str, List[str]]:

    try:
        client = OpenAI()
        combined_transcript = []
        temp_audio_chunks = []

        audio_file_size = os.path.getsize(audio_file_path)
        
        if audio_file_size <= MAX_WHISPER_AUDIO_SIZE_BYTES:
            print(f"Audio file size ({audio_file_size / (1024*1024):.2f} MB) is within Whisper API limit. Transcribing directly.")
            with open(audio_file_path, "rb") as file:
                transcript = client.audio.transcriptions.create(
                    file=file,
                    model="whisper-1",
                    response_format="text"
                )
            return transcript, []
        
        else:
            print(f"Audio file size ({audio_file_size / (1024*1024):.2f} MB) exceeds Whisper API limit. Splitting audio...")

            try:
                audio = AudioSegment.from_file(audio_file_path)
                duration_ms = len(audio)

                chunk_length_ms = MAX_CHUNK_DURATION_SECONDS * 1000

                for i, start_ms in enumerate(range(0, duration_ms, chunk_length_ms)):
                    end_ms = min(start_ms + chunk_length_ms, duration_ms)
                    chunk = audio[start_ms:end_ms]

                    chunk_file_path = os.path.join(tempfile.gettempdir(), f"audio_chunk_{os.urandom(8).hex()}.mp3")
                    chunk.export(chunk_file_path, format="mp3")
                    temp_audio_chunks.append(chunk_file_path)

                    chunk_size_mb = os.path.getsize(chunk_file_path) / (1024 * 1024)
                    print(f"  Transcribing chunk {i+1} ({start_ms/1000:.1f}s-{end_ms/1000:.1f}s), size: {chunk_size_mb:.2f} MB...")

                    with open(chunk_file_path, "rb") as file:
                        transcript_chunk = client.audio.transcriptions.create(
                            file=file,
                            model="whisper-1",
                            response_format="text"
                        )
                    combined_transcript.append(transcript_chunk.strip())
                
                return "\n".join(combined_transcript), temp_audio_chunks

            except Exception as e:
                print(f"Error splitting or transcribing audio chunks: {e}")
                raise RuntimeError(f"Failed to process large audio file: {e}")
            
    except Exception as e:
        print(f"Error processing audio file {audio_file_path}: {e}")
        raise RuntimeError(f"Failed to process audio file: {e}")

def fetch_web_content(url: str) -> Optional[str]:

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        text = soup.get_text(separator='\n')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        print(f"Successfully fetched content from {url}, length: {len(text)} chars.")
        return text
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None
    
    except Exception as e:
        print(f"An unexpected error occurred while processing content from {url}: {e}")
        return None

def download_youtube_audio(youtube_url: str) -> Optional[str]:

    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, f"youtube_audio_{os.urandom(8).hex()}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path, 
        'quiet': True,       
        'no_warnings': True,  
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            downloaded_file = ydl.prepare_filename(info_dict)
            output_path = os.path.splitext(downloaded_file)[0] + '.mp3'

            if os.path.exists(output_path):
                print(f"Successfully downloaded YouTube audio to: {output_path}")
                return output_path
            elif os.path.exists(downloaded_file):
                print(f"Successfully downloaded YouTube audio to: {downloaded_file}")
                return downloaded_file
            else:
                print(f"Downloaded file not found at expected path: {output_path} or {downloaded_file}")
                return None
            
    except yt_dlp.utils.DownloadError as e:
        print(f"Error downloading YouTube audio from {youtube_url}: {e}")
        return None
    
    except Exception as e:
        print(f"An unexpected error occurred during YouTube audio download: {e}")
        return None