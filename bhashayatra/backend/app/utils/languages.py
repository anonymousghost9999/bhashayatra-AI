"""
Language constants and utilities for multilingual TourBuddy AI support.

Supported Languages:
- English (en)
- Hindi (hi) 
- Telugu (te)
- Kannada (kn)
"""

from typing import Dict, List, Tuple
from enum import Enum

class Language(str, Enum):
    """Supported languages enum"""
    ENGLISH = "en"
    HINDI = "hi"
    TELUGU = "te"
    KANNADA = "kn"

# Language code to name mapping
LANGUAGE_NAMES = {
    Language.ENGLISH: "English",
    Language.HINDI: "Hindi",
    Language.TELUGU: "Telugu", 
    Language.KANNADA: "Kannada"
}

# All supported languages list
SUPPORTED_LANGUAGES = [Language.ENGLISH, Language.HINDI, Language.TELUGU, Language.KANNADA]

def validate_language(lang_code: str) -> str:
    """
    Validate if language code is supported.
    Returns normalized language code or raises ValueError.
    """
    if lang_code not in SUPPORTED_LANGUAGES:
        supported = ", ".join(SUPPORTED_LANGUAGES)
        raise ValueError(f"Unsupported language: {lang_code}. Supported: {supported}")
    return lang_code

def get_translation_pairs() -> List[Tuple[str, str]]:
    """
    Get all possible translation pairs.
    Returns list of (source_lang, target_lang) tuples.
    """
    pairs = []
    for source in SUPPORTED_LANGUAGES:
        for target in SUPPORTED_LANGUAGES:
            if source != target:  # Don't translate to same language
                pairs.append((source, target))
    return pairs

def get_same_language_operations() -> List[str]:
    """
    Get all languages that support same-language operations (ASR, TTS, OCR).
    """
    return list(SUPPORTED_LANGUAGES)

def format_language_pair(source: str, target: str) -> str:
    """Format language pair for display (e.g., 'English to Hindi')"""
    source_name = LANGUAGE_NAMES.get(source, source)
    target_name = LANGUAGE_NAMES.get(target, target)
    return f"{source_name} to {target_name}"