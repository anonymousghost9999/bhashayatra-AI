import io
import re
import wave
from typing import Tuple
from fastapi import HTTPException, UploadFile, status

MAX_OCR_MB = 5
MAX_ASR_MB = 5
MAX_TTS_WORDS = 30
MAX_MT_WORDS = 50
MAX_ASR_SECONDS = 20.0

_ALLOWED_IMG_CT = {"image/jpeg", "image/png", "image/jpg"}
_ALLOWED_AUDIO_CT = {"audio/wav", "audio/x-wav", "audio/wave", "audio/vnd.wave"}

_WORD_RE = re.compile(r"\w+(?:'\w+)?")
# Allow Unicode letters (all languages) + common punctuation
_TTS_ALLOWED_CHARS_RE = re.compile(r"^[\w\s\.,!\?\-:;\(\)']+$", re.UNICODE)


def count_words(text: str) -> int:
    return len(_WORD_RE.findall(text or ""))


def ensure_mt_constraints(text: str):
    if count_words(text) > MAX_MT_WORDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MT limit exceeded: max {MAX_MT_WORDS} words",
        )


def ensure_tts_constraints(text: str):
    if count_words(text) > MAX_TTS_WORDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"TTS limit exceeded: max {MAX_TTS_WORDS} words",
        )
    # Removed character validation to support multilingual text (Hindi, Telugu, Kannada, etc.)


def _get_upload_bytes(upload: UploadFile) -> Tuple[bytes, str]:
    # Read entire file content into memory; ensure we reset cursor.
    content_type = upload.content_type or ""
    data = upload.file.read()
    try:
        upload.file.seek(0)
    except Exception:
        pass
    return data, content_type


def ensure_ocr_constraints(upload: UploadFile) -> bytes:
    data, content_type = _get_upload_bytes(upload)
    size_mb = len(data) / (1024 * 1024)
    if size_mb > MAX_OCR_MB:
        raise HTTPException(status_code=400, detail=f"OCR file too large: {size_mb:.2f} MB > {MAX_OCR_MB} MB")
    if content_type not in _ALLOWED_IMG_CT:
        raise HTTPException(status_code=400, detail="OCR requires JPG or PNG image")
    return data


def ensure_asr_constraints(upload: UploadFile) -> bytes:
    data, content_type = _get_upload_bytes(upload)
    size_mb = len(data) / (1024 * 1024)
    if size_mb > MAX_ASR_MB:
        raise HTTPException(status_code=400, detail=f"ASR audio too large: {size_mb:.2f} MB > {MAX_ASR_MB} MB")
    if content_type not in _ALLOWED_AUDIO_CT:
        raise HTTPException(status_code=400, detail="ASR requires WAV audio")

    # Estimate duration using wave module
    try:
        with wave.open(io.BytesIO(data), 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate) if rate else 0.0
            if duration > MAX_ASR_SECONDS + 0.5:
                raise HTTPException(status_code=400, detail=f"ASR audio too long: {duration:.1f}s > {MAX_ASR_SECONDS}s")
    except wave.Error:
        # If not a valid WAV file, raise
        raise HTTPException(status_code=400, detail="Invalid WAV file")

    return data
