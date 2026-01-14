import httpx
from typing import Optional
from fastapi import UploadFile
from ..config import settings
from ..utils.validators import ensure_mt_constraints, ensure_tts_constraints, ensure_asr_constraints, ensure_ocr_constraints

# Inline API endpoints - you need to replace these URLs with actual working endpoints
# Current endpoints are for demonstration - map each to your actual Bhashini API URLs

INLINE_BHASHINI_API_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjhlYTc3YzhiOTNlM2JlYzkwMWZkY2I3Iiwicm9sZSI6Im1lZ2F0aG9uX3N0dWRlbnQifQ.ZHdNQlUu_TqRU3KJ4HryvrHqqS4Wfpuii8xyIYMtcso"

# ==================== TRANSLATION ENDPOINTS ====================
# These handle text translation between language pairs

# English → Other Languages
MT_EN_TO_HI_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb92316383c"  # English → Hindi translation
MT_EN_TO_TE_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb92316389a"  # TODO: English → Telugu translation endpoint
MT_EN_TO_KN_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb923163823"  # TODO: English → Kannada translation endpoint

# Hindi → Other Languages  
MT_HI_TO_EN_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb92316384a"  # TODO: Hindi → English translation endpoint
MT_HI_TO_TE_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb92316388e"  # TODO: Hindi → Telugu translation endpoint
MT_HI_TO_KN_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb9231638a3"  # TODO: Hindi → Kannada translation endpoint

# Telugu → Other Languages
MT_TE_TO_EN_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb923163869"  # TODO: Telugu → English translation endpoint
MT_TE_TO_HI_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb923163897"  # TODO: Telugu → Hindi translation endpoint
MT_TE_TO_KN_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb923163896"  # TODO: Telugu → Kannada translation endpoint

# Kannada → Other Languages
MT_KN_TO_EN_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb92316389d"  # TODO: Kannada → English translation endpoint
MT_KN_TO_HI_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb9231638a9"  # TODO: Kannada → Hindi translation endpoint
MT_KN_TO_TE_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb9231638b1"  # TODO: Kannada → Telugu translation endpoint

# ==================== ASR (SPEECH-TO-TEXT) ENDPOINTS ====================
# These convert audio to text within the same language

ASR_ENGLISH_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/infer_asr/67127dcbb1a6984f0c5e7d35"  # English audio → English text
ASR_HINDI_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/infer_asr/67100d22a0397bc812dacb27"    # TODO: Hindi audio → Hindi text endpoint
ASR_TELUGU_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/infer_asr/67b840e29c21bec07537674b"   # TODO: Telugu audio → Telugu text endpoint
ASR_KANNADA_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/infer_asr/6834189e620e7a7dd24ec499"  # TODO: Kannada audio → Kannada text endpoint

# ==================== TTS (TEXT-TO-SPEECH) ENDPOINTS ====================
# These convert text to audio within the same language
# Gender (male/female) is passed as a parameter to the same endpoint

TTS_ENGLISH_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/generate_tts/67bca8b3e0b95a6a1ea34a93"  # English text → English audio (supports both male/female)
TTS_HINDI_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/generate_tts/67bca89ae0b95a6a1ea34a92"    # TODO: Hindi text → Hindi audio endpoint
TTS_TELUGU_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/generate_tts/67b842f39c21bec07537674e"   # TODO: Telugu text → Telugu audio endpoint
TTS_KANNADA_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/generate_tts/67bca94de0b95a6a1ea34a98"  # TODO: Kannada text → Kannada audio endpoint

# ==================== OCR (IMAGE-TO-TEXT) ENDPOINTS ====================
# These extract text from images within the same language

