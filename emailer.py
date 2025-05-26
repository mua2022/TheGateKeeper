from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

TIMETABLE_JSON = "data/timetable.json"
SENDER_EMAIL = "muaemmanuel2022@gmail.com"  # Gmail address acting as the server
APP_PASSWORD = "zajx derh jmmz vpgu"  

def load_timetable():
    if not os.path.exists(TIMETABLE_JSON):
        return {}
    with open(TIMETABLE_JSON, 'r') as f:
        return json.load(f)

def get_today_schedule(course):
    timetable = load_timetable()
    today = datetime.today().strftime("%A").lower()
    return timetable.get(course, {}).get(today, [])

def send_schedule_email(to_email, name, course):
    schedule = get_today_schedule(course)
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = 'Your Schedule for Today'

    if schedule:
        schedule_text = '\n'.join([f"{item['unit']} at {item['time']}" for item in schedule])
        body = f"Hello {name},\n\nHere is your schedule for today ({course}):\n\n{schedule_text}\n\nAll the best in your classes!"
    else:
        body = (
            f"Hello {name},\n\nYou have no scheduled classes for today ({course}).\n"
            "Feel free to explore the campus, visit the library, or participate in recreational activities."
        )

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
