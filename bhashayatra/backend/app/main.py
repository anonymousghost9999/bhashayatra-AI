from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import translate_speech, image_translate, itinerary, chat, summarize, mt
from .routers import multilingual_translate, multilingual_asr, multilingual_tts, multilingual_ocr
from .routers import unified_operations

app = FastAPI(title="TourBuddy AI API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health
@app.get("/health")
def health():
    return {"status": "ok"}

# Routers
# Legacy endpoints (keep for backward compatibility)
app.include_router(translate_speech.router)
app.include_router(image_translate.router)
app.include_router(itinerary.router)
app.include_router(chat.router)
app.include_router(summarize.router)
app.include_router(mt.router)

# New multilingual endpoints
app.include_router(multilingual_translate.router)
app.include_router(multilingual_asr.router)
app.include_router(multilingual_tts.router)
app.include_router(multilingual_ocr.router)

# Unified operations endpoint (recommended for UI)
app.include_router(unified_operations.router)
