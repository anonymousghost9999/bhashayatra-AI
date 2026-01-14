"""
Multilingual Translation API Endpoints

This module provides translation services between all supported language pairs:
- English ↔ Hindi
- English ↔ Telugu  
- English ↔ Kannada
- Hindi ↔ Telugu
- Hindi ↔ Kannada
- Telugu ↔ Kannada

All translation endpoints accept source and target language parameters.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.bhashini import mt_translate  # You'll need to extend this for multilingual
from ..utils.languages import validate_language, format_language_pair, get_translation_pairs
from ..utils.validators import ensure_mt_constraints

router = APIRouter(prefix="/translate", tags=["translation"])

class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    language_pair: str

@router.post("/", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text between any supported language pair.
    
    Supports all combinations:
    - English → Hindi, Telugu, Kannada
    - Hindi → English, Telugu, Kannada  
    - Telugu → English, Hindi, Kannada
    - Kannada → English, Hindi, Telugu
    
    Args:
        request: TranslationRequest with text, source_language, target_language
        
    Returns:
        TranslationResponse with original text, translated text, and language info
    """
    try:
        # Validate languages
        source_lang = validate_language(request.source_language)
        target_lang = validate_language(request.target_language)
        
        if source_lang == target_lang:
            raise HTTPException(status_code=400, detail="Source and target languages cannot be the same")
        
        # Validate text constraints
        ensure_mt_constraints(request.text)
        
        # TODO: Replace with actual multilingual translation service
        # For now, this calls the existing service - you'll need to extend it
        translated_text = await mt_translate(request.text, source_lang, target_lang)
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            source_language=source_lang,
            target_language=target_lang,
            language_pair=format_language_pair(source_lang, target_lang)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

# Individual language pair endpoints for easier API mapping

@router.post("/en-to-hi")
async def translate_english_to_hindi(request: dict):
    """
    Translate English text to Hindi.
    
    This endpoint specifically handles English → Hindi translation.
    Use this when you know the source is English and target is Hindi.
    """
    translation_request = TranslationRequest(
        text=request.get("text", ""),
        source_language="en",
        target_language="hi"
    )
    return await translate_text(translation_request)

@router.post("/hi-to-en")
async def translate_hindi_to_english(request: dict):
    """
    Translate Hindi text to English.
    
    This endpoint specifically handles Hindi → English translation.
    Use this when you know the source is Hindi and target is English.
    """
    translation_request = TranslationRequest(
        text=request.get("text", ""),
        source_language="hi",
        target_language="en"
    )
    return await translate_text(translation_request)

@router.post("/en-to-te")
async def translate_english_to_telugu(request: dict):
    """
    Translate English text to Telugu.
    
    This endpoint specifically handles English → Telugu translation.
    Use this when you know the source is English and target is Telugu.
    """
    translation_request = TranslationRequest(
        text=request.get("text", ""),
        source_language="en",
        target_language="te"
    )
    return await translate_text(translation_request)

@router.post("/te-to-en")
async def translate_telugu_to_english(request: dict):
    """
    Translate Telugu text to English.
    
    This endpoint specifically handles Telugu → English translation.
    Use this when you know the source is Telugu and target is English.
    """
    translation_request = TranslationRequest(
        text=request.get("text", ""),
        source_language="te",
        target_language="en"
    )
    return await translate_text(translation_request)

@router.post("/en-to-kn")
async def translate_english_to_kannada(request: dict):
    """
    Translate English text to Kannada.
    
    This endpoint specifically handles English → Kannada translation.
    Use this when you know the source is English and target is Kannada.
    """
    translation_request = TranslationRequest(
        text=request.get("text", ""),
        source_language="en",
        target_language="kn"
    )
    return await translate_text(translation_request)

@router.post("/kn-to-en")
async def translate_kannada_to_english(request: dict):
    """
    Translate Kannada text to English.
    
    This endpoint specifically handles Kannada → English translation.
    Use this when you know the source is Kannada and target is English.
    """
    translation_request = TranslationRequest(
        text=request.get("text", ""),
        source_language="kn",
        target_language="en"
    )
    return await translate_text(translation_request)

@router.post("/hi-to-te")
async def translate_hindi_to_telugu(request: dict):
    """
    Translate Hindi text to Telugu.
    
    This endpoint specifically handles Hindi → Telugu translation.
    Use this when you know the source is Hindi and target is Telugu.
    """
    translation_request = TranslationRequest(
        text=request.get("text", ""),
        source_language="hi",
        target_language="te"
    )
    return await translate_text(translation_request)

@router.post("/te-to-hi")
async def translate_telugu_to_hindi(request: dict):
    """
    Translate Telugu text to Hindi.
    
    This endpoint specifically handles Telugu → Hindi translation.
    Use this when you know the source is Telugu and target is Hindi.
    """
    translation_request = TranslationRequest(
        text=request.get("text", ""),
        source_language="te",
        target_language="hi"
    )
    return await translate_text(translation_request)

@router.post("/hi-to-kn")
async def translate_hindi_to_kannada(request: dict):
    """
    Translate Hindi text to Kannada.
    
    This endpoint specifically handles Hindi → Kannada translation.
    Use this when you know the source is Hindi and target is Kannada.
    """
    translation_request = TranslationRequest(
        text=request.get("text", ""),
        source_language="hi",
        target_language="kn"
    )
    return await translate_text(translation_request)

@router.post("/kn-to-hi")
async def translate_kannada_to_hindi(request: dict):
    """
    Translate Kannada text to Hindi.
    
    This endpoint specifically handles Kannada → Hindi translation.
    Use this when you know the source is Kannada and target is Hindi.
    """
    translation_request = TranslationRequest(
        text=request.get("text", ""),
        source_language="kn",
        target_language="hi"
    )
    return await translate_text(translation_request)

@router.post("/te-to-kn")
async def translate_telugu_to_kannada(request: dict):
    """
    Translate Telugu text to Kannada.
    
    This endpoint specifically handles Telugu → Kannada translation.
    Use this when you know the source is Telugu and target is Kannada.
    """
    translation_request = TranslationRequest(
        text=request.get("text", ""),
        source_language="te",
        target_language="kn"
    )
    return await translate_text(translation_request)

@router.post("/kn-to-te")
async def translate_kannada_to_telugu(request: dict):
    """
    Translate Kannada text to Telugu.
    
    This endpoint specifically handles Kannada → Telugu translation.
    Use this when you know the source is Kannada and target is Telugu.
    """
    translation_request = TranslationRequest(
        text=request.get("text", ""),
        source_language="kn",
        target_language="te"
    )
    return await translate_text(translation_request)

@router.get("/supported-pairs")
async def get_supported_translation_pairs():
    """
    Get all supported translation language pairs.
    
    Returns a list of all possible source→target language combinations
    that are supported by the translation service.
    """
    pairs = get_translation_pairs()
    return {
        "supported_pairs": [
            {
                "source": source,
                "target": target,
                "display_name": format_language_pair(source, target)
            }
            for source, target in pairs
        ]
    }