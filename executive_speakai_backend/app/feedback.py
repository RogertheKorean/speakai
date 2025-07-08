# feedback.py

import os
import uuid
import shutil
import datetime
import requests
from fastapi import APIRouter, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from models import HistoryItem
from db import get_connection
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile):
    try:
        uid = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1] or ".webm"
        save_path = f"temp/{uid}{ext}"
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        headers = {"authorization": ASSEMBLYAI_API_KEY}
        with open(save_path, 'rb') as audio_file:
            upload_res = requests.post(
                "https://api.assemblyai.com/v2/upload",
                headers=headers,
                data=audio_file
            )
        audio_url = upload_res.json()["upload_url"]
        transcript_res = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            json={"audio_url": audio_url},
            headers=headers
        )
        transcript_id = transcript_res.json()["id"]
        while True:
            poll_res = requests.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers=headers
            )
            status = poll_res.json()["status"]
            if status == "completed":
                break
            if status == "error":
                raise Exception("Transcription error")
        transcript_text = poll_res.json()["text"]
        client = OpenAI(api_key=OPENAI_API_KEY)
        gpt_res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an English speaking coach."},
                {"role": "user", "content": f"Please give feedback on this speaking sample: {transcript_text}"}
            ]
        )
        feedback_text = gpt_res.choices[0].message.content.strip()
        return {"filename": os.path.basename(save_path), "transcription": transcript_text, "feedback": feedback_text}
    except Exception as e:
        print("UPLOAD ERROR:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/save-history")
async def save_history(item: HistoryItem):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO history (filename, transcription, feedback, timestamp, tag) VALUES (?, ?, ?, ?, ?)",
            (
                item.filename,
                item.transcription,
                item.feedback,
                str(datetime.datetime.now()),
                item.tag
            )
        )
        conn.commit()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        print("SAVE HISTORY ERROR:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/history", response_class=HTMLResponse)
def serve_history_page(request: Request):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse("history.html", {"request": request, "history": rows})

@router.post("/delete/{id}")
def delete_history_item(id: int):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT filename FROM history WHERE id = ?", (id,))
        row = c.fetchone()
        if row:
            file_path = os.path.join("temp", row[0])
            if os.path.exists(file_path):
                os.remove(file_path)
            c.execute("DELETE FROM history WHERE id = ?", (id,))
            conn.commit()
        conn.close()
        return RedirectResponse(url="/history", status_code=303)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/download/txt/{id}")
def download_transcript(id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT transcription FROM history WHERE id = ?", (id,))
    result = c.fetchone()
    conn.close()
    if not result:
        return JSONResponse(status_code=404, content={"error": "Transcript not found"})
    text_path = f"temp/{id}_transcript.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(result[0])
    return FileResponse(text_path, filename=f"transcript_{id}.txt", media_type='text/plain')
