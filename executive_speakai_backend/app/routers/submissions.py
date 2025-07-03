from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import SessionLocal
from app.services.gpt_feedback import generate_feedback

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.SubmissionOut)
def submit_response(data: schemas.SubmissionCreate, db: Session = Depends(get_db)):
    # Optional: regenerate feedback if not provided
    feedback = data.feedback or generate_feedback(data.transcript)

    submission = models.Submission(
        student_name=data.student_name,
        prompt_id=data.prompt_id,
        transcript=data.transcript,
        feedback=feedback,
        audio_path=data.audio_path,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission
