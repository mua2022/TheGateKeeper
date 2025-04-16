# face_recognition/recognizer.py
import face_recognition
import numpy as np

def recognize_face(frame, known_encodings, known_ids):
    rgb_frame = frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    results = []
    for encoding, loc in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, encoding)
        face_distances = face_recognition.face_distance(known_encodings, encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            student_id = known_ids[best_match_index]
            results.append((student_id, loc))
    return results
