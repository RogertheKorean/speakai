# auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt, JWTError
from typing import Optional
import datetime
import sqlite3
from models import User, Token
from db import get_connection
import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_db(username: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, full_name, hashed_password, disabled FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0], "username": row[1], "full_name": row[2], "hashed_password": row[3], "disabled": bool(row[4])
        }
    return None

def authenticate_user(username: str, password: str):
    user = get_user_db(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_db(username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register")
def register(username: str = Form(...), password: str = Form(...), full_name: Optional[str] = Form(None)):
    if get_user_db(username):
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(password)
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (username, full_name, hashed_password, disabled) VALUES (?, ?, ?, 0)",
              (username, full_name, hashed_password))
    conn.commit()
    conn.close()
    return {"msg": "User registered successfully"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}
