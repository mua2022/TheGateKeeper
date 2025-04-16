import sqlite3
DB_PATH = 'database/attendance.db'

def determine_status(student_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status FROM attendance WHERE student_id = ? ORDER BY id DESC LIMIT 1", (student_id,))
    row = c.fetchone()
    conn.close()
    return 'login' if row is None or row[0] == 'logout' else 'logout'
