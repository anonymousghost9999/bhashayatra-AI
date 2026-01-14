from pydantic import BaseModel
from typing import List, Literal, Optional


class ItineraryRequest(BaseModel):
    destination: str
    days: int = 2
    interests: Optional[List[str]] = None
    target_lang: str = "en"
    speak: bool = True


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    target_lang: str = "en"
    speak: bool = False


class SummarizeRequest(BaseModel):
    text: Optional[str] = None
    target_lang: str = "en"
    speak: bool = False
