# TourBuddy AI – Multilingual Smart Tourism Assistant (Bhashini + Gemini)

This README walks you through everything from scratch on Windows (PowerShell) to run the backend, test all features, and optionally scaffold a frontend.

If you follow this document top-to-bottom, you will have:
- A running FastAPI backend that integrates Bhashini (AnuvaadHub) MT/ASR/TTS/OCR using the exact payloads and headers you were given.
- Gemini-powered itinerary, chat and summarization endpoints.
- Clear examples to test each endpoint with curl on Windows.
- Optional steps to scaffold a React (Vite) frontend.

--------------------------------------------------------------------------------

## 0) Quickstart (TL;DR)

- Ensure Python 3.10+ is installed (Windows). If not, install from https://www.python.org/downloads/
- Open PowerShell in the project root (Megathon-25).
- Create a virtual environment and install dependencies:
  powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r backend/requirements.txt

- Copy env template and fill in your AnuvaadHub endpoints + token and Gemini key:
  powershell
  Copy-Item backend/.env.example backend/.env
  notepad backend/.env

- In backend/.env, set:
  - BHASHINI_API_KEY= your AnuvaadHub access token (this is the value for the access-token header)
  - BHASHINI_MT_URL= the MT api_endpoint
  - BHASHINI_ASR_URL= the ASR api_endpoint
  - BHASHINI_TTS_URL= the TTS api_endpoint
  - BHASHINI_OCR_URL= the OCR api_endpoint
  - GEMINI_API_KEY= your Google Gemini key
  - MOCK_MODE=false to call real APIs

- Run the API server:
  powershell
  uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

- Test health:
  powershell
  curl http://localhost:8000/health

Done. See section 6 for full endpoint tests and payloads.

--------------------------------------------------------------------------------

## 1) Project Structure

The repo (created for you) looks like this:

- backend/
  - app/
    - main.py                FastAPI app entrypoint (CORS + routers)
    - config.py              Loads .env and settings
    - models/schemas.py      Pydantic models
    - services/
      - bhashini.py          Calls Bhashini MT/ASR/TTS/OCR per spec (access-token header)
      - gemini.py            Gemini integration for itinerary/chat/summarization
    - routers/
      - mt.py                MT translate endpoint (spec-compliant payload)
      - translate_speech.py  ASR, TTS, and speech->speech pipeline
      - image_translate.py   OCR, translate, speak pipeline
      - itinerary.py         Gemini itinerary + optional translate/tts
      - chat.py              Gemini chat + optional translate/tts
      - summarize.py         Summarize text or OCR + optional translate/tts
    - utils/validators.py    Enforces constraints (MT 50 words, TTS 30 words, etc.)
  - requirements.txt         Python dependencies
  - .env.example             Template for your keys and endpoints
- .gitignore                 Ignores venv, env files, node_modules, etc.

Optional frontend code is not yet scaffolded; instructions are provided below if you want to add it.

--------------------------------------------------------------------------------

## 2) Prerequisites (Windows)

- PowerShell 5.1+ (you have it)
- Python 3.10 or newer: https://www.python.org/downloads/
  - Ensure the "Add python.exe to PATH" option is selected during install.
- Node.js 18+ (only if you want to scaffold a frontend): https://nodejs.org/
- Optional (for audio prep): FFmpeg to convert to WAV if needed: https://www.gyan.dev/ffmpeg/builds/

Tip: If activating the virtual environment shows a script execution policy error, temporarily allow scripts for this session:
  powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

--------------------------------------------------------------------------------

## 3) Get Your Credentials and Endpoints (AnuvaadHub + Gemini)

You will paste these into backend/.env later.

- From AnuvaadHub (Bhashini), collect:
  - Access token (paste into BHASHINI_API_KEY). This value will be sent as the header access-token: <value> on every request to Bhashini.
  - MT api_endpoint
  - ASR api_endpoint
  - TTS api_endpoint
  - OCR api_endpoint

- From Google (Gemini):
  - GEMINI_API_KEY (for itinerary, chat, summarize)

Security reminder:
- Never commit your backend/.env or paste secrets into chat or public places.
- The .gitignore is configured to ignore .env.

--------------------------------------------------------------------------------

## 4) Configure Environment

1) Create the env file from the template:
  powershell
  Copy-Item backend/.env.example backend/.env

2) Open backend/.env and fill in values:
- BHASHINI_API_KEY=
- BHASHINI_MT_URL=
- BHASHINI_ASR_URL=
- BHASHINI_TTS_URL=
- BHASHINI_OCR_URL=
- GEMINI_API_KEY=
- ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173  # adjust if you add a frontend
- HOST=127.0.0.1
- PORT=8000
- MOCK_MODE=false  # set to true for offline mock responses

