import os
import uuid
import shutil
import datetime
import requests
import sqlite3
from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Create temp dir if it doesn't exist
os.makedirs("temp", exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/temp", StaticFiles(directory="temp"), name="temp")
templates = Jinja2Templates(directory="templates")

# === DATABASE SETUP ===
DB_PATH = "history.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# History table
c.execute('''
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    transcription TEXT,
    feedback TEXT,
    timestamp TEXT,
    tag TEXT
)
''')

# Courses
c.execute('''
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT
)
''')

# Sections
c.execute('''
CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    title TEXT,
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
''')

# Pages
c.execute('''
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER,
    title TEXT,
    type TEXT,
    completed INTEGER DEFAULT 0,
    viewed INTEGER DEFAULT 0,
    FOREIGN KEY(section_id) REFERENCES sections(id)
)
''')

conn.commit()

# Dummy data loader

def load_sample_curriculum():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM courses")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO courses (title) VALUES ('English Bootcamp')")
        course_id = c.lastrowid

        c.execute("INSERT INTO sections (course_id, title) VALUES (?, ?)", (course_id, "Day 1"))
        section_id = c.lastrowid

        pages = [
            (section_id, "Intro Lecture", "lecture"),
            (section_id, "Warm-up Quiz", "quiz"),
            (section_id, "Practice Speaking", "record"),
        ]
        c.executemany("INSERT INTO pages (section_id, title, type) VALUES (?, ?, ?)", pages)
        conn.commit()
        print("Sample curriculum loaded.")
    conn.close()

load_sample_curriculum()

@app.get("/curriculum", response_class=HTMLResponse)
def serve_curriculum_page(request: Request):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title FROM courses")
    courses = c.fetchall()

    sections_with_pages = []
    for course_id, course_title in courses:
        c.execute("SELECT id, title FROM sections WHERE course_id = ?", (course_id,))
        sections = c.fetchall()
        section_list = []
        for section_id, section_title in sections:
            c.execute("SELECT id, title, type, completed, viewed FROM pages WHERE section_id = ?", (section_id,))
            pages = c.fetchall()
            section_list.append({
                "id": section_id,
                "title": section_title,
                "pages": [
                    {
                        "id": page[0],
                        "title": page[1],
                        "type": page[2],
                        "completed": bool(page[3]),
                        "viewed": bool(page[4])
                    } for page in pages
                ]
            })
        sections_with_pages.append({
            "id": course_id,
            "title": course_title,
            "sections": section_list
        })
    conn.close()

    if sections_with_pages:
        sections = sections_with_pages[0]["sections"]
    else:
        sections = []

    all_done = all(
        all(page["completed"] for page in section["pages"])
        for section in sections
    ) if sections else False

    return templates.TemplateResponse("curriculum.html", {
        "request": request,
        "sections": sections,
        "all_done": all_done
    })

