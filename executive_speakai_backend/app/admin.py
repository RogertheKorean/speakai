# admin.py

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from db import get_connection
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/admin/page", response_class=HTMLResponse)
def show_admin_page(request: Request):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, title FROM sections")
    sections = c.fetchall()
    conn.close()
    return templates.TemplateResponse("admin_page.html", {"request": request, "sections": sections})

@router.post("/admin/page")
async def create_page(request: Request, section_id: int = Form(...), title: str = Form(...), type: str = Form(...)):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO pages (section_id, title, type) VALUES (?, ?, ?)", (section_id, title, type))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/curriculum", status_code=303)

@router.get("/admin/section", response_class=HTMLResponse)
def show_admin_section_page(request: Request):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, title FROM courses")
    courses = c.fetchall()
    conn.close()
    return templates.TemplateResponse("admin_section.html", {"request": request, "courses": courses})

@router.post("/admin/section")
async def create_section(request: Request, course_id: int = Form(...), title: str = Form(...)):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO sections (course_id, title) VALUES (?, ?)", (course_id, title))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/curriculum", status_code=303)
