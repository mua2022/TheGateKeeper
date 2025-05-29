import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import face_recognition
import numpy as np
import os
import sqlite3
from datetime import datetime
from database.db_handler import log_attendance
from face_recognizer.trainer import train_all_faces
from register_student import StudentRegistrationForm
from utils.time_utils import determine_status
from timetable_parser import get_day_schedule_for_course
import json
from timetable_parser import extract_text_from_pdf, parse_timetable_text
import threading
import pickle
import shutil
import smtplib
from email.message import EmailMessage
from utils.notification import notify_student_on_login
from report_generator import ReportGenerator
from home_dashboard import HomeDashboard
import pyttsx3 as engine

GMAIL_ADDRESS = "muaemmanuel2022@gmail.com"          # Replace with your Gmail
GMAIL_APP_PASSWORD = "zajx derh jmmz vpgu" 
IMG_DIR = 'student_images'
DB_PATH = 'database/attendance.db'
ENCODE_FILE = 'face_recognizer/encodings.pkl'
MEMO_DIR = 'memos'
TT_DIR = 'timetables'

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)
if not os.path.exists(DB_PATH):
    os.makedirs(os.path.dirname(DB_PATH))
if not os.path.exists(ENCODE_FILE):
    with open(ENCODE_FILE, 'wb') as f:
        pickle.dump([], f)
if not os.path.exists(TT_DIR):
    os.makedirs(TT_DIR)
