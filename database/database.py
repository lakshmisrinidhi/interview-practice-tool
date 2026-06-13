import sqlite3
import os
from datetime import datetime

DB_PATH = "database/interview.db"

def init_db():
    """Create database tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            mode TEXT,
            total_questions INTEGER,
            avg_overall REAL,
            avg_clarity REAL,
            avg_technical REAL,
            avg_communication REAL,
            avg_star REAL
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            question TEXT,
            answer TEXT,
            clarity INTEGER,
            technical_depth INTEGER,
            communication INTEGER,
            overall INTEGER,
            star_score INTEGER,
            date TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_session(mode, evaluations, star_scores):
    """Save interview session to database"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Calculate averages
    if evaluations:
        avg_overall = sum(e["overall"] for e in evaluations) / len(evaluations)
        avg_clarity = sum(e["clarity"] for e in evaluations) / len(evaluations)
        avg_technical = sum(e["technical_depth"] for e in evaluations) / len(evaluations)
        avg_communication = sum(e["communication"] for e in evaluations) / len(evaluations)
    else:
        avg_overall = avg_clarity = avg_technical = avg_communication = 0

    avg_star = sum(star_scores) / len(star_scores) if star_scores else 0

    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    c.execute('''
        INSERT INTO sessions 
        (date, mode, total_questions, avg_overall, avg_clarity, avg_technical, avg_communication, avg_star)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, mode, len(evaluations), avg_overall, avg_clarity, avg_technical, avg_communication, avg_star))
    
    conn.commit()
    conn.close()

def get_all_sessions():
    """Get all past sessions"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT * FROM sessions ORDER BY date ASC")
    sessions = c.fetchall()
    conn.close()
    
    return sessions

def get_session_count():
    """Get total number of sessions"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM sessions")
    count = c.fetchone()[0]
    conn.close()
    return count