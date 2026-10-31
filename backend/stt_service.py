import os
import logging
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

load_dotenv()

# Logging configuration - strictly prevents logging audio bytes or credentials
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("haqdaar.stt")

app = FastAPI(title="HAQDAAR STT Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_CANDIDATE = os.getenv("GEMINI_STT_MODEL", "gemini-3.5-flash-lite")

SUPPORTED_LANGUAGES = {
    "hi": {
        "name": "Hindi",
        "script": "Devanagari",
        "locale": "hi-IN"
    },
    "mr": {
        "name": "Marathi",
        "script": "Devanagari",
        "locale": "mr-IN"
    },
    "ta": {
        "name": "Tamil",
        "script": "Tamil",
        "locale": "ta-IN"
    }
}

ALLOWED_MIME_TYPES = {
    "audio/webm",
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/mp3",
    "audio/mpeg",
    "audio/ogg",
    "audio/m4a",
    "audio/mp4"
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB maximum upload

# Initialize Gemini client securely server-side
client = genai.Client(api_key=API_KEY) if API_KEY else None

class STTResponse(BaseModel):
    status: str
    transcript: str
    language: str
    language_name: str
    provider: str
    audio_bytes_received: int
    mime_type: str

def get_verified_model() -> str:
    """Verifies and returns the configured model identifier."""
    if not client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini API client not initialized. GEMINI_API_KEY is missing on server."
        )
    return MODEL_CANDIDATE

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "stt",
        "model": MODEL_CANDIDATE,
        "has_credentials": bool(API_KEY)
    }

@app.post("/api/stt", response_model=STTResponse)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file blob from MediaRecorder"),
    language: str = Form(..., description="Target language code: hi, mr, or ta")
):
    # 1. Language validation - Strict rejection without silent substitution
    clean_lang = language.strip().lower()
    if clean_lang not in SUPPORTED_LANGUAGES:
        logger.warning(f"Rejected unsupported STT language request: '{language}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language '{language}'. Supported: Hindi ('hi'), Marathi ('mr'), Tamil ('ta'). Silent substitution is prohibited."
        )

    lang_meta = SUPPORTED_LANGUAGES[clean_lang]

    # 2. MIME type validation
    content_type = (file.content_type or "").lower().split(";")[0].strip()
    if content_type not in ALLOWED_MIME_TYPES:
        # Fallback inspection by filename extension if mime type is octet-stream
        ext = os.path.splitext(file.filename or "")[1].lower()
        ext_mime_map = {
            ".webm": "audio/webm",
            ".wav": "audio/wav",
            ".mp3": "audio/mpeg",
            ".ogg": "audio/ogg",
            ".m4a": "audio/mp4"
        }
        if ext in ext_mime_map:
            content_type = ext_mime_map[ext]
        else:
            logger.warning(f"Rejected unsupported audio MIME type: '{file.content_type}'")
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported audio type '{file.content_type}'. Allowed: audio/webm, audio/wav, audio/mp3, audio/ogg, audio/m4a."
            )

    # 3. Read and validate payload size
    try:
        audio_bytes = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded audio stream: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded audio stream."
        )

    audio_size = len(audio_bytes)
    if audio_size == 0:
        logger.warning("Rejected empty audio upload (0 bytes)")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded audio file is empty (0 bytes)."
        )

    if audio_size > MAX_FILE_SIZE_BYTES:
        logger.warning(f"Rejected audio exceeding size limit: {audio_size} bytes")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio payload size ({audio_size} bytes) exceeds 10MB limit."
        )

    # 4. Transcribe using Gemini multimodal audio capabilities
    target_model = get_verified_model()
    prompt = (
        f"Transcribe this spoken audio verbatim in the {lang_meta['name']} language "
        f"using the original {lang_meta['script']} script. "
        "Do not translate into English or other languages. "
        "Return ONLY the verbatim transcript text without quotation marks, markdown headings, or commentary."
    )

    try:
        # Map audio/mpeg to audio/mp3 for genai compatibility if necessary
        genai_mime = "audio/mp3" if content_type in ["audio/mpeg", "audio/mp3"] else content_type

        response = client.models.generate_content(
            model=target_model,
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type=genai_mime),
                prompt
            ],
            config=types.GenerateContentConfig(
                temperature=0.0
            )
        )

        transcript = (response.text or "").strip()
        logger.info(f"Successfully transcribed {audio_size} bytes for language '{clean_lang}' using {target_model}")

        return STTResponse(
            status="success",
            transcript=transcript,
            language=clean_lang,
            language_name=lang_meta["name"],
            provider=target_model,
            audio_bytes_received=audio_size,
            mime_type=content_type
        )

    except Exception as e:
        logger.exception(f"Gemini STT transcription failed for language '{clean_lang}'")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Speech transcription provider error: {str(e)}"
        )

