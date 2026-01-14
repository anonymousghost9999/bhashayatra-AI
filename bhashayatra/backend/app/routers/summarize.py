from fastapi import APIRouter, File, UploadFile
from ..models.schemas import SummarizeRequest
from ..services.gemini import summarize_text
from ..services.bhashini import mt_translate, tts_synthesize, ocr_extract

router = APIRouter(prefix="/summarize", tags=["summarize"])


@router.post("/text")
async def summarize_from_text(req: SummarizeRequest):
    base = summarize_text(req.text or "")
    translated = await mt_translate(base) if req.target_lang else base
    tts_url = await tts_synthesize(translated) if req.speak else None
    return {"summary": base, "translated": translated if req.target_lang else None, "tts_url": tts_url}


@router.post("/ocr")
async def summarize_from_image(file: UploadFile = File(...), target_lang: str = "en", speak: bool = False):
    decoded = await ocr_extract(file)
    base = summarize_text(decoded)
    translated = await mt_translate(base) if target_lang else base
    tts_url = await tts_synthesize(translated) if speak else None
    return {"decoded_text": decoded, "summary": base, "translated": translated if target_lang else None, "tts_url": tts_url}
