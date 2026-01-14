"""
Multilingual ASR (Automatic Speech Recognition) API Endpoints

This module provides speech-to-text services for all supported languages.
Each language has its own trained model and works within the same language only.

Supported Languages:
- English (en)
- Hindi (hi)
- Telugu (te)
- Kannada (kn)

Note: ASR works within the same language only - English audio → English text, etc.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from ..services.bhashini import asr_transcribe  # You'll need to extend this for multilingual
from ..utils.languages import validate_language, LANGUAGE_NAMES
from ..utils.validators import ensure_asr_constraints

router = APIRouter(prefix="/asr", tags=["speech-recognition"])

class ASRRequest(BaseModel):
    language: str

class ASRResponse(BaseModel):
    recognized_text: str
    language: str
    language_name: str

@router.post("/", response_model=ASRResponse)
async def transcribe_audio(audio_file: UploadFile = File(...), language: str = "en"):
    """
    Transcribe audio to text in the specified language.
    
    The audio and output text will be in the same language.
    Each language uses its own trained ASR model.
    
    Args:
        audio_file: WAV audio file (≤5MB, ~≤20s)
        language: Language code (en/hi/te/kn)
        
    Returns:
        ASRResponse with recognized text and language info
    """
    try:
        # Validate language
        lang = validate_language(language)
        
        # Validate audio constraints
        ensure_asr_constraints(audio_file)
        
        # TODO: Replace with actual multilingual ASR service
        # For now, this calls the existing service - you'll need to extend it
        recognized_text = await asr_transcribe(audio_file, language=lang)
        
        return ASRResponse(
            recognized_text=recognized_text,
            language=lang,
            language_name=LANGUAGE_NAMES[lang]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ASR failed: {str(e)}")

# Language-specific endpoints for easier API mapping

@router.post("/english")
async def transcribe_english_audio(audio_file: UploadFile = File(...)):
    """
    Transcribe English audio to English text.
    
    This endpoint specifically handles English speech recognition.
    Input: English audio file
    Output: English text
    """
    return await transcribe_audio(audio_file, language="en")

@router.post("/hindi") 
async def transcribe_hindi_audio(audio_file: UploadFile = File(...)):
    """
    Transcribe Hindi audio to Hindi text.
    
    This endpoint specifically handles Hindi speech recognition.
    Input: Hindi audio file
    Output: Hindi text
    """
    return await transcribe_audio(audio_file, language="hi")

@router.post("/telugu")
async def transcribe_telugu_audio(audio_file: UploadFile = File(...)):
    """
    Transcribe Telugu audio to Telugu text.
    
    This endpoint specifically handles Telugu speech recognition.
    Input: Telugu audio file
    Output: Telugu text
    """
    return await transcribe_audio(audio_file, language="te")

@router.post("/kannada")
async def transcribe_kannada_audio(audio_file: UploadFile = File(...)):
    """
    Transcribe Kannada audio to Kannada text.
    
    This endpoint specifically handles Kannada speech recognition.
    Input: Kannada audio file
    Output: Kannada text
    """
    return await transcribe_audio(audio_file, language="kn")

@router.get("/supported-languages")
async def get_supported_asr_languages():
    """
    Get all supported languages for speech recognition.
    
    Returns a list of all languages that have trained ASR models available.
    Each language works independently within the same language only.
    """
    from ..utils.languages import SUPPORTED_LANGUAGES
    
    return {
        "supported_languages": [
            {
                "code": lang,
                "name": LANGUAGE_NAMES[lang],
                "description": f"{LANGUAGE_NAMES[lang]} speech → {LANGUAGE_NAMES[lang]} text"
            }
            for lang in SUPPORTED_LANGUAGES
        ]
    }