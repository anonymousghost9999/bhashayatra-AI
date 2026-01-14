from fastapi import APIRouter
from ..models.schemas import ChatRequest
from ..services.gemini import chat_completion
from ..services.bhashini import mt_translate, tts_synthesize

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat(req: ChatRequest):
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    base = chat_completion(messages)
    translated = await mt_translate(base) if req.target_lang else base
    tts_url = await tts_synthesize(translated) if req.speak else None
    return {"reply": base, "translated": translated if req.target_lang else None, "tts_url": tts_url}
