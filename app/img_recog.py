import cv2
import face_recognition
import pickle
import numpy as np
import io

with open("model/Testing/face_recog/EncodeFile.p", 'rb') as file:
    encodeListKnown, studentIds = pickle.load(file)
print("File Loaded")


def recognize_face(encoding_to_check):
    matches = face_recognition.compare_faces(
        encodeListKnown, encoding_to_check)
    face_distances = face_recognition.face_distance(
        encodeListKnown, encoding_to_check)
    best_match_index = np.argmin(face_distances)

    if matches[best_match_index]:
        name = studentIds[best_match_index]
        return name
    else:
        return "Unknown"


def process_image(image_file):
    image_data = np.frombuffer(image_file.read(), np.uint8)
    new_image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    if new_image is None:
        raise ValueError("Error: Image could not be loaded.")

    rgb_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    return face_locations, face_encodings, new_image


def send_name(image_file):
    face_locations, face_encodings, new_image = process_image(image_file)
    for face_encoding in face_encodings:
        identified_name = recognize_face(face_encoding)
        return identified_name


def draw_box(image_file):
    face_locations, face_encodings, new_image = process_image(image_file)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        name = recognize_face(face_encoding)
        cv2.rectangle(new_image, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(new_image, name, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    _, img_encoded = cv2.imencode('.jpg', new_image)
    img_bytes = io.BytesIO(img_encoded.tobytes())
    return img_bytes
