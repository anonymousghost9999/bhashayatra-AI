"""
Unified Language-Aware Operations Router

This router provides a single interface for all operations where users can select:
- Source language (language of input)  
- Target language (desired output language)
- Operation type (what they want to do)

The system automatically determines what underlying operations are needed and chains them.

Examples:
- Text (Hindi) → Text (English): Uses MT
- Text (Hindi) → Audio (English): Uses MT + TTS  
- Audio (Hindi) → Text (English): Uses ASR + MT
- Audio (Hindi) → Audio (English): Uses ASR + MT + TTS
- Image (Hindi) → Text (English): Uses OCR + MT
- Image (Hindi) → Audio (English): Uses OCR + MT + TTS
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from typing import Optional

from ..services.pipeline import (
    text_to_text_pipeline,
    text_to_audio_pipeline,
    audio_to_text_pipeline, 
    audio_to_audio_pipeline,
    image_to_text_pipeline,
    image_to_audio_pipeline,
    PipelineResult
)
from ..utils.languages import validate_language, LANGUAGE_NAMES, SUPPORTED_LANGUAGES

router = APIRouter(prefix="/unified", tags=["unified-operations"])

class TextOperationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str
    output_type: str = "text"  # "text" or "audio"
    gender: Optional[str] = "female"

class OperationResponse(BaseModel):
    success: bool
    final_output: str
    source_language: str
    target_language: str
    input_type: str
    output_type: str
    operations_performed: list[str]
    intermediate_results: dict
    message: str

def create_response(result: PipelineResult, message: str = "Operation completed successfully") -> OperationResponse:
    """Helper to create standardized response from pipeline result"""
    return OperationResponse(
        success=True,
        final_output=str(result.final_output),
        source_language=result.source_language,
        target_language=result.target_language, 
        input_type=result.input_type,
        output_type=result.output_type,
        operations_performed=result.operations_performed,
        intermediate_results=result.intermediate_results,
        message=message
    )

@router.post("/text", response_model=OperationResponse)
async def process_text(request: TextOperationRequest):
    """
    Process text input with language selection.
    
    Can output either text or audio in the target language.
    Automatically handles translation if needed.
    
    Examples:
    - Hindi text → English text (uses MT)
    - Hindi text → Hindi audio (uses TTS) 
    - Hindi text → English audio (uses MT + TTS)
    - English text → English text (no operation needed, returns as-is)
    """
    try:
        # Validate languages
        source_lang = validate_language(request.source_language)
        target_lang = validate_language(request.target_language)
        
        if request.output_type.lower() == "audio":
            # Text → Audio
            result = await text_to_audio_pipeline(
                text=request.text,
                source_language=source_lang,
                target_language=target_lang,
                gender=request.gender or "female"
            )
            message = f"Converted {LANGUAGE_NAMES[source_lang]} text to {LANGUAGE_NAMES[target_lang]} audio"
        else:
            # Text → Text  
            result = await text_to_text_pipeline(
                text=request.text,
                source_language=source_lang,
                target_language=target_lang
            )
            if source_lang == target_lang:
                message = f"Text returned as-is (same language: {LANGUAGE_NAMES[source_lang]})"
            else:
                message = f"Translated from {LANGUAGE_NAMES[source_lang]} to {LANGUAGE_NAMES[target_lang]}"
        
        return create_response(result, message)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Check if it's a timeout error
        if "timeout" in str(e).lower() or "readtimeout" in str(e).lower():
            raise HTTPException(status_code=500, detail="Timeout error")
        else:
            raise HTTPException(status_code=500, detail="Operation failed")

@router.post("/audio", response_model=OperationResponse)
async def process_audio(
    audio_file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...),
    output_type: str = Form("text"),
    gender: Optional[str] = Form("female")
):
    """
    Process audio input with language selection.
    
    Can output either text or audio in the target language.
    Automatically handles transcription and translation if needed.
    
    Examples:
    - Hindi audio → English text (uses ASR + MT)
    - Hindi audio → Hindi text (uses ASR)
    - Hindi audio → English audio (uses ASR + MT + TTS)
    - Hindi audio → Hindi audio (uses ASR + TTS)
    """
    try:
        # Validate languages
        source_lang = validate_language(source_language)
        target_lang = validate_language(target_language)
        
        if output_type.lower() == "audio":
            # Audio → Audio
            result = await audio_to_audio_pipeline(
                audio_file=audio_file,
                source_language=source_lang,
                target_language=target_lang,
                gender=gender or "female"
            )
            message = f"Converted {LANGUAGE_NAMES[source_lang]} audio to {LANGUAGE_NAMES[target_lang]} audio"
        else:
            # Audio → Text
            result = await audio_to_text_pipeline(
                audio_file=audio_file,
                source_language=source_lang,
                target_language=target_lang
            )
            if source_lang == target_lang:
                message = f"Transcribed {LANGUAGE_NAMES[source_lang]} audio to text"
            else:
                message = f"Transcribed and translated {LANGUAGE_NAMES[source_lang]} audio to {LANGUAGE_NAMES[target_lang]} text"
        
        return create_response(result, message)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Check if it's a timeout error
        if "timeout" in str(e).lower() or "readtimeout" in str(e).lower():
            raise HTTPException(status_code=500, detail="Timeout error")
        else:
            raise HTTPException(status_code=500, detail="Operation failed")

@router.post("/image", response_model=OperationResponse)
async def process_image(
    image_file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...), 
    output_type: str = Form("text"),
    gender: Optional[str] = Form("female")
):
    """
    Process image input with language selection.
    
    Can output either text or audio in the target language.
    Automatically handles OCR and translation if needed.
    
    Examples:
    - Hindi image → English text (uses OCR + MT)
    - Hindi image → Hindi text (uses OCR)
    - Hindi image → English audio (uses OCR + MT + TTS) 
    - Hindi image → Hindi audio (uses OCR + TTS)
    """
    try:
        # Validate languages
        source_lang = validate_language(source_language)
        target_lang = validate_language(target_language)
        
        if output_type.lower() == "audio":
            # Image → Audio
            result = await image_to_audio_pipeline(
                image_file=image_file,
                source_language=source_lang,
                target_language=target_lang,
                gender=gender or "female"
            )
            message = f"Extracted {LANGUAGE_NAMES[source_lang]} text from image and converted to {LANGUAGE_NAMES[target_lang]} audio"
        else:
            # Image → Text
            result = await image_to_text_pipeline(
                image_file=image_file,
                source_language=source_lang,
                target_language=target_lang
            )
            if source_lang == target_lang:
                message = f"Extracted {LANGUAGE_NAMES[source_lang]} text from image"
            else:
                message = f"Extracted {LANGUAGE_NAMES[source_lang]} text from image and translated to {LANGUAGE_NAMES[target_lang]}"
        
        return create_response(result, message)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Check if it's a timeout error
        if "timeout" in str(e).lower() or "readtimeout" in str(e).lower():
            raise HTTPException(status_code=500, detail="Timeout error")
        else:
            raise HTTPException(status_code=500, detail="Operation failed")

@router.get("/supported-languages")
async def get_supported_languages():
    """
    Get all supported languages for operations.
    
    Returns list of languages that can be used as source or target.
    """
    return {
        "supported_languages": [
            {
                "code": lang,
                "name": LANGUAGE_NAMES[lang]
            }
            for lang in SUPPORTED_LANGUAGES
        ]
    }

@router.get("/operation-combinations")
async def get_operation_combinations():
    """
    Get all possible input/output type combinations.
    
    Shows what operations the system can perform.
    """
    return {
        "combinations": [
            {
                "input": "text",
                "output": "text", 
                "description": "Text translation or pass-through",
                "example": "Hindi text → English text"
            },
            {
                "input": "text",
                "output": "audio",
                "description": "Text to speech with optional translation",
                "example": "Hindi text → English audio"
            },
            {
                "input": "audio", 
                "output": "text",
                "description": "Speech recognition with optional translation",
                "example": "Hindi audio → English text"
            },
            {
                "input": "audio",
                "output": "audio", 
                "description": "Audio translation (speech-to-speech)",
                "example": "Hindi audio → English audio"
            },
            {
                "input": "image",
                "output": "text",
                "description": "OCR with optional translation", 
                "example": "Hindi image → English text"
            },
            {
                "input": "image",
                "output": "audio",
                "description": "OCR to speech with optional translation",
                "example": "Hindi image → English audio"
            }
        ]
    }