OCR_ENGLISH_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_ocr_status_and_infer/687f420802ae0a1948845594"  # English text in image → English text
OCR_HINDI_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_ocr_status_and_infer/6711fe751595b8ffe97adc1f"     # TODO: Hindi text in image → Hindi text endpoint
OCR_TELUGU_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_ocr_status_and_infer/687f65f502ae0a19488455b5"    # TODO: Telugu text in image → Telugu text endpoint
OCR_KANNADA_URL: str = "https://canvas.iiit.ac.in/sandboxbeprod/check_ocr_status_and_infer/687f64db02ae0a19488455b0"   # TODO: Kannada text in image → Kannada text endpoint

TIMEOUT = httpx.Timeout(120.0, connect=30.0)  # Increased timeout for slow APIs

def _token() -> str:
    """Get the API token for Bhashini services"""
    return (INLINE_BHASHINI_API_KEY or settings.BHASHINI_API_KEY or "").strip()

def _get_mt_url(source_lang: str, target_lang: str) -> str:
    """Get translation URL based on source and target language pair"""
    # Map language pair to specific endpoint URL
    url_map = {
        ("en", "hi"): MT_EN_TO_HI_URL,
        ("en", "te"): MT_EN_TO_TE_URL,
        ("en", "kn"): MT_EN_TO_KN_URL,
        ("hi", "en"): MT_HI_TO_EN_URL,
        ("hi", "te"): MT_HI_TO_TE_URL,
        ("hi", "kn"): MT_HI_TO_KN_URL,
        ("te", "en"): MT_TE_TO_EN_URL,
        ("te", "hi"): MT_TE_TO_HI_URL,
        ("te", "kn"): MT_TE_TO_KN_URL,
        ("kn", "en"): MT_KN_TO_EN_URL,
        ("kn", "hi"): MT_KN_TO_HI_URL,
        ("kn", "te"): MT_KN_TO_TE_URL,
    }
    return url_map.get((source_lang, target_lang), "")

def _get_asr_url(language: str) -> str:
    """Get ASR URL based on language"""
    # Map language to specific ASR endpoint
    url_map = {
        "en": ASR_ENGLISH_URL,
        "hi": ASR_HINDI_URL,
        "te": ASR_TELUGU_URL,
        "kn": ASR_KANNADA_URL,
    }
    return url_map.get(language, "")

def _get_tts_url(language: str, gender: str = "female") -> str:
    """Get TTS URL based on language (gender is passed as parameter)"""
    # Map language to TTS endpoint (gender is handled as parameter)
    url_map = {
        "en": TTS_ENGLISH_URL,
        "hi": TTS_HINDI_URL,
        "te": TTS_TELUGU_URL,
        "kn": TTS_KANNADA_URL,
    }
    return url_map.get(language, "")

def _get_ocr_url(language: str) -> str:
    """Get OCR URL based on language"""
    # Map language to specific OCR endpoint
    url_map = {
        "en": OCR_ENGLISH_URL,
        "hi": OCR_HINDI_URL,
        "te": OCR_TELUGU_URL,
        "kn": OCR_KANNADA_URL,
    }
    return url_map.get(language, "")


