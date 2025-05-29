import sqlite3
from datetime import datetime

DB_PATH = 'database/attendance.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE,
            name TEXT,
            email TEXT,
            course TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            name TEXT,
            timestamp TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_attendance(student_id, name, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO attendance (student_id, name, timestamp, status) VALUES (?, ?, ?, ?)",
              (student_id, name, timestamp, status))
    conn.commit()
    conn.close()
