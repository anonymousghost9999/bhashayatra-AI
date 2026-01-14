from fastapi import APIRouter, File, UploadFile
from ..services.bhashini import ocr_extract, mt_translate, tts_synthesize

router = APIRouter(prefix="/image", tags=["image"])


@router.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    decoded = await ocr_extract(file)
    return {"decoded_text": decoded}


@router.post("/translate")
async def translate(file: UploadFile = File(...), tts_gender: str = "female"):
    decoded = await ocr_extract(file)
    translated = await mt_translate(decoded)
    tts_url = await tts_synthesize(translated, tts_gender)
    return {"decoded_text": decoded, "translated_text": translated, "tts_url": tts_url}
