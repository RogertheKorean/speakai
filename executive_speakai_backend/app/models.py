### models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SessionHistory(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(200))
    transcription = Column(Text)
    feedback = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tag = Column(String(100), default="untagged")