from datetime import datetime
import fitz # PyMuPDF
import os
import re
import json
import tkinter as tk
from tkinter import filedialog, messagebox

TIMETABLE_FOLDER = "timetables"
TIMETABLE_JSON = os.path.join(TIMETABLE_FOLDER, "parsed_timetable.json")

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
        return text

def parse_timetable_text(raw_text):
    timetable_data = {}
    current_day = None
    current_course = None
    # This regex finds course-like headers and time/unit info
    day_pattern = re.compile(r'\b(Monday|Tuesday|Wednesday|Thursday|Friday)\b', re.IGNORECASE)
    course_pattern = re.compile(r'\b(bsey|bcsy|bity)\d+s\d+\b', re.IGNORECASE)

    lines = raw_text.splitlines()
    for line in lines:
        day_match = day_pattern.search(line)
        if day_match:
            current_day = day_match.group(0).capitalize()
            if current_day not in timetable_data:
                timetable_data[current_day] = {}
            continue

        course_match = course_pattern.search(line)
        if course_match:
            current_course = course_match.group(0).lower()
            if current_day and current_course:
                timetable_data[current_day][current_course] = []
            continue

        if current_day and current_course:
            if line.strip():
                timetable_data[current_day][current_course].append(line.strip())

    with open(TIMETABLE_JSON, "w") as f:
        json.dump(timetable_data, f, indent=4)

    return timetable_data
def get_day_schedule_for_course(course, date=None):
    if not os.path.exists(TIMETABLE_JSON):
        return []
    with open(TIMETABLE_JSON, "r") as f:
        timetable_data = json.load(f)

    if not date:
        date = datetime.today()

    day = date.strftime("%A")
    return timetable_data.get(day, {}).get(course.lower(), [])
def upload_timetable_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    if not os.path.exists(TIMETABLE_FOLDER):
        os.makedirs(TIMETABLE_FOLDER)

    dest_path = os.path.join(TIMETABLE_FOLDER, os.path.basename(file_path))
    with open(file_path, 'rb') as fsrc, open(dest_path, 'wb') as fdst:
        fdst.write(fsrc.read())

    raw_text = extract_text_from_pdf(dest_path)
    parse_timetable_text(raw_text)
    messagebox.showinfo("Success", "Timetable uploaded and parsed successfully.")
def view_timetable():
    if not os.path.exists(TIMETABLE_JSON):
        messagebox.showerror("Error", "No timetable data found.")
        return

    with open(TIMETABLE_JSON, "r") as f:
        timetable_data = json.load(f)

    top = tk.Toplevel()
    top.title("Timetable")

    for day, courses in timetable_data.items():
        day_label = tk.Label(top, text=day, font=("Arial", 16, "bold"))
        day_label.pack(pady=5)

        for course, details in courses.items():
            course_label = tk.Label(top, text=f"{course}: {', '.join(details)}")
            course_label.pack(anchor="w", padx=20)

            separator = tk.Frame(top, height=2, bd=1, relief=tk.SUNKEN)
            separator.pack(fill=tk.X, padx=10, pady=5)