Notes:
- When MOCK_MODE=true, the backend returns mock strings and URLs without calling external APIs.
- When MOCK_MODE=false, all Bhashini requests include header access-token: BHASHINI_API_KEY as required.

--------------------------------------------------------------------------------

## 5) Install and Run the Backend

From the project root (Megathon-25):

1) Create and activate a virtual environment:
  powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1

2) Install Python dependencies:
  powershell
  pip install -r backend/requirements.txt

3) Start the FastAPI server:
  powershell
  uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

4) Health check:
  powershell
  curl http://localhost:8000/health

--------------------------------------------------------------------------------

## 6) API Endpoints, Payloads, Constraints, and Test Commands

All external requests made from our backend to Bhashini include the header access-token: BHASHINI_API_KEY. Your client (curl/Postman) does NOT need to set that header when calling our FastAPI.

Constraints (enforced server-side):
- MT: Maximum 50 words.
- ASR: WAV only, <= 5 MB, duration ~<= 20 seconds.
- TTS: Maximum 30 words, no special characters (letters, numbers, whitespace and basic punctuation only).
- OCR: JPG/PNG, <= 5 MB.

Important: For WAV, ensure 16-bit PCM WAV if possible. If your recorded audio is webm/ogg, convert to wav (see tips in Troubleshooting).

A) Machine Translation (MT)
- Endpoint (our backend): POST http://localhost:8000/mt/translate
- Request JSON: { "input_text": "Hello, how are you?" }
- Response JSON: { "output_text": "..." }
- Test (Windows curl):
  powershell
  curl -X POST http://localhost:8000/mt/translate -H "Content-Type: application/json" -d '{"input_text":"Hello, how are you?"}'

B) ASR (Audio Speech Recognition)
- Endpoint: POST http://localhost:8000/speech/asr
- Form-data: audio_file (WAV)
- Response: { "recognized_text": "..." }
- Test:
  powershell
  curl -X POST http://localhost:8000/speech/asr -F "audio_file=@C:/full/path/to/audio.wav;type=audio/wav"

C) TTS (Text to Speech)
- Endpoint: POST http://localhost:8000/speech/tts
- Request JSON: { "text": "string", "gender": "male"|"female" }
- Response: { "s3_url": "https://..." }
- Test:
  powershell
  curl -X POST http://localhost:8000/speech/tts -H "Content-Type: application/json" -d '{"text":"Welcome to Jaipur!","gender":"female"}'

D) OCR (Optical Character Recognition)
- Endpoint: POST http://localhost:8000/image/ocr
- Form-data: file (jpg/png)
- Response: { "decoded_text": "..." }
- Test:
  powershell
  curl -X POST http://localhost:8000/image/ocr -F "file=@C:/full/path/to/photo.jpg;type=image/jpeg"

E) Speech-to-Speech Translation Pipeline (ASR -> MT -> TTS)
- Endpoint: POST http://localhost:8000/speech/translate-speech?tts_gender=female
- Form-data: audio_file (WAV)
- Response: { recognized_text, translated_text, tts_url }
- Test:
  powershell
  curl -X POST "http://localhost:8000/speech/translate-speech?tts_gender=female" -F "audio_file=@C:/full/path/to/audio.wav;type=audio/wav"

F) Image Translate Pipeline (OCR -> MT -> TTS)
- Endpoint: POST http://localhost:8000/image/translate?tts_gender=female
- Form-data: file (jpg/png)
- Response: { decoded_text, translated_text, tts_url }
- Test:
  powershell
  curl -X POST "http://localhost:8000/image/translate?tts_gender=female" -F "file=@C:/full/path/to/photo.png;type=image/png"

G) Itinerary Generator (Gemini + optional MT + TTS)
- Endpoint: POST http://localhost:8000/itinerary/generate
- Request JSON:
  {
    "destination": "Jaipur",
    "days": 2,
    "interests": ["heritage", "food"],
    "target_lang": "en",
    "speak": true
  }
- Response: { itinerary, translated?, tts_url? }
- Test:
  powershell
  curl -X POST http://localhost:8000/itinerary/generate -H "Content-Type: application/json" -d '{"destination":"Jaipur","days":2,"interests":["heritage","food"],"target_lang":"en","speak":true}'

H) Chat (Gemini + optional MT + TTS)
- Endpoint: POST http://localhost:8000/chat
- Request JSON:
  {
    "messages": [
      {"role":"user","content":"Tell me about Amber Fort"}
    ],
    "target_lang": "en",
    "speak": false
  }
- Response: { reply, translated?, tts_url? }
- Test:
  powershell
  curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"Tell me about Amber Fort"}],"target_lang":"en","speak":false}'

