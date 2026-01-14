# Complete List of Inline API Endpoints Needed

This document lists all the inline API endpoint URLs you need to implement for full multilingual support across English, Hindi, Telugu, and Kannada.

## Current Status
✅ **Working Endpoints (You have these):**
- `MT_EN_TO_HI_URL` - English → Hindi translation  
- `ASR_ENGLISH_URL` - English audio → English text
- `TTS_ENGLISH_FEMALE_URL` - English text → English female voice
- `OCR_ENGLISH_URL` - English text in image → English text

❌ **Missing Endpoints (You need to add these):**

---

## 🔄 TRANSLATION ENDPOINTS (11 missing)

### English → Other Languages (2 missing)
- `MT_EN_TO_TE_URL` - **English text → Telugu text**
  - Input: English text
  - Output: Telugu translation
  - Example: "Hello" → "హలో"

- `MT_EN_TO_KN_URL` - **English text → Kannada text**  
  - Input: English text
  - Output: Kannada translation
  - Example: "Hello" → "ಹಲೋ"

### Hindi → Other Languages (3 missing)
- `MT_HI_TO_EN_URL` - **Hindi text → English text**
  - Input: Hindi text
  - Output: English translation
  - Example: "नमस्ते" → "Hello"

- `MT_HI_TO_TE_URL` - **Hindi text → Telugu text**
  - Input: Hindi text  
  - Output: Telugu translation
  - Example: "नमस्ते" → "నమస్తే"

- `MT_HI_TO_KN_URL` - **Hindi text → Kannada text**
  - Input: Hindi text
  - Output: Kannada translation  
  - Example: "नमस्ते" → "ನಮಸ್ತೆ"

### Telugu → Other Languages (3 missing)
- `MT_TE_TO_EN_URL` - **Telugu text → English text**
  - Input: Telugu text
  - Output: English translation
  - Example: "నమస్తే" → "Hello"

- `MT_TE_TO_HI_URL` - **Telugu text → Hindi text**
  - Input: Telugu text
  - Output: Hindi translation
  - Example: "నమస్తే" → "नमस्ते"

- `MT_TE_TO_KN_URL` - **Telugu text → Kannada text**
  - Input: Telugu text
  - Output: Kannada translation
  - Example: "నమస్తే" → "ನಮಸ್ತೆ"

### Kannada → Other Languages (3 missing)
- `MT_KN_TO_EN_URL` - **Kannada text → English text**
  - Input: Kannada text
  - Output: English translation
  - Example: "ನಮಸ್ತೆ" → "Hello"

- `MT_KN_TO_HI_URL` - **Kannada text → Hindi text**
  - Input: Kannada text
  - Output: Hindi translation
  - Example: "ನಮಸ್ತೆ" → "नमस्ते"

- `MT_KN_TO_TE_URL` - **Kannada text → Telugu text**
  - Input: Kannada text
  - Output: Telugu translation
  - Example: "ನಮಸ್ತೆ" → "నమస్తే"

---

## 🎤 ASR (SPEECH-TO-TEXT) ENDPOINTS (3 missing)

- `ASR_HINDI_URL` - **Hindi audio → Hindi text**
  - Input: WAV file with Hindi speech
  - Output: Hindi text transcription
  - Example: Hindi audio → "नमस्ते"

- `ASR_TELUGU_URL` - **Telugu audio → Telugu text**
  - Input: WAV file with Telugu speech  
  - Output: Telugu text transcription
  - Example: Telugu audio → "నమస్తే"

- `ASR_KANNADA_URL` - **Kannada audio → Kannada text**
  - Input: WAV file with Kannada speech
  - Output: Kannada text transcription
  - Example: Kannada audio → "ನಮಸ್ತೆ"

---

## 🔊 TTS (TEXT-TO-SPEECH) ENDPOINTS (3 missing)

**Note**: Gender (male/female) is now handled as a parameter to the same endpoint, eliminating the need for separate URLs.

- `TTS_HINDI_URL` - **Hindi text → Hindi audio (supports both genders)**
  - Input: Hindi text + gender parameter
  - Output: Audio URL with Hindi voice (male or female based on parameter)
  - Example: "नमस्ते" + "female" → female_voice.wav

- `TTS_TELUGU_URL` - **Telugu text → Telugu audio (supports both genders)**
  - Input: Telugu text + gender parameter
  - Output: Audio URL with Telugu voice (male or female based on parameter)
  - Example: "నమస్తే" + "male" → male_voice.wav

- `TTS_KANNADA_URL` - **Kannada text → Kannada audio (supports both genders)**
  - Input: Kannada text + gender parameter
  - Output: Audio URL with Kannada voice (male or female based on parameter)
  - Example: "ನಮಸ್ತೆ" + "female" → female_voice.wav

---

## 👁️ OCR (IMAGE-TO-TEXT) ENDPOINTS (3 missing)

- `OCR_HINDI_URL` - **Hindi text in image → Hindi text**
  - Input: JPG/PNG image containing Hindi text
  - Output: Extracted Hindi text
  - Example: Image with "नमस्ते" → "नमस्ते"

- `OCR_TELUGU_URL` - **Telugu text in image → Telugu text**
  - Input: JPG/PNG image containing Telugu text
  - Output: Extracted Telugu text  
  - Example: Image with "నమస్తే" → "నమస్తే"

- `OCR_KANNADA_URL` - **Kannada text in image → Kannada text**
  - Input: JPG/PNG image containing Kannada text
  - Output: Extracted Kannada text
  - Example: Image with "ನಮಸ್ತೆ" → "ನಮಸ್ತೆ"

---

## 📊 SUMMARY

**Total Endpoints Needed: 24**
- ✅ Working: 4 endpoints
- ❌ Missing: 20 endpoints

### Breakdown:
- **Translation**: 11 missing (out of 12 total)
- **ASR**: 3 missing (out of 4 total)  
- **TTS**: 3 missing (out of 4 total)
- **OCR**: 3 missing (out of 4 total)

---

## 🚀 How to Add Missing Endpoints

1. **Find your Bhashini API URLs** for each missing service
2. **Update the constants** in `backend/app/services/bhashini.py`
3. **Replace empty strings** with actual URLs:
   ```python
   # Replace this:
   MT_HI_TO_EN_URL: str = ""
   
   # With actual URL:
   MT_HI_TO_EN_URL: str = "https://your-bhashini-url-here"
   ```

4. **Test each endpoint** individually to ensure it works

Once you add all these URLs, your system will support:
- **All language pairs** for translation
- **All languages** for speech recognition  
- **All languages and genders** for text-to-speech
- **All languages** for OCR

The pipeline system will automatically chain these operations as needed!