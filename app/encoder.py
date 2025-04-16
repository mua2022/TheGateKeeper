# face_recognition/encoder.py
import face_recognition
import os

def load_known_faces(directory="student_images"):
    known_encodings = []
    known_ids = []
    for file in os.listdir(directory):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(directory, file)
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                student_id = file.split("_")[0]
                known_ids.append(student_id)
    return known_encodings, known_ids