@app.get("/lecture/{page_id}", response_class=HTMLResponse)
def serve_lecture_page(request: Request, page_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT title FROM pages WHERE id = ?", (page_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return templates.TemplateResponse("lecture.html", {"request": request, "page_id": page_id, "page_title": row[0]})
    return JSONResponse(status_code=404, content={"error": "Page not found"})

@app.get("/quiz/{page_id}", response_class=HTMLResponse)
def serve_quiz_page(request: Request, page_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT title FROM pages WHERE id = ?", (page_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return templates.TemplateResponse("quiz.html", {"request": request, "page_id": page_id, "page_title": row[0]})
    return JSONResponse(status_code=404, content={"error": "Page not found"})

@app.get("/record/{page_id}", response_class=HTMLResponse)
def serve_record_page_with_id(request: Request, page_id: int):
    return templates.TemplateResponse("record.html", {"request": request, "page_id": page_id})

@app.get("/record", response_class=HTMLResponse)
def serve_record_page(request: Request):
    return templates.TemplateResponse("record.html", {"request": request})

import os
import uuid
import shutil
import datetime
import requests
import sqlite3
from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Create temp dir if it doesn't exist
os.makedirs("temp", exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/temp", StaticFiles(directory="temp"), name="temp")
templates = Jinja2Templates(directory="templates")

# === DATABASE SETUP ===
DB_PATH = "history.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# History table
c.execute('''
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    transcription TEXT,
    feedback TEXT,
    timestamp TEXT,
    tag TEXT
)
''')

# Courses
c.execute('''
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT
)
''')

# Sections
c.execute('''
CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    title TEXT,
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
''')

# Pages
c.execute('''
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER,
    title TEXT,
    type TEXT,
    completed INTEGER DEFAULT 0,
    viewed INTEGER DEFAULT 0,
    FOREIGN KEY(section_id) REFERENCES sections(id)
)
''')

conn.commit()

# Dummy data loader

def load_sample_curriculum():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM courses")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO courses (title) VALUES ('English Bootcamp')")
        course_id = c.lastrowid

        c.execute("INSERT INTO sections (course_id, title) VALUES (?, ?)", (course_id, "Day 1"))
        section_id = c.lastrowid

        pages = [
            (section_id, "Intro Lecture", "lecture"),
            (section_id, "Warm-up Quiz", "quiz"),
            (section_id, "Practice Speaking", "record"),
        ]
        c.executemany("INSERT INTO pages (section_id, title, type) VALUES (?, ?, ?)", pages)
        conn.commit()
        print("Sample curriculum loaded.")
    conn.close()

load_sample_curriculum()

@app.get("/curriculum", response_class=HTMLResponse)
def serve_curriculum_page(request: Request):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title FROM courses")
    courses = c.fetchall()

    sections_with_pages = []
    for course_id, course_title in courses:
        c.execute("SELECT id, title FROM sections WHERE course_id = ?", (course_id,))
        sections = c.fetchall()
        section_list = []
        for section_id, section_title in sections:
            c.execute("SELECT id, title, type, completed, viewed FROM pages WHERE section_id = ?", (section_id,))
            pages = c.fetchall()
            section_list.append({
                "id": section_id,
                "title": section_title,
                "pages": [
                    {
                        "id": page[0],
                        "title": page[1],
                        "type": page[2],
                        "completed": bool(page[3]),
                        "viewed": bool(page[4])
                    } for page in pages
                ]
            })
        sections_with_pages.append({
            "id": course_id,
            "title": course_title,
            "sections": section_list
        })
    conn.close()

    if sections_with_pages:
        sections = sections_with_pages[0]["sections"]
    else:
        sections = []

    all_done = all(
        all(page["completed"] for page in section["pages"])
        for section in sections
    ) if sections else False

    return templates.TemplateResponse("curriculum.html", {
        "request": request,
        "sections": sections,
        "all_done": all_done
    })

@app.get("/view/{page_id}")
def mark_page_viewed(page_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE pages SET viewed = 1 WHERE id = ?", (page_id,))
    c.execute("SELECT type FROM pages WHERE id = ?", (page_id,))
    row = c.fetchone()
    conn.commit()
    conn.close()

    if not row:
        return JSONResponse(status_code=404, content={"error": "Page not found"})

    page_type = row[0]
    if page_type == "lecture":
        return RedirectResponse(url=f"/lecture/{page_id}", status_code=303)
    elif page_type == "quiz":
        return RedirectResponse(url=f"/quiz/{page_id}", status_code=303)
    elif page_type == "record":
        return RedirectResponse(url=f"/record/{page_id}", status_code=303)
    else:
        return JSONResponse(status_code=400, content={"error": "Unknown page type"})


@app.get("/complete/{page_id}")
def mark_page_completed(page_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE pages SET completed = 1 WHERE id = ?", (page_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/curriculum", status_code=303)

@app.get("/admin/page", response_class=HTMLResponse)
def show_admin_form(request: Request):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title FROM sections")
    sections = c.fetchall()
    conn.close()
    return templates.TemplateResponse("admin_page.html", {"request": request, "sections": sections})

@app.post("/admin/page")
def create_page(request: Request, section_id: int = Form(...), title: str = Form(...), type: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO pages (section_id, title, type) VALUES (?, ?, ?)", (section_id, title, type))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/curriculum", status_code=303)

@app.get("/history", response_class=HTMLResponse)
def serve_history_page(request: Request):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return templates.TemplateResponse("history.html", {"request": request, "history": rows})

@app.post("/delete/{id}")
def delete_history_item(id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
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

@app.get("/download/txt/{id}")
def download_transcript(id: int):
    conn = sqlite3.connect(DB_PATH)
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

@app.post("/upload")
async def upload_file(file: UploadFile):
    try:
        uid = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1] or ".webm"
        save_path = f"temp/{uid}{ext}"

        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        headers = {"authorization": ASSEMBLYAI_API_KEY}

        with open(save_path, 'rb') as audio_file:
            upload_res = requests.post("https://api.assemblyai.com/v2/upload",
                                       headers=headers, data=audio_file)
        audio_url = upload_res.json()["upload_url"]

        json_data = {"audio_url": audio_url}
        transcript_res = requests.post("https://api.assemblyai.com/v2/transcript",
                                       json=json_data, headers=headers)
        transcript_id = transcript_res.json()["id"]

        while True:
            poll_res = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
            status = poll_res.json()["status"]
            if status == "completed":
                break
            elif status == "error":
                raise Exception("Transcription failed")

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

        return {
            "filename": os.path.basename(save_path),
            "transcription": transcript_text,
            "feedback": feedback_text
        }

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})

class HistoryItem(BaseModel):
    filename: str
    transcription: str
    feedback: str
    tag: str

@app.post("/save-history")
async def save_history(item: HistoryItem):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO history (filename, transcription, feedback, timestamp, tag) VALUES (?, ?, ?, ?, ?)",
                  (item.filename, item.transcription, item.feedback, str(datetime.datetime.now()), item.tag))
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        print("SAVE HISTORY ERROR:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
