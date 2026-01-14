# TourBuddy AI Multilingual API Documentation

This document describes all available API endpoints for the multilingual TourBuddy AI system supporting English, Hindi, Telugu, and Kannada.

## Supported Languages
- **English** (en)
- **Hindi** (hi)  
- **Telugu** (te)
- **Kannada** (kn)

## Service Types

### 1. Translation (Cross-Language)
Translation works between different languages - you can translate from any supported language to any other supported language.

### 2. ASR, TTS, OCR (Same-Language)  
These services work within the same language only:
- **ASR**: English audio → English text
- **TTS**: Hindi text → Hindi audio
- **OCR**: Telugu image → Telugu text

---

## 1. TRANSLATION ENDPOINTS

### Universal Translation
**POST** `/translate/`
```json
{
  "text": "Hello world",
  "source_language": "en", 
  "target_language": "hi"
}
```
**What it does**: Translate text between any supported language pair

### Specific Language Pair Endpoints

#### English ↔ Hindi
- **POST** `/translate/en-to-hi` - English → Hindi translation
- **POST** `/translate/hi-to-en` - Hindi → English translation

#### English ↔ Telugu  
- **POST** `/translate/en-to-te` - English → Telugu translation
- **POST** `/translate/te-to-en` - Telugu → English translation

#### English ↔ Kannada
- **POST** `/translate/en-to-kn` - English → Kannada translation  
- **POST** `/translate/kn-to-en` - Kannada → English translation

#### Hindi ↔ Telugu
- **POST** `/translate/hi-to-te` - Hindi → Telugu translation
- **POST** `/translate/te-to-hi` - Telugu → Hindi translation

#### Hindi ↔ Kannada
- **POST** `/translate/hi-to-kn` - Hindi → Kannada translation
- **POST** `/translate/kn-to-hi` - Kannada → Hindi translation

#### Telugu ↔ Kannada  
- **POST** `/translate/te-to-kn` - Telugu → Kannada translation
- **POST** `/translate/kn-to-te` - Kannada → Telugu translation

#### Utility
- **GET** `/translate/supported-pairs` - Get all supported translation pairs

---

## 2. ASR (SPEECH-TO-TEXT) ENDPOINTS

### Universal ASR
**POST** `/asr/?language=en` (with audio file)
**What it does**: Convert audio to text in the specified language (same language only)

### Language-Specific ASR Endpoints

- **POST** `/asr/english` - English audio → English text
- **POST** `/asr/hindi` - Hindi audio → Hindi text  
- **POST** `/asr/telugu` - Telugu audio → Telugu text
- **POST** `/asr/kannada` - Kannada audio → Kannada text

#### Utility
- **GET** `/asr/supported-languages` - Get all supported ASR languages

---

## 3. TTS (TEXT-TO-SPEECH) ENDPOINTS

### Universal TTS
**POST** `/tts/`
```json
{
  "text": "Hello world",
  "language": "en",
  "gender": "female"
}
```
**What it does**: Convert text to speech in the specified language (same language only)

### Language-Specific TTS Endpoints

- **POST** `/tts/english` - English text → English audio
- **POST** `/tts/hindi` - Hindi text → Hindi audio
- **POST** `/tts/telugu` - Telugu text → Telugu audio  
- **POST** `/tts/kannada` - Kannada text → Kannada audio

**Note**: Gender selection is handled via the `"gender"` parameter in the request body for all TTS endpoints. No separate gender-specific endpoints are needed.

#### Utility
- **GET** `/tts/supported-languages` - Get all supported TTS languages

---

## 4. OCR (IMAGE-TO-TEXT) ENDPOINTS  

### Universal OCR
**POST** `/ocr/?language=en` (with image file)
**What it does**: Extract text from image in the specified language (same language only)

### Language-Specific OCR Endpoints

- **POST** `/ocr/english` - English text image → English text
- **POST** `/ocr/hindi` - Hindi text image → Hindi text
- **POST** `/ocr/telugu` - Telugu text image → Telugu text
- **POST** `/ocr/kannada` - Kannada text image → Kannada text

#### Utility
- **GET** `/ocr/supported-languages` - Get all supported OCR languages

---

## API Usage Examples

### Example 1: Translate English to Hindi
```bash
curl -X POST "http://localhost:8000/translate/en-to-hi" \
  -H "Content-Type: application/json" \
  -d '{"text": "Welcome to India"}'
```

### Example 2: Convert Hindi Text to Speech  
```bash
curl -X POST "http://localhost:8000/tts/hindi" \
  -H "Content-Type: application/json" \
  -d '{"text": "नमस्ते", "gender": "female"}'
```

### Example 3: Transcribe Telugu Audio
```bash
curl -X POST "http://localhost:8000/asr/telugu" \
  -F "audio_file=@telugu_audio.wav"
```

### Example 4: Extract Kannada Text from Image
```bash
curl -X POST "http://localhost:8000/ocr/kannada" \
  -F "image_file=@kannada_text_image.jpg"
```

---

## Complete Endpoint Matrix

### Translation (12 endpoints - all cross-language pairs)
| Source | Target | Endpoint |
|--------|--------|----------|
| English | Hindi | `/translate/en-to-hi` |
| Hindi | English | `/translate/hi-to-en` |
| English | Telugu | `/translate/en-to-te` |
| Telugu | English | `/translate/te-to-en` |
| English | Kannada | `/translate/en-to-kn` |
| Kannada | English | `/translate/kn-to-en` |
| Hindi | Telugu | `/translate/hi-to-te` |
| Telugu | Hindi | `/translate/te-to-hi` |
| Hindi | Kannada | `/translate/hi-to-kn` |
| Kannada | Hindi | `/translate/kn-to-hi` |
| Telugu | Kannada | `/translate/te-to-kn` |
| Kannada | Telugu | `/translate/kn-to-te` |

### ASR (4 endpoints - same language only)
| Language | Endpoint |
|----------|----------|
| English | `/asr/english` |
| Hindi | `/asr/hindi` |
| Telugu | `/asr/telugu` |
| Kannada | `/asr/kannada` |

### TTS (4 endpoints - same language only)
| Language | Endpoint | Gender Support |
|----------|----------|----------------|
| English | `/tts/english` | Pass `"gender": "male"` or `"gender": "female"` in request |
| Hindi | `/tts/hindi` | Pass `"gender": "male"` or `"gender": "female"` in request |
| Telugu | `/tts/telugu` | Pass `"gender": "male"` or `"gender": "female"` in request |
| Kannada | `/tts/kannada` | Pass `"gender": "male"` or `"gender": "female"` in request |

### OCR (4 endpoints - same language only)
| Language | Endpoint |
|----------|----------|
| English | `/ocr/english` |
| Hindi | `/ocr/hindi` |
| Telugu | `/ocr/telugu` |
| Kannada | `/ocr/kannada` |

---

## Total: 24 Specific Language Endpoints + 4 Universal Endpoints = 28 Endpoints

This comprehensive API structure allows you to map any combination of languages to the appropriate endpoints for all four core operations (MT, ASR, TTS, OCR).