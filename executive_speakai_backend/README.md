# Executive SpeakAI API (V1)

A FastAPI-based backend for an AI-powered executive English training app. Supports:
- Admin upload of session summaries and prompts
- Student submission of spoken responses
- GPT-3.5 feedback on grammar and expression

---

## 🚀 Setup

### 1. Clone and install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your OpenAI API key

Create a `.env` file or set an environment variable:

```bash
export OPENAI_API_KEY=your_openai_key_here
```

### 3. Initialize the database

```python
# Create tables
from app.database import init_db
init_db()
```

Or add this to `main.py` temporarily:

```python
from app.database import init_db
init_db()
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

---

## 🧪 API Endpoints

### ✅ Create a session (admin)

`POST /sessions/admin/session`

```json
{
  "title": "Session 1",
  "summary": "Introductions and small talk practice",
  "prompts": [
    {"question": "Tell me about your role at the company."},
    {"question": "How do you usually start meetings in English?"}
  ]
}
```

---

### 📋 Get sessions

- `GET /sessions/` — List all sessions  
- `GET /sessions/{id}` — Get prompts for one session

---

### 🎤 Submit a response

`POST /submit/`

```json
{
  "student_name": "Alice",
  "prompt_id": 1,
  "transcript": "I am working at Samsung as project manager.",
  "feedback": "",  // leave blank to auto-generate
  "audio_path": "/uploads/alice_q1.wav"
}
```

Returns: feedback and transcript details

---

## 📦 Folder Structure

```
app/
├── main.py
├── models.py
├── schemas.py
├── database.py
├── routers/
│   ├── sessions.py
│   └── submissions.py
└── services/
    └── gpt_feedback.py
```

---

## 🧠 Future Ideas

- Audio transcription (via Whisper)
- Pronunciation scoring
- Student dashboard and teacher feedback view

