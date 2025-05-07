import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
import os
import face_recognition
import pickle
import shutil
from datetime import datetime

IMG_DIR = 'student_images'
ENCODE_FILE = 'face_recognizer/encodings.pkl'

class StudentRegistrationForm:
    def __init__(self, master, refresh_callback):
        self.top = tk.Toplevel(master)
        self.top.title("Register Student")
        self.refresh_callback = refresh_callback

        tk.Label(self.top, text="Student ID").grid(row=0, column=0, pady=5)
        self.entry_id = tk.Entry(self.top)
        self.entry_id.grid(row=0, column=1, pady=5)

        tk.Label(self.top, text="Full Name").grid(row=1, column=0, pady=5)
        self.entry_name = tk.Entry(self.top)
        self.entry_name.grid(row=1, column=1, pady=5)

        btn_frame = tk.Frame(self.top)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(btn_frame, text="📷 Capture via Camera", command=self.capture_from_camera).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📁 Upload Images", command=self.upload_images).pack(side=tk.LEFT, padx=5)

    def get_student_folder(self):
        student_id = self.entry_id.get().strip().replace('/', '_')
        name = self.entry_name.get().strip().replace('/', '_')

        if not student_id or not name:
            messagebox.showerror("Error", "Please enter both student ID and name")
            return None, None, None

        folder_name = f"{student_id}_{name}"
        folder_path = os.path.join(IMG_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return student_id, name, folder_path

    def capture_from_camera(self):
        student_id, name, folder_path = self.get_student_folder()
        if not folder_path:
            return

        self.capture_count = 0
        self.max_images = 4
        self.captured_data = []

        self.cam_window = tk.Toplevel(self.top)
        self.cam_window.title("Capture Faces")

        self.cam_label = tk.Label(self.cam_window)
        self.cam_label.pack()

        self.cam_button = tk.Button(self.cam_window, text="Capture", command=lambda: self.capture_image(student_id, name, folder_path))
        self.cam_button.pack(pady=5)

        self.video = cv2.VideoCapture(0)
        self.update_camera_frame()

    def update_camera_frame(self):
        ret, frame = self.video.read()
        if ret:
            self.current_frame = frame.copy()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(rgb, (320, 240))
            photo = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
            self.tk_image = tk.PhotoImage(master=self.cam_window, data=cv2.imencode('.png', photo)[1].tobytes())
            self.cam_label.configure(image=self.tk_image)
        if self.capture_count < self.max_images:
            self.cam_window.after(10, self.update_camera_frame)
        else:
            self.video.release()
            self.cam_window.destroy()
            self.save_encodings()

    def capture_image(self, student_id, name, folder_path):
        if self.capture_count >= self.max_images:
            return

        image = self.current_frame
        face_locations = face_recognition.face_locations(image)
        if not face_locations:
            messagebox.showwarning("No Face", "No face detected. Please try again.")
            return

        image_path = os.path.join(folder_path, f"{student_id}_{self.capture_count}.jpg")
        cv2.imwrite(image_path, image)
        self.captured_data.append((image_path, image, face_locations))
        self.capture_count += 1

        if self.capture_count == self.max_images:
            messagebox.showinfo("Done", f"Captured {self.max_images} images. Encoding and saving...")

    def upload_images(self):
        student_id, name, folder_path = self.get_student_folder()
        if not folder_path:
            return

        files = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if not files:
            return

        valid_images = []
        for i, file_path in enumerate(files):
            img = face_recognition.load_image_file(file_path)
            boxes = face_recognition.face_locations(img)
            if not boxes:
                continue
            new_path = os.path.join(folder_path, f"{student_id}_{i}.jpg")
            shutil.copy(file_path, new_path)
            valid_images.append((new_path, img, boxes))

        if not valid_images:
            messagebox.showerror("Error", "None of the selected images contained a face")
            return

        self.captured_data = valid_images
        self.save_encodings()

    def save_encodings(self):
        student_id = self.entry_id.get().strip().replace('/', '_')
        name = self.entry_name.get().strip().replace('/', '_')

        encodings_data = []
        if os.path.exists(ENCODE_FILE):
            with open(ENCODE_FILE, 'rb') as f:
                encodings_data = pickle.load(f)

        for path, image, boxes in self.captured_data:
            try:
                encoding = face_recognition.face_encodings(image, known_face_locations=boxes)[0]
                encodings_data.append({
                    'student_id': student_id,
                    'name': name,
                    'encoding': encoding
                })
            except Exception as e:
                print(f"Failed to encode {path}:", e)

        with open(ENCODE_FILE, 'wb') as f:
            pickle.dump(encodings_data, f)
        import sqlite3
        conn = sqlite3.connect("database/attendance.db")
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO students (student_id, name) VALUES (?, ?)", (student_id, name))
        conn.commit()
        conn.close()

        self.refresh_callback()
        self.top.destroy()
        messagebox.showinfo("Success", f"Registered {name} and updated encoding file.")
