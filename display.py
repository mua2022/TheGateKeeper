import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import face_recognition
import numpy as np
import os
import sqlite3
from database.db_handler import log_attendance
from face_recognizer.encoder import load_known_faces
from utils.time_utils import determine_status
import threading

IMG_DIR = 'student_images'
DB_PATH = 'database/attendance.db'

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")

        self.known_encodings, self.known_ids = load_known_faces()

        # Register Frame
        reg_frame = tk.LabelFrame(root, text="Register Student")
        reg_frame.pack(side=tk.LEFT, padx=10, pady=10)

        tk.Label(reg_frame, text="Student ID").grid(row=0, column=0)
        self.entry_id = tk.Entry(reg_frame)
        self.entry_id.grid(row=0, column=1)

        tk.Label(reg_frame, text="Name").grid(row=1, column=0)
        self.entry_name = tk.Entry(reg_frame)
        self.entry_name.grid(row=1, column=1)

        tk.Button(reg_frame, text="Upload Image(s)", command=self.upload_images).grid(row=2, column=0, columnspan=2, pady=5)

        # Camera Frame
        cam_frame = tk.LabelFrame(root, text="Live Camera")
        cam_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.video_label = tk.Label(cam_frame)
        self.video_label.pack()

        self.video = cv2.VideoCapture(0)
        self.update_frame()

        self.thread = threading.Thread(target=self.recognize_faces, daemon=True)
        self.thread.start()

    def upload_images(self):
        student_id = self.entry_id.get()
        name = self.entry_name.get()

        if not student_id or not name:
            messagebox.showerror("Error", "Please provide both Student ID and Name")
            return

        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        for i, file_path in enumerate(file_paths):
            ext = os.path.splitext(file_path)[1]
            filename = f"{student_id}_{name}_{i}{ext}"
            dest_path = os.path.join(IMG_DIR, filename)
            img = Image.open(file_path)
            img.save(dest_path)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO students (student_id, name) VALUES (?, ?)", (student_id, name))
        conn.commit()
        conn.close()

        self.known_encodings, self.known_ids = load_known_faces()
        messagebox.showinfo("Success", f"Uploaded {len(file_paths)} images for {name}")

    def update_frame(self):
        ret, frame = self.video.read()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        self.root.after(10, self.update_frame)

    def recognize_faces(self):
        while True:
            ret, frame = self.video.read()
            if not ret:
                continue

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
                distances = face_recognition.face_distance(self.known_encodings, face_encoding)

                best_match_index = np.argmin(distances)
                if matches[best_match_index]:
                    student_id = self.known_ids[best_match_index]

                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("SELECT name FROM students WHERE student_id = ?", (student_id,))
                    row = c.fetchone()
                    conn.close()
                    if not row:
                        continue

                    name = row[0]
                    status = determine_status(student_id)
                    log_attendance(student_id, name, status)

                    top, right, bottom, left = [v * 4 for v in face_location]
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    label = f"{name} ({student_id}) - {status}"
                    cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

