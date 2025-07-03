from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PromptBase(BaseModel):
    question: str

class PromptCreate(PromptBase):
    pass

class PromptOut(PromptBase):
    id: int

    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    title: str
    summary: Optional[str] = None

class SessionCreate(SessionBase):
    prompts: List[PromptCreate]

class SessionOut(SessionBase):
    id: int
    date: datetime
    prompts: List[PromptOut]

    class Config:
        from_attributes = True

class SubmissionCreate(BaseModel):
    student_name: str
    prompt_id: int
    transcript: str
    feedback: str
    audio_path: str

class SubmissionOut(BaseModel):
    id: int
    student_name: str
    transcript: str
    feedback: str
    audio_path: str
    submitted_at: datetime

    class Config:
        from_attributes = True
