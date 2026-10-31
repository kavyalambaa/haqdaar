import os
import sys
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure backend directory is on sys.path for consistent module imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from tts_service import stream_tts, generate_tts, TTSRequest
from stt_service import transcribe_audio, STTResponse
from conversation_service import engine
from rag_kb import kb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("haqdaar.main")

app = FastAPI(
    title="HAQDAAR Multilingual Voice Assistant Gateway",
    version="2.0.0",
    description="Unified API Gateway connecting Kisan Sahayak, Yojana Sahayak, STT, and TTS."
)

# CORS configuration allowing local frontend Vite server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Citizen input text")
    language: str = Field(default="hi", description="Language code: hi, mr, or ta")
    persona: Optional[str] = Field(default="kisan", description="kisan or yojana")
    session_id: Optional[str] = Field(default=None, description="Conversation session UUID")

class ChatResponse(BaseModel):
    session_id: str
    reply_text: str
    spoken_text: str
    language: str
    persona: str
    sources: List[Dict[str, Any]]
    audio_stream_url: str

@app.get("/health")
async def health_check():
    """Unified system health check across all micro-modules."""
    return {
        "status": "ok",
        "gateway": "haqdaar_v2",
        "modules": {
            "tts": "active",
            "stt": "active",
            "conversation": "active",
            "rag": f"{len(kb.documents)} verified docs indexed"
        }
    }

# Re-expose Phase 1 TTS routes on the gateway with proper BackgroundTasks lifecycle
@app.post("/api/tts")
async def tts_legacy(request: TTSRequest, background_tasks: BackgroundTasks):
    return await generate_tts(request, background_tasks)

@app.post("/api/tts/stream")
async def tts_stream(request: TTSRequest):
    return await stream_tts(request)

# Re-expose Phase 2 STT routes on the gateway
@app.post("/api/stt", response_model=STTResponse)
async def stt_endpoint(
    file: UploadFile = File(...),
    language: str = Form(...)
):
    return await transcribe_audio(file=file, language=language)

# Phase 3 Conversation routes
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    msg = request.message.strip()
    if not msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )

    clean_lang = request.language.lower().strip()
    if clean_lang not in ["hi", "mr", "ta"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language '{request.language}'. Supported: hi, mr, ta."
        )

    result = engine.process_turn(
        message=msg,
        language=clean_lang,
        persona=request.persona,
        session_id=request.session_id
    )

    return ChatResponse(**result)

@app.get("/api/schemes")
async def list_schemes():
    """Returns verified catalog of schemes and ICAR guides with sources."""
    return {"catalog": kb.get_catalog()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

