import smtplib
from email.mime.text import MIMEText
from .database import students_collection
from datetime import datetime

def send_exam_email(student_id):
    student = students_collection.find_one({"student_id": student_id})
    if not student:
        return "Student not found."

    sender = "youruniversity@gmail.com"
    password = "yourpassword"
    subject = "Exam Day Reminder"
    body = f"Dear {student['name']},\n\nYou have an exam today.\n\nGood luck!"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = student['email']

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, student['email'], msg.as_string())
        return "Email sent."
    except Exception as e:
        return f"Error sending email: {e}"

def check_and_notify_exam(student_id):
    student = students_collection.find_one({"student_id": student_id})
    today = datetime.now().date()
    if student and str(today) in student.get('exam_dates', []):
        return send_exam_email(student_id)
    return "No exam today."
