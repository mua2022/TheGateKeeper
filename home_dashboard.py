import tkinter as tk
from tkinter import scrolledtext

class HomeDashboard:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("🏠 System Overview Dashboard")
        self.top.geometry("900x600")
        self.top.configure(bg="#e0e0e0")

        header = tk.Label(
            self.top,
            text="📘 Project Summary",
            font=("Segoe UI", 22, "bold"),
            bg="#007acc",
            fg="white",
            padx=20,
            pady=10
        )
        header.pack(fill='x', pady=(10, 5))

        self.text_area = scrolledtext.ScrolledText(
            self.top,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            width=110,
            height=30,
            bg="white",
            fg="#333333",
            insertbackground="black",
            relief=tk.FLAT,
            bd=2
        )
        self.text_area.pack(padx=20, pady=10, fill='both', expand=True)

        self.insert_summary()

    def insert_summary(self):
        self.text_area.configure(state='normal')
        content = """📌 Problem Statement:
Traditional university gate logging systems are inefficient, relying on manual processes or ID cards, which are prone to fraud, delays, and inaccuracy.

✅ Proposed Solution:
An AI-powered face and voice recognition system that logs students securely and efficiently at campus entry points. It automates attendance tracking and reduces bottlenecks.

🎯 Objectives:
- Develop a face recognition system using deep learning.
- Register students with metadata including course and email.
- Send schedule reminders and memos via email.
- Parse timetable PDFs and match with student records.
- Log login/logout events automatically and securely.

🧱 System Features:
- Real-time face recognition using `face_recognition` and OpenCV.
- Timetable upload and parser that reads structured PDF data.
- Automated schedule emailing upon student login.
- GUI-based student registration and control panel.
- Report generation of logs (PDF export by ID or date).
- Secure memo broadcasting to all students.

📊 Results:
- System detects and recognizes student faces within ~1.3 seconds.
- Achieved >95% recognition accuracy with clear, consistent training data.
- Successfully parses timetables and sends schedule notifications.
- Admins can export attendance logs and view student records.

📘 Recommendations:
- Implement liveness detection to prevent photo-based spoofing.
- Extend the voice module for two-factor biometric logging.
- Add a web-based admin dashboard using Django or Flask.
- Integrate with real-time gate barrier control hardware.

This solution demonstrates how AI can automate and secure routine student interactions, paving the way for smarter academic environments.
"""
        # Insert the content
        self.text_area.insert(tk.END, content)

        # Define tags for colored headings
        headings = [
            "📌 Problem Statement:",
            "✅ Proposed Solution:",
            "🎯 Objectives:",
            "🧱 System Features:",
            "📊 Results:",
            "📘 Recommendations:"
        ]
        for heading in headings:
            start = "1.0"
            while True:
                pos = self.text_area.search(heading, start, stopindex=tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(heading)}c"
                self.text_area.tag_add("heading", pos, end)
                start = end
        self.text_area.tag_config("heading", foreground="#007acc", font=("Segoe UI", 11, "bold"))

        self.text_area.configure(state='disabled')
