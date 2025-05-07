import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import face_recognition
import numpy as np
import os
import sqlite3
import threading
import pickle
from datetime import datetime

from database.db_handler import log_attendance
from face_recognizer.trainer import train_all_faces
from register_student import StudentRegistrationForm
from utils.time_utils import determine_status

IMG_DIR = 'student_images'
DB_PATH = 'database/attendance.db'
ENCODE_FILE = 'face_recognizer/encodings.pkl'

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI University Student Logging System")

        self.running = False
        self.known_encodings, self.known_ids, self.known_labels = self.load_encodings()

        self.create_widgets()

    def create_widgets(self):
        reg_frame = tk.LabelFrame(self.root, text="Control Panel")
        reg_frame.pack(side=tk.LEFT, padx=10, pady=10)

        tk.Button(reg_frame, text="Start Camera", command=self.start_camera).pack(fill='x', pady=3)
        tk.Button(reg_frame, text="Register Student", command=self.open_registration_form).pack(fill='x', pady=3)
        tk.Button(reg_frame, text="Train Dataset", command=self.train_dataset).pack(fill='x', pady=3)
        tk.Button(reg_frame, text="View Students", command=self.view_students).pack(fill='x', pady=3)
        tk.Button(reg_frame, text="Filter Logs by Date", command=self.filter_logs_by_date).pack(fill='x', pady=3)
        tk.Button(reg_frame, text="Exit", command=self.root.quit).pack(fill='x', pady=3)

        self.progress = ttk.Progressbar(reg_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=5)  

        cam_frame = tk.LabelFrame(self.root, text="Live Camera")
        cam_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.video_label = tk.Label(cam_frame)
        self.video_label.pack()

        self.log_text = tk.Text(cam_frame, height=10, width=50)
        self.log_text.pack(pady=10)

    def load_encodings(self):
        if not os.path.exists(ENCODE_FILE):
            return [], [], []
        with open(ENCODE_FILE, 'rb') as f:
            data = pickle.load(f)
        encodings = [item['encoding'] for item in data]
        ids = [item['student_id'] for item in data]
        names = [item['name'] for item in data]
        return encodings, ids, names

    def refresh_encodings(self):
        self.known_encodings, self.known_ids, self.known_labels = self.load_encodings()

    def open_registration_form(self):
        StudentRegistrationForm(self.root, self.auto_train_after_register)

    def auto_train_after_register(self):
        self.train_dataset()

    def train_dataset(self):
        self.progress.start()
        self.root.update_idletasks()
        train_all_faces()
        self.refresh_encodings()
        self.progress.stop()
        messagebox.showinfo("Training Complete", "All faces have been trained and encodings saved.")

    def view_students(self):
        top = tk.Toplevel(self.root)
        top.title("Registered Students")

        tree = ttk.Treeview(top, columns=("ID", "Name"), show='headings')
        tree.heading("ID", text="Student ID")
        tree.heading("Name", text="Name")
        tree.pack(fill=tk.BOTH, expand=True)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT student_id, name FROM students")
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
        if not self.known_encodings:
            messagebox.showwarning("No Encodings", "Train dataset before starting camera.")
            return
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
                        color = (0, 0, 255)

                        self.log_text.insert(tk.END, f"{name} ({student_id}) - {status}\n")
                        self.log_text.see(tk.END)

                label = f"{name} ({student_id}) - {status}" if name != "Unknown" else "Unknown"
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
