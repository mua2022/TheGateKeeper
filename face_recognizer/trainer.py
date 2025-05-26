import os
import face_recognition
import pickle
import sqlite3

IMG_DIR = 'student_images'
ENCODE_FILE = 'face_recognizer/encodings.pkl'
DB_PATH = 'database/attendance.db'

def get_student_info_from_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT student_id, name FROM students")
    student_data = dict(c.fetchall())  # {student_id: name}
    conn.close()
    return student_data

def train_all_faces():
    encodings_data = []
    student_info = get_student_info_from_db()

    for folder in os.listdir(IMG_DIR):
        folder_path = os.path.join(IMG_DIR, folder)
        if not os.path.isdir(folder_path):
            continue

        # Try matching folder name to student_id
        possible_ids = list(student_info.keys())
        matched_id = next((sid for sid in possible_ids if folder.startswith(sid)), None)
        if not matched_id:
            print(f"❌ Skipping folder '{folder}' — no matching student ID in database.")
            continue

        student_name = student_info[matched_id]

        for file in os.listdir(folder_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(folder_path, file)
                image = face_recognition.load_image_file(image_path)
                boxes = face_recognition.face_locations(image)
                if not boxes:
                    print(f"⚠️ Skipping {file}: no face found.")
                    continue
                encoding = face_recognition.face_encodings(image, known_face_locations=boxes)
                if not encoding:
                    print(f"⚠️ Skipping {file}: encoding failed.")
                    continue

                encodings_data.append({
                    'student_id': matched_id,
                    'name': student_name,
                    'encoding': encoding[0]
                })

    with open(ENCODE_FILE, 'wb') as f:
        pickle.dump(encodings_data, f)

    print(f"\n✅ Trained {len(encodings_data)} faces and saved to '{ENCODE_FILE}'")

if __name__ == '__main__':
    train_all_faces()
