#trainer.py
import os
import face_recognition
import pickle

IMG_DIR = 'student_images'
ENCODE_FILE = 'face_recognizer/encodings.pkl'

def train_all_faces():
    encodings_data = []

    for folder in os.listdir(IMG_DIR):
        folder_path = os.path.join(IMG_DIR, folder)
        if not os.path.isdir(folder_path):
            continue

        try:
            student_id, name = folder.split('_', 1)
        except ValueError:
            print(f"Skipping malformed folder name: {folder}")
            continue

        for file in os.listdir(folder_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(folder_path, file)
                image = face_recognition.load_image_file(image_path)
                boxes = face_recognition.face_locations(image)
                if not boxes:
                    print(f"Skipping {file}: no face found")
                    continue
                encoding = face_recognition.face_encodings(image, known_face_locations=boxes)
                if not encoding:
                    print(f"Skipping {file}: encoding failed")
                    continue
                encodings_data.append({
                    'student_id': student_id,
                    'name': name,
                    'encoding': encoding[0]
                })

    with open(ENCODE_FILE, 'wb') as f:
        pickle.dump(encodings_data, f)

    print(f"✅ Encoded and saved {len(encodings_data)} face(s) to {ENCODE_FILE}")

if __name__ == '__main__':
    train_all_faces()
