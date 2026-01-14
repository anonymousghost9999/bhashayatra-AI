from fastapi import APIRouter
from ..models.schemas import ItineraryRequest
from ..services.gemini import generate_itinerary
from ..services.bhashini import mt_translate, tts_synthesize

router = APIRouter(prefix="/itinerary", tags=["itinerary"])


@router.post("/generate")
async def generate(req: ItineraryRequest):
    base = generate_itinerary(req.destination, req.days, req.interests)
    translated = await mt_translate(base) if req.target_lang else base
    tts_url = await tts_synthesize(translated) if req.speak else None
    return {
        "itinerary": base,
        "translated": translated if req.target_lang else None,
        "tts_url": tts_url,
    }
