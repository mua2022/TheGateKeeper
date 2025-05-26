import sqlite3
from emailer import send_schedule_email 

DB_PATH = 'database/attendance.db'

def notify_student_on_login(student_id: str, name: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT email, course FROM students WHERE student_id = ?", (student_id,))
        row = c.fetchone()
        conn.close()

        if row and row[0] and row[1]:
            email, course = row
            send_schedule_email(email, name, course)
            print(f"✅ Schedule email sent to {email}")
        else:
            print(f"⚠️ Missing email or course for student {student_id}")

    except Exception as e:
        print(f"❌ Error sending schedule notification for {student_id}: {e}")
