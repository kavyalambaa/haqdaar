import os
import logging
import tempfile
import asyncio
import edge_tts
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

# Configure basic logger to output to terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HAQDAAR TTS Service", version="1.0.0")

# CORS middleware for local Vite origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VOICE_MAPPING = {
    "hi": "hi-IN-SwaraNeural",
    "hi-in": "hi-IN-SwaraNeural",
    "mr": "mr-IN-AarohiNeural",
    "mr-in": "mr-IN-AarohiNeural",
    "ta": "ta-IN-PallaviNeural",
    "ta-in": "ta-IN-PallaviNeural"
}

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Text to synthesize")
    language: str = Field(..., description="Language code: hi, mr, or ta")

def remove_file(path: str):
    """Safely remove temporary audio file."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

async def create_edge_tts_stream(text: str, voice: str, timeout_sec: float = 15.0):
    """
    Initiates an in-memory audio stream using edge-tts Communicate.
    Captures the first chunk before returning to verify provider responsiveness
    and prevent emitting a broken 200 stream on immediate failure.
    """
    communicate = edge_tts.Communicate(text=text, voice=voice)
    stream_iter = communicate.stream()

    first_chunk = None

    async def fetch_first_chunk():
        nonlocal first_chunk
        async for chunk in stream_iter:
            if chunk.get("type") == "audio" and chunk.get("data"):
                first_chunk = chunk["data"]
                break

    try:
        await asyncio.wait_for(fetch_first_chunk(), timeout=timeout_sec)
    except asyncio.TimeoutError:
        logger.error(f"Timeout ({timeout_sec}s) while connecting to Edge TTS for voice '{voice}'")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="TTS Provider connection timed out. Please retry."
        )
    except Exception as e:
        logger.exception(f"Failed to initiate Edge TTS stream for voice '{voice}': {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TTS Provider Connection Failed: {str(e)}"
        )

    if first_chunk is None:
        logger.error(f"Edge TTS returned empty audio for voice '{voice}'")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="TTS Provider returned empty audio stream."
        )

    async def stream_generator():
        try:
            yield first_chunk
            async for chunk in stream_iter:
                if chunk.get("type") == "audio" and chunk.get("data"):
                    yield chunk["data"]
        except asyncio.CancelledError:
            logger.info(f"Client disconnected during TTS streaming for voice '{voice}'")
        except Exception as e:
            logger.warning(f"Error during audio stream transmission: {e}")

    return stream_generator()

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "tts"}

@app.post("/api/tts")
async def generate_tts(request: TTSRequest, background_tasks: BackgroundTasks):
    text = request.text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text payload cannot be empty."
        )

    lang = request.language.lower().strip()
    if lang not in VOICE_MAPPING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language '{request.language}'. Supported: hi, mr, ta."
        )

    voice = VOICE_MAPPING[lang]

    # Create temporary MP3 file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file_path = temp_file.name
    temp_file.close()

    try:
        # Native edge_tts Communicate API call
        communicate = edge_tts.Communicate(text=text, voice=voice)
        await communicate.save(temp_file_path)

        # Verify MP3 exists and is non-empty
        if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
            raise RuntimeError("Generated MP3 audio file is missing or empty.")

        # Schedule temporary file cleanup after response transmission
        background_tasks.add_task(remove_file, temp_file_path)

        return FileResponse(
            path=temp_file_path,
            media_type="audio/mpeg",
            filename=f"speech_{lang}.mp3"
        )
    except Exception as e:
        logger.exception("Native Edge TTS synthesis failed")
        remove_file(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS Generation Failed: {str(e)}"
        )

@app.post("/api/tts/stream")
async def stream_tts(request: TTSRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text payload cannot be empty."
        )

    lang = request.language.lower().strip()
    if lang not in VOICE_MAPPING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language '{request.language}'. Supported: Hindi ('hi'), Marathi ('mr'), Tamil ('ta'). Silent substitution is prohibited."
        )

    voice = VOICE_MAPPING[lang]
    generator = await create_edge_tts_stream(text=text, voice=voice)

    return StreamingResponse(
        generator,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f"inline; filename=stream_{lang}.mp3",
            "Cache-Control": "no-cache",
            "X-Voice-Used": voice,
            "X-Language": lang
        }
    )