I) Summarize Text (Gemini + optional MT + TTS)
- Endpoint: POST http://localhost:8000/summarize/text
- Request JSON: { "text": "...", "target_lang": "en", "speak": false }
- Response: { summary, translated?, tts_url? }
- Test:
  powershell
  curl -X POST http://localhost:8000/summarize/text -H "Content-Type: application/json" -d '{"text":"Amber Fort is a UNESCO World Heritage Site...","target_lang":"en","speak":false}'

J) Summarize from OCR (OCR -> Gemini summarize + optional MT + TTS)
- Endpoint: POST http://localhost:8000/summarize/ocr?target_lang=en&speak=false
- Form-data: file (jpg/png)
- Response: { decoded_text, summary, translated?, tts_url? }
- Test:
  powershell
  curl -X POST "http://localhost:8000/summarize/ocr?target_lang=en&speak=false" -F "file=@C:/full/path/to/photo.jpg;type=image/jpeg"

--------------------------------------------------------------------------------

## 7) Optional – Scaffold a React Frontend (Vite + TypeScript)

If you also want a simple UI to drive the backend:

1) Install Node.js (if not already): https://nodejs.org/

2) Create a Vite React project in the frontend folder:
  powershell
  npm create vite@latest frontend -- --template react-ts
  cd frontend
  npm install
  npm install axios

3) Create a .env.local in the frontend folder:
  text
  VITE_API_BASE_URL=http://localhost:8000

4) Start the dev server:
  powershell
  npm run dev

5) CORS: If the frontend runs on http://localhost:5173, it is already allowed via ALLOWED_ORIGINS in backend/.env. Adjust if needed.

6) Minimal API calls (pseudo-steps):
- Use axios to call `${import.meta.env.VITE_API_BASE_URL}/speech/asr` with form-data for WAV files.
- Similar for image OCR translate and other endpoints.

Note on audio recording: the browser MediaRecorder often produces webm/ogg. To meet the ASR WAV constraint, either upload a pre-recorded WAV (simplest for a demo), or use a client-side WAV encoder library. For hackathon speed, file upload (WAV) is recommended.

--------------------------------------------------------------------------------

## 8) Troubleshooting

- Virtual environment activation fails with "running scripts is disabled":
  powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

- 401 Unauthorized from Bhashini (in server logs):
  - Ensure BHASHINI_API_KEY is correct and not expired.
  - Ensure the header key is access-token on your API call (the backend does this automatically when MOCK_MODE=false).

- 400 errors mentioning constraints:
  - MT: ensure <= 50 words.
  - TTS: ensure <= 30 words, remove special characters (keep alphanumeric and basic punctuation).
  - ASR: ensure WAV, <= 5MB, duration <= ~20s.
  - OCR: ensure JPG/PNG, <= 5MB, correct content-type.

- ASR "Invalid WAV file":
  - Convert to 16-bit PCM WAV. Example with ffmpeg (if installed):
    powershell
    ffmpeg -i input.webm -ar 16000 -ac 1 -c:a pcm_s16le output.wav

- CORS blocked in browser:
  - Add your frontend origin to ALLOWED_ORIGINS in backend/.env, comma-separated.
  - Restart the backend.

- Port already in use (8000):
  - Change PORT in backend/.env and pass it to uvicorn, e.g. --port 8001.

- Gemini errors:
  - Ensure GEMINI_API_KEY is set and valid.
  - Internet access is required for Gemini calls.

--------------------------------------------------------------------------------

## 9) Production Tips (Optional)

- Run uvicorn behind a reverse proxy (nginx) and use multiple workers (e.g., gunicorn on Linux). On Windows during development, uvicorn --reload is fine.
- Add request logging and basic rate limiting.
- Never commit backend/.env.
- Validate user inputs on the frontend as well (e.g., warn when exceeding word limits).

--------------------------------------------------------------------------------

## 10) Reference: Implemented Contracts (Per Spec)

- Header sent to Bhashini: access-token: <BHASHINI_API_KEY>
- MT: Request { "input_text": "..." } → Response data.output_text
- ASR: Form-data audio_file (WAV) → Response data.recognized_text
- TTS: Request { "text":"string", "gender":"male|female" } → Response data.s3_url
- OCR: Form-data file (JPG/PNG) → Response data.decoded_text
- Constraints: MT 50 words, ASR ~20 sec & <5MB WAV, TTS 30 words & no special chars, OCR <5MB JPG/PNG

All of the above are enforced and/or followed by the backend code in backend/app.

--------------------------------------------------------------------------------

## 11) Next Steps

- Keep MOCK_MODE=true while wiring up UI and testing flows quickly. Switch to MOCK_MODE=false when your Bhashini endpoints and token are ready.
- Build a minimal UI for the five key features: speech translation, image translation, itinerary, chatbot, summarization.
- If you want, add streaming later (websocket or server-sent events) for lower latency UX.