async def mt_translate(input_text: str, source_lang: str = "en", target_lang: str = "hi") -> str:
    """
    Translate text between specified language pairs.
    
    Args:
        input_text: Text to translate
        source_lang: Source language code (en/hi/te/kn)
        target_lang: Target language code (en/hi/te/kn)
    
    Returns:
        Translated text
    
    Endpoint mapping:
    - en→hi: Use MT_EN_TO_HI_URL (English text → Hindi text)
    - en→te: Use MT_EN_TO_TE_URL (English text → Telugu text)
    - en→kn: Use MT_EN_TO_KN_URL (English text → Kannada text)
    - hi→en: Use MT_HI_TO_EN_URL (Hindi text → English text)
    - And so on for all 12 language pairs...
    """
    ensure_mt_constraints(input_text)
    
    # Get the specific URL for this language pair
    url = _get_mt_url(source_lang, target_lang)
    if not url:
        raise RuntimeError(f"Translation from {source_lang} to {target_lang} not configured. Please add the endpoint URL.")
    
    token = _token()
    if not token:
        raise RuntimeError("BHASHINI_API_KEY not configured")
    
    headers = {"access-token": token}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(url, json={"input_text": input_text}, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("output_text", "")


async def asr_transcribe(audio_file: UploadFile, language: str = "en") -> str:
    """
    Convert audio to text in the specified language.
    
    Args:
        audio_file: WAV audio file to transcribe
        language: Language of the audio (en/hi/te/kn)
    
    Returns:
        Recognized text in the same language as the audio
    
    Endpoint mapping:
    - en: Use ASR_ENGLISH_URL (English audio → English text)
    - hi: Use ASR_HINDI_URL (Hindi audio → Hindi text)
    - te: Use ASR_TELUGU_URL (Telugu audio → Telugu text)
    - kn: Use ASR_KANNADA_URL (Kannada audio → Kannada text)
    """
    data = ensure_asr_constraints(audio_file)
    
    # Get the specific URL for this language
    url = _get_asr_url(language)
    if not url:
        raise RuntimeError(f"ASR for {language} not configured. Please add the endpoint URL.")
    
    token = _token()
    if not token:
        raise RuntimeError("BHASHINI_API_KEY not configured")
    
    files = {"audio_file": (audio_file.filename, data, audio_file.content_type or "audio/wav")}
    headers = {"access-token": token}
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(url, headers=headers, files=files)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("recognized_text", "")


async def tts_synthesize(text: str, gender: Optional[str] = "female", language: str = "en") -> str:
    """
    Convert text to speech in the specified language and gender.
    
    Args:
        text: Text to convert to speech
        gender: Voice gender ("male" or "female")
        language: Language of the text and desired speech (en/hi/te/kn)
    
    Returns:
        URL to the generated audio file
    
    Endpoint mapping:
    - en: Use TTS_ENGLISH_URL (English text → English audio, gender as parameter)
    - hi: Use TTS_HINDI_URL (Hindi text → Hindi audio, gender as parameter)
    - te: Use TTS_TELUGU_URL (Telugu text → Telugu audio, gender as parameter)
    - kn: Use TTS_KANNADA_URL (Kannada text → Kannada audio, gender as parameter)
    """
    ensure_tts_constraints(text)
    
    gender = (gender or "female").lower()
    if gender not in ("male", "female"):
        gender = "female"
    
    # Get the specific URL for this language (gender passed as parameter)
    url = _get_tts_url(language, gender)
    if not url:
        raise RuntimeError(f"TTS for {language} not configured. Please add the endpoint URL.")
    
    token = _token()
    if not token:
        raise RuntimeError("BHASHINI_API_KEY not configured")
    
    headers = {"access-token": token}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(url, json={"text": text, "gender": gender}, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("s3_url", "")


async def ocr_extract(image_file: UploadFile, language: str = "en") -> str:
    """
    Extract text from image in the specified language.
    
    Args:
        image_file: Image file (JPG/PNG) containing text
        language: Language of the text in the image (en/hi/te/kn)
    
    Returns:
        Extracted text in the same language as the image content
    
    Endpoint mapping:
    - en: Use OCR_ENGLISH_URL (Image with English text → English text)
    - hi: Use OCR_HINDI_URL (Image with Hindi text → Hindi text)
    - te: Use OCR_TELUGU_URL (Image with Telugu text → Telugu text)
    - kn: Use OCR_KANNADA_URL (Image with Kannada text → Kannada text)
    """
    data = ensure_ocr_constraints(image_file)
    
    # Get the specific URL for this language
    url = _get_ocr_url(language)
    if not url:
        raise RuntimeError(f"OCR for {language} not configured. Please add the endpoint URL.")
    
    token = _token()
    if not token:
        raise RuntimeError("BHASHINI_API_KEY not configured")
    
    files = {"file": (image_file.filename, data, image_file.content_type or "image/png")}
    headers = {"access-token": token}
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(url, headers=headers, files=files)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("decoded_text", "")
