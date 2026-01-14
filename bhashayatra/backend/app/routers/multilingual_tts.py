"""
Multilingual TTS (Text-to-Speech) API Endpoints

This module provides text-to-speech services for all supported languages.
Each language has its own trained voice models and works within the same language only.

Supported Languages:
- English (en)
- Hindi (hi)
- Telugu (te)
- Kannada (kn)

Note: TTS works within the same language only - English text → English audio, etc.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..services.bhashini import tts_synthesize  # You'll need to extend this for multilingual
from ..utils.languages import validate_language, LANGUAGE_NAMES
from ..utils.validators import ensure_tts_constraints

router = APIRouter(prefix="/tts", tags=["text-to-speech"])

class TTSRequest(BaseModel):
    text: str
    language: str
    gender: Optional[str] = "female"

class TTSResponse(BaseModel):
    audio_url: str
    text: str
    language: str
    language_name: str
    gender: str

@router.post("/", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """
    Convert text to speech in the specified language.
    
    The input text and output audio will be in the same language.
    Each language uses its own trained TTS models with male/female voices.
    
    Args:
        request: TTSRequest with text, language, and optional gender
        
    Returns:
        TTSResponse with audio URL and metadata
    """
    try:
        # Validate language
        lang = validate_language(request.language)
        
        # Validate text constraints
        ensure_tts_constraints(request.text)
        
        # Validate gender
        gender = (request.gender or "female").lower()
        if gender not in ["male", "female"]:
            gender = "female"
        
        # TODO: Replace with actual multilingual TTS service
        # For now, this calls the existing service - you'll need to extend it
        audio_url = await tts_synthesize(request.text, gender, language=lang)
        
        return TTSResponse(
            audio_url=audio_url,
            text=request.text,
            language=lang,
            language_name=LANGUAGE_NAMES[lang],
            gender=gender
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

# Language-specific endpoints for easier API mapping

@router.post("/english")
async def synthesize_english_speech(request: dict):
    """
    Convert English text to English speech.
    
    This endpoint specifically handles English text-to-speech.
    Input: English text
    Output: English audio
    """
    tts_request = TTSRequest(
        text=request.get("text", ""),
        language="en",
        gender=request.get("gender", "female")
    )
    return await synthesize_speech(tts_request)

@router.post("/hindi")
async def synthesize_hindi_speech(request: dict):
    """
    Convert Hindi text to Hindi speech.
    
    This endpoint specifically handles Hindi text-to-speech.
    Input: Hindi text
    Output: Hindi audio
    """
    tts_request = TTSRequest(
        text=request.get("text", ""),
        language="hi",
        gender=request.get("gender", "female")
    )
    return await synthesize_speech(tts_request)

@router.post("/telugu")
async def synthesize_telugu_speech(request: dict):
    """
    Convert Telugu text to Telugu speech.
    
    This endpoint specifically handles Telugu text-to-speech.
    Input: Telugu text
    Output: Telugu audio
    """
    tts_request = TTSRequest(
        text=request.get("text", ""),
        language="te",
        gender=request.get("gender", "female")
    )
    return await synthesize_speech(tts_request)

@router.post("/kannada")
async def synthesize_kannada_speech(request: dict):
    """
    Convert Kannada text to Kannada speech.
    
    This endpoint specifically handles Kannada text-to-speech.
    Input: Kannada text
    Output: Kannada audio
    """
    tts_request = TTSRequest(
        text=request.get("text", ""),
        language="kn",
        gender=request.get("gender", "female")
    )
    return await synthesize_speech(tts_request)

# Note: Gender is handled as a parameter in the main endpoints above.
# No need for separate male/female endpoints since the same service handles both.

@router.get("/supported-languages")
async def get_supported_tts_languages():
    """
    Get all supported languages for text-to-speech.
    
    Returns a list of all languages that have trained TTS models available.
    Each language works independently within the same language only.
    """
    from ..utils.languages import SUPPORTED_LANGUAGES
    
    return {
        "supported_languages": [
            {
                "code": lang,
                "name": LANGUAGE_NAMES[lang],
                "description": f"{LANGUAGE_NAMES[lang]} text → {LANGUAGE_NAMES[lang]} speech",
                "voices": ["male", "female"]
            }
            for lang in SUPPORTED_LANGUAGES
        ]
    }