from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/admin/session", response_model=schemas.SessionOut)
def create_session(session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    db_session = models.Session(title=session_data.title, summary=session_data.summary)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    for prompt_data in session_data.prompts:
        prompt = models.Prompt(session_id=db_session.id, question=prompt_data.question)
        db.add(prompt)

    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/", response_model=list[schemas.SessionOut])
def list_sessions(db: Session = Depends(get_db)):
    return db.query(models.Session).all()

@router.get("/{session_id}", response_model=schemas.SessionOut)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
