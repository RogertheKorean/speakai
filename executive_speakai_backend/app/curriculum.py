# curriculum.py

from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from models import Section, Page
from db import get_connection
from typing import List, Optional
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/curriculum", response_class=HTMLResponse)
def serve_curriculum_page(request: Request):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, title FROM courses")
    courses = c.fetchall()
    sections_with_pages = []
    for course_id, course_title in courses:
        c.execute("SELECT id, title FROM sections WHERE course_id = ?", (course_id,))
        sections = c.fetchall()
        section_list = []
        for section_id, section_title in sections:
            c.execute(
                "SELECT id, title, type, completed, viewed FROM pages WHERE section_id = ?", (section_id,)
            )
            pages = c.fetchall()
            section_list.append({
                "id": section_id,
                "title": section_title,
                "pages": [
                    {
                        "id": p[0],
                        "title": p[1],
                        "type": p[2],
                        "completed": bool(p[3]),
                        "viewed": bool(p[4])
                    } for p in pages
                ]
            })
        sections_with_pages.append({
            "id": course_id,
            "title": course_title,
            "sections": section_list
        })
    conn.close()
    sections = sections_with_pages[0]["sections"] if sections_with_pages else []
    all_done = all(
        all(page["completed"] for page in sec["pages"]) for sec in sections
    ) if sections else False
    return templates.TemplateResponse(
        "curriculum.html",
        {"request": request, "sections": sections, "all_done": all_done}
    )

@router.get("/view/{page_id}")
def mark_page_viewed(page_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE pages SET viewed = 1 WHERE id = ?", (page_id,))
    c.execute("SELECT type FROM pages WHERE id = ?", (page_id,))
    row = c.fetchone()
    conn.commit()
    conn.close()
    if not row:
        return JSONResponse(status_code=404, content={"error": "Page not found"})
    page_type = row[0]
    redirect_map = {
        "lecture": f"/lecture/{page_id}",
        "quiz": f"/quiz/{page_id}",
        "record": f"/record/{page_id}"
    }
    return RedirectResponse(
        url=redirect_map.get(page_type, "/curriculum"), status_code=303
    )

@router.get("/lecture/{page_id}", response_class=HTMLResponse)
def show_lecture_page(request: Request, page_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT title FROM pages WHERE id = ?", (page_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return JSONResponse(status_code=404, content={"error": "Lecture not found"})
    return templates.TemplateResponse("lecture.html", {"request": request, "title": row[0]})

@router.get("/quiz/{page_id}", response_class=HTMLResponse)
def show_quiz_page(request: Request, page_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT title FROM pages WHERE id = ?", (page_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return JSONResponse(status_code=404, content={"error": "Quiz not found"})
    return templates.TemplateResponse("quiz.html", {"request": request, "title": row[0]})

@router.get("/record/{page_id}", response_class=HTMLResponse)
def show_record_page(request: Request, page_id: int):
    return templates.TemplateResponse("record.html", {"request": request, "page_id": page_id})
