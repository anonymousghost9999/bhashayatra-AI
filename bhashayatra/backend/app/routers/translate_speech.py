from fastapi import APIRouter, File, UploadFile, HTTPException
from ..services.bhashini import asr_transcribe, mt_translate, tts_synthesize

router = APIRouter(prefix="/speech", tags=["speech"])


@router.post("/asr")
async def asr(audio_file: UploadFile = File(...)):
    recognized = await asr_transcribe(audio_file)
    return {"recognized_text": recognized}


@router.post("/tts")
async def tts(payload: dict):
    text = payload.get("text", "")
    gender = payload.get("gender", "female")
    if not text:
        raise HTTPException(status_code=400, detail="Missing text")
    url = await tts_synthesize(text, gender)
    return {"s3_url": url}


@router.post("/translate-speech")
async def translate_speech(audio_file: UploadFile = File(...), tts_gender: str = "female"):
    """
    Pipeline: ASR -> MT -> TTS (optional, returns URL)
    """
    recognized = await asr_transcribe(audio_file)
    translated = await mt_translate(recognized)
    tts_url = await tts_synthesize(translated, tts_gender)
    return {
        "recognized_text": recognized,
        "translated_text": translated,
        "tts_url": tts_url,
    }
