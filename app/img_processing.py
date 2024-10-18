import cv2
import face_recognition
import pickle
import os
import numpy as np
import io
from flask import current_app as app
import logging

from ultralytics import YOLO
# Suppress unnecessary logging from YOLO
logging.getLogger('ultralytics').setLevel(logging.CRITICAL)

# Load the YOLO model
model = YOLO("../model/yolov8n.pt")


def initialize():
    with app.app_context():
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        else:
            pass

        try:
            with open("resources/EncodeFile.p", 'rb') as file:
                global encodeListKnown, studentIds
                encodeListKnown, studentIds = pickle.load(file)
        except FileNotFoundError:
            print("EncodeFile.p not found, starting with an empty list.")


def get_images():
    pathlist = os.listdir(app.config['UPLOAD_FOLDER'])
    imgList = []
    personIds = []

    for path in pathlist:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], path)
        img = cv2.imread(img_path)

        if img is None:
            print(f"Error loading image: {img_path}")
            continue

        imgList.append(img)
        personIds.append(os.path.splitext(path)[0])

    if not imgList:
        print("No valid images loaded.")
    else:
        print(f"Loaded {len(imgList)} images successfully.")

    return imgList, personIds


def find_encodings(imageslist):
    encodeList = []
    for img in imageslist:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img_rgb)
        if encodings:
            encodeList.append(encodings[0])
        else:
            print("No faces found in the image.")
    return encodeList


def save_encodings(encodeListKnown, personIds):
    encodeListKnownWithIds = [encodeListKnown, personIds]
    with open("resources/EncodeFile.p", "wb") as file:
        pickle.dump(encodeListKnownWithIds, file)
    print("File saved")


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


def object_detection(image_file):
    # Convert the image file (bytes) to a NumPy array
    image_bytes = np.frombuffer(image_file.read(), np.uint8)

    # Decode image from bytes using OpenCV
    image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

    # Check if image was properly decoded
    if image is None:
        raise ValueError(
            "Error decoding the image. Unsupported or invalid image format.")

    # Predict objects in the image using YOLO
    results = model.predict(image)

    # Extract detected objects' names
    detected_objects = [model.names[int(box.cls)] for box in results[0].boxes]
    # detected_objects = set(detected_objects)
    return detected_objects