if not os.path.exists(MEMO_DIR):
    os.makedirs(MEMO_DIR)

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI University Student Logging System")

        self.running = False
        self.encoding_file = ENCODE_FILE
        self.known_encodings, self.known_ids, self.known_labels = self.load_encodings()

        # --- Header Frame ---
        header_frame = tk.Frame(root, bg="#003366", height=50)
        header_frame.pack(fill=tk.X)

        # System Title
        tk.Label(header_frame, text="AI Student Logging System", bg="#003366", fg="white",
                font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=10, pady=10)

        # Right-aligned buttons
        btn_frame = tk.Frame(header_frame, bg="#003366")
        btn_frame.pack(side=tk.RIGHT, padx=10)

        tk.Button(btn_frame, text="❓ Support", bg="#005580", fg="white", command=lambda: messagebox.showinfo("Support", "Contact: muaemmanuel2022@gmail.com or Call: +254 758 514 602")).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="📘 User Manual", bg="#005580", fg="white", command=lambda: os.system("start https://github.com/mua2022/TheGateKeeper")).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="🏠 Home Dashboard", bg="#005580", fg="white", command=lambda: HomeDashboard(self.root)).pack(side=tk.RIGHT, padx=5)

        reg_frame = tk.LabelFrame(root, text="Control Panel")
        reg_frame.pack(side=tk.LEFT, padx=10, pady=10)

        tk.Button(reg_frame, text="📷 Start Camera", command=self.start_camera).grid(row=0, column=0, columnspan=2, pady=5)
        tk.Button(reg_frame, text="📝 Register Student", command=self.open_registration_form).grid(row=1, column=0, columnspan=2, pady=5)
        tk.Button(reg_frame, text="🧠 Train Dataset", command=self.train_dataset).grid(row=2, column=0, columnspan=2, pady=5)
        tk.Button(reg_frame, text="👨‍🎓 View Students", command=self.view_students).grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(reg_frame, text="📄 Generate Report", command=lambda: ReportGenerator(self.root)).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(reg_frame, text="📬Upload Memo", command=self.upload_memo).grid(row=5, column=0, columnspan=2, pady=5)
        tk.Button(reg_frame, text="🗓️Upload Timetable", command=self.upload_timetable_pdf).grid(row=6, column=0,columnspan=2, pady=5)
        tk.Button(reg_frame, text="❌ Exit", command=self.root.quit).grid(row=7, column=0, columnspan=2, pady=5)

        cam_frame = tk.LabelFrame(root, text="Live Camera")
        cam_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.video_label = tk.Label(cam_frame)
        self.video_label.pack()

        self.log_text = tk.Text(cam_frame, height=10, width=50)
        self.log_text.pack(pady=10)

        self.thread = threading.Thread(target=self.recognize_faces, daemon=True)
        self.thread.start()

        self.progress = ttk.Progressbar(reg_frame, mode='indeterminate')

    def open_registration_form(self):
        StudentRegistrationForm(self.root, self.auto_train_after_register)

    def auto_train_after_register(self):
        self.train_dataset()

    def train_dataset(self):
        self.progress.grid(row=7, column=0, columnspan=2, pady=5)
        self.progress.start()
        self.root.update_idletasks()
        train_all_faces()
        self.known_encodings, self.known_ids, self.known_labels = self.load_encodings()
        self.progress.stop()
        self.progress.grid_remove()
        messagebox.showinfo("Training Complete", "All faces have been trained and encodings saved.")

    def load_encodings(self):
        if not os.path.exists(ENCODE_FILE):
            return [], [], []
        with open(ENCODE_FILE, 'rb') as f:
            data = pickle.load(f)
        encodings = [item['encoding'] for item in data]
        ids = [item['student_id'] for item in data]
        names = [item['name'] for item in data]
        return encodings, ids, names

    def upload_memo(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        dest_path = os.path.join(MEMO_DIR, os.path.basename(file_path))
        shutil.copy(file_path, dest_path)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT email FROM students")
        emails = [row[0] for row in c.fetchall() if row[0]]
        conn.close()

        for email in emails:
            try:
                msg = EmailMessage()
                msg['Subject'] = 'New University Memo'
                msg['From'] = GMAIL_ADDRESS
                msg['To'] = email
                msg.set_content('Dear student,\n\nPlease find the attached university memo.\n\nRegards,\nUniversity Admin')

                with open(dest_path, 'rb') as f:
                    file_data = f.read()
                    msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=os.path.basename(file_path))

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
                    smtp.send_message(msg)

            except Exception as e:
                print(f"❌ Failed to send memo to {email}: {e}")

        messagebox.showinfo("Success", f"📨 Memo uploaded and sent to {len(emails)} students.")

    def upload_timetable_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        dest_path = os.path.join(TT_DIR, os.path.basename(file_path))
        shutil.copy(file_path, dest_path)

        raw_text = extract_text_from_pdf(dest_path)
        parse_timetable_text(raw_text)

        messagebox.showinfo("Success", "Timetable uploaded and parsed successfully.")

    def view_students(self):
        top = tk.Toplevel(self.root)
        top.title("Registered Students")

        tree = ttk.Treeview(top, columns=("ID", "Name", "Email", "Course"), show='headings')
        tree.heading("ID", text="Student ID")
        tree.heading("Name", text="Name")
        tree.heading("Email", text="Email")
        tree.heading("Course", text="Course")
        tree.pack(fill=tk.BOTH, expand=True)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT student_id, name, email, course FROM students")
        for row in c.fetchall():
            tree.insert('', tk.END, values=row)
        conn.close()

        def delete_selected():
            selected = tree.selection()
            if selected:
                item = tree.item(selected[0])
                student_id = item['values'][0]
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
                conn.commit()
                conn.close()
                tree.delete(selected[0])
                messagebox.showinfo("Deleted", f"Student {student_id} has been removed.")

        tk.Button(top, text="Delete Selected", command=delete_selected).pack(pady=5)

    def filter_logs_by_date(self):
        top = tk.Toplevel(self.root)
        top.title("Filter Logs by Date")

        tk.Label(top, text="Enter Date (YYYY-MM-DD):").pack(pady=5)
        date_entry = tk.Entry(top)
        date_entry.pack(pady=5)

        tree = ttk.Treeview(top, columns=("Student ID", "Name", "Time", "Status"), show='headings')
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill=tk.BOTH, expand=True)

        def fetch_logs():
            date_val = date_entry.get()
            if not date_val:
                messagebox.showerror("Error", "Please enter a date")
                return
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT student_id, name, timestamp, status FROM attendance WHERE date(timestamp) = ?", (date_val,))
            rows = c.fetchall()
            conn.close()
            tree.delete(*tree.get_children())
            for row in rows:
                tree.insert('', tk.END, values=row)

        tk.Button(top, text="Fetch Logs", command=fetch_logs).pack(pady=5)

    def start_camera(self):
        if not os.path.exists(self.encoding_file):
            messagebox.showwarning("Missing Encodings", "Please train the dataset first.")
            return
        with open(self.encoding_file, 'rb') as f:
            data = pickle.load(f)
            self.known_encodings = [item['encoding'] for item in data]
            self.known_labels = [item['name'] for item in data]
        self.running = True
        threading.Thread(target=self.recognize_faces).start()

    def recognize_faces(self):
        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.5)
                face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)

                name = "Unknown"
                student_id = ""
                status = ""
                color = (0, 255, 0)

                if any(matches):
                    best_match = np.argmin(face_distances)
                    if matches[best_match]:
                        student_id = self.known_ids[best_match]
                        name = self.known_labels[best_match]
                        status = determine_status(student_id)
                        log_attendance(student_id, name, status)

                        if status == "login":
                            notify_student_on_login(student_id, name)

                        color = (0, 0, 255)

                        self.log_text.insert(tk.END, f"{name} ({student_id}) - {status}\n")
                        self.log_text.see(tk.END)
                        engine.speak(f"{name} ({student_id}) has logged {status} at {datetime.now().strftime('%H:%M:%S')}")
                        engine.speak(f"The student has been recognized by the system")
                label = f"{name} ({student_id}) - {status}" if name != "Unknown" else "Unknown" 
                
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
