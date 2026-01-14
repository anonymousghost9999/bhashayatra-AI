import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, str(default)).strip().lower()
    return raw in ("1", "true", "yes", "on")


def _get_list(name: str, default: str) -> list[str]:
    return [s.strip() for s in os.getenv(name, default).split(",") if s.strip()]


@dataclass
class Settings:
    # Bhashini
    BHASHINI_API_KEY: str = os.getenv("BHASHINI_API_KEY", "")
    BHASHINI_ASR_URL: str = os.getenv("BHASHINI_ASR_URL", "")
    BHASHINI_MT_URL: str = os.getenv("BHASHINI_MT_URL", "")
    BHASHINI_TTS_URL: str = os.getenv("BHASHINI_TTS_URL", "")
    BHASHINI_OCR_URL: str = os.getenv("BHASHINI_OCR_URL", "")

    # Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # CORS / Server
    ALLOWED_ORIGINS: list[str] = None
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    def __post_init__(self):
        if self.ALLOWED_ORIGINS is None:
            # Default allow local dev origins, including simple static site on :5500 and Vite (:5173/:5174)
            self.ALLOWED_ORIGINS = _get_list(
                "ALLOWED_ORIGINS",
                "http://localhost:5500,http://127.0.0.1:5500,"
                "http://localhost:5173,http://127.0.0.1:5173,"
                "http://localhost:5174,http://127.0.0.1:5174"
            )


settings = Settings()
