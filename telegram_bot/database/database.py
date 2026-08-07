import sqlite3
from pathlib import Path

from config import DATABASE_NAME


def _db_path():
    project_root = Path(__file__).resolve().parents[1]
    return project_root / DATABASE_NAME


def get_connection():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        section TEXT NOT NULL,
        subsection TEXT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        wrong1 TEXT NOT NULL,
        wrong2 TEXT NOT NULL,
        wrong3 TEXT NOT NULL,
        wrong4 TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        username TEXT,
        first_seen TEXT,
        last_seen TEXT,
        visits INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS stats (
        user_id INTEGER,
        section TEXT,
        asked INTEGER DEFAULT 0,
        correct INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, section)
    );

    CREATE TABLE IF NOT EXISTS mistakes (
        user_id INTEGER,
        question_id INTEGER,
        PRIMARY KEY (user_id, question_id)
    );

    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        mode TEXT,
        section TEXT,
        total INTEGER,
        correct INTEGER,
        wrong INTEGER,
        percent INTEGER
    );
    """)
    conn.commit()
    conn.close()