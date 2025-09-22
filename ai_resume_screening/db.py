import sqlite3
from typing import Optional

DB_NAME = "resumes.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_name TEXT,
        raw_text TEXT,
        parsed_skills TEXT,
        parsed_experience TEXT,
        jd_id INTEGER,
        FOREIGN KEY(jd_id) REFERENCES job_descriptions(id)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        jd_id INTEGER,
        candidate_name TEXT,
        score REAL,
        FOREIGN KEY(jd_id) REFERENCES job_descriptions(id)
    )""")
    conn.commit()
    conn.close()

def insert_job(title: str, description: str) -> int:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO job_descriptions (title, description) VALUES (?, ?)", (title, description))
    conn.commit()
    job_id = cur.lastrowid
    conn.close()
    return job_id

def insert_resume(candidate_name: str, raw_text: str, skills: list[str], experience: list[str], jd_id: Optional[int] = None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO resumes (candidate_name, raw_text, parsed_skills, parsed_experience, jd_id)
        VALUES (?, ?, ?, ?, ?)
    """, (candidate_name, raw_text, ",".join(skills), ",".join(experience), jd_id))
    conn.commit()
    conn.close()

def insert_result(jd_id: int, candidate_name: str, score: float):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO results (jd_id, candidate_name, score)
        VALUES (?, ?, ?)
    """, (jd_id, candidate_name, float(score)))
    conn.commit()
    conn.close()