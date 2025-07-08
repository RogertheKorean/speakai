# models.py
from typing import Optional, List
from pydantic import BaseModel

class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class Page(BaseModel):
    id: int
    title: str
    type: str
    completed: bool = False
    content: Optional[str] = None

class Section(BaseModel):
    id: int
    title: str
    completed: bool = False
    pages: List[Page]

class HistoryItem(BaseModel):
    filename: str
    transcription: str
    feedback: str
    tag: str
