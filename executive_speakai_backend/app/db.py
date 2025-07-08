# db.py
import sqlite3

DB_PATH = "history.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Users
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        full_name TEXT,
        hashed_password TEXT,
        disabled INTEGER DEFAULT 0
    )
    ''')
    # History
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
    conn.close()
