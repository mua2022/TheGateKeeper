import face_recognition
import os

def load_known_faces(directory="student_images"):
    known_encodings = []
    known_ids = []
    for file in os.listdir(directory):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(directory, file)
            image = face_recognition.load_image_file(path)
            face_locations = face_recognition.face_locations(image)
            encoding_list = face_recognition.face_encodings(image, face_locations)
            if encoding_list:
                known_encodings.append(encoding_list[0])
                student_id = file.split("_")[0]
                known_ids.append(student_id)
            else:
                print(f"⚠️ Skipped {file}: no encodable face found.")
    return known_encodings, known_ids
