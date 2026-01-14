"""
Multilingual OCR (Optical Character Recognition) API Endpoints

This module provides image-to-text services for all supported languages.
Each language has its own trained OCR models and works within the same language only.

Supported Languages:
- English (en)
- Hindi (hi)
- Telugu (te)
- Kannada (kn)

Note: OCR works within the same language only - English text in image → English text, etc.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from ..services.bhashini import ocr_extract  # You'll need to extend this for multilingual
from ..utils.languages import validate_language, LANGUAGE_NAMES
from ..utils.validators import ensure_ocr_constraints

router = APIRouter(prefix="/ocr", tags=["optical-character-recognition"])

class OCRRequest(BaseModel):
    language: str

class OCRResponse(BaseModel):
    extracted_text: str
    language: str
    language_name: str

@router.post("/", response_model=OCRResponse)
async def extract_text_from_image(image_file: UploadFile = File(...), language: str = "en"):
    """
    Extract text from image in the specified language.
    
    The image contains text in the specified language and output will be in the same language.
    Each language uses its own trained OCR model for better accuracy.
    
    Args:
        image_file: Image file (JPG/PNG, ≤5MB)
        language: Language code (en/hi/te/kn) of text in the image
        
    Returns:
        OCRResponse with extracted text and language info
    """
    try:
        # Validate language
        lang = validate_language(language)
        
        # Validate image constraints
        ensure_ocr_constraints(image_file)
        
        # TODO: Replace with actual multilingual OCR service
        # For now, this calls the existing service - you'll need to extend it
        extracted_text = await ocr_extract(image_file, language=lang)
        
        return OCRResponse(
            extracted_text=extracted_text,
            language=lang,
            language_name=LANGUAGE_NAMES[lang]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

# Language-specific endpoints for easier API mapping

@router.post("/english")
async def extract_english_text(image_file: UploadFile = File(...)):
    """
    Extract English text from image.
    
    This endpoint specifically handles English OCR.
    Input: Image containing English text
    Output: Extracted English text
    """
    return await extract_text_from_image(image_file, language="en")

@router.post("/hindi")
async def extract_hindi_text(image_file: UploadFile = File(...)):
    """
    Extract Hindi text from image.
    
    This endpoint specifically handles Hindi OCR.
    Input: Image containing Hindi text
    Output: Extracted Hindi text
    """
    return await extract_text_from_image(image_file, language="hi")

@router.post("/telugu")
async def extract_telugu_text(image_file: UploadFile = File(...)):
    """
    Extract Telugu text from image.
    
    This endpoint specifically handles Telugu OCR.
    Input: Image containing Telugu text
    Output: Extracted Telugu text
    """
    return await extract_text_from_image(image_file, language="te")

@router.post("/kannada")
async def extract_kannada_text(image_file: UploadFile = File(...)):
    """
    Extract Kannada text from image.
    
    This endpoint specifically handles Kannada OCR.
    Input: Image containing Kannada text
    Output: Extracted Kannada text
    """
    return await extract_text_from_image(image_file, language="kn")

@router.get("/supported-languages")
async def get_supported_ocr_languages():
    """
    Get all supported languages for optical character recognition.
    
    Returns a list of all languages that have trained OCR models available.
    Each language works independently within the same language only.
    """
    from ..utils.languages import SUPPORTED_LANGUAGES
    
    return {
        "supported_languages": [
            {
                "code": lang,
                "name": LANGUAGE_NAMES[lang],
                "description": f"Image with {LANGUAGE_NAMES[lang]} text → {LANGUAGE_NAMES[lang]} text"
            }
            for lang in SUPPORTED_LANGUAGES
        ]
    }