from fastapi import APIRouter, HTTPException
from ..services.bhashini import mt_translate

router = APIRouter(prefix="/mt", tags=["mt"])


@router.post("/translate")
async def translate(payload: dict):
    text = payload.get("input_text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Missing input_text")
    output = await mt_translate(text)
    return {"output_text": output}
