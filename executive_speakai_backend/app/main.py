# main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import init_db
from auth import router as auth_router
from curriculum import router as curriculum_router
from feedback import router as feedback_router
from admin import router as admin_router

os.makedirs("temp", exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/temp", StaticFiles(directory="temp"), name="temp")
templates = Jinja2Templates(directory="templates")

# Initialize DB & tables at startup
@app.on_event("startup")
def startup_event():
    init_db()

# Include modular routers
app.include_router(auth_router)
app.include_router(curriculum_router)
app.include_router(feedback_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {"msg": "SpeakAI Modular Backend Running!"}
