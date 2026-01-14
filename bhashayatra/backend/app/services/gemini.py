from google import genai
from ..config import settings
from typing import Optional

INLINE_GEMINI_API_KEY = "AIzaSyBPiK3XOEmXg0xfSMEVUf5jltcYJlr3yfQ"
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"


def _get_api_key() -> str:
    api_key = (INLINE_GEMINI_API_KEY or settings.GEMINI_API_KEY or "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    return api_key


def _get_client() -> genai.Client:
    return genai.Client(api_key=_get_api_key())


def _select_model(model_override: Optional[str] = None) -> str:
    requested = (
        model_override
        or getattr(settings, "GEMINI_MODEL", "")
        or "gemini-2.0-flash"
    ).strip()

    candidates = [requested]
    for fallback in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"]:
        if fallback not in candidates:
            candidates.append(fallback)

    client = _get_client()
    last_error: Exception | None = None

    for model_id in candidates:
        try:
            client.models.get(model=model_id)
            return model_id
        except Exception as exc:
            last_error = exc
            print(f"Skipping {model_id}: {exc}")
            continue

    raise RuntimeError(
        f"Unable to initialise Gemini model. Tried: {', '.join(candidates)}"
    ) from last_error


def generate_itinerary(destination: str, days: int, interests: list[str] | None) -> str:
    prompt = (
        "You are TourBuddy, a concise travel planner. Create a practical, time-boxed itinerary.\n"
        f"Destination: {destination}\n"
        f"Days: {days}\n"
        f"Interests: {', '.join(interests or []) or 'general sightseeing and local food'}\n\n"
        "Format per day with morning/afternoon/evening, include travel time hints, entry fees if known, and local food suggestions."
    )
    client = _get_client()
    model = _select_model()
    resp = client.models.generate_content(model=model, contents=prompt)
    return getattr(resp, "text", "") or ""


def chat_completion(messages: list[dict[str, str]]) -> str:
    # Flatten messages into a single prompt (basic chat)
    formatted = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        formatted.append(f"{role.upper()}: {content}")
    prompt = "\n".join(formatted) + "\nASSISTANT:"
    client = _get_client()
    model = _select_model()
    resp = client.models.generate_content(model=model, contents=prompt)
    return getattr(resp, "text", "") or ""


def summarize_text(text: str) -> str:
    prompt = (
        "Summarize the following content into clear bullet points with key facts, times, prices, and contacts if present.\n\n"
        f"CONTENT:\n{text}"
    )
    client = _get_client()
    model = _select_model()
    resp = client.models.generate_content(model=model, contents=prompt)
    return getattr(resp, "text", "") or ""
