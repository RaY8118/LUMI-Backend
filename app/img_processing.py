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
    """Initialize the application, creating the upload folder and loading encodings."""
    with app.app_context():
        # Create upload folder if it doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        else:
            pass
        # Load known face encodings and IDs from file
        try:
            with open("resources/EncodeFile.p", 'rb') as file:
                global encodeListKnown, studentIds
                encodeListKnown, studentIds = pickle.load(file)
        except FileNotFoundError:
            print("EncodeFile.p not found, starting with an empty list.")


def get_images():
    """Load images from the upload folder and return them with their corresponding IDs."""
    pathlist = os.listdir(app.config['UPLOAD_FOLDER'])
    imgList = []
    personIds = []  # List to hold IDs of persons

    for path in pathlist:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], path)
        img = cv2.imread(img_path)  # Read the image

        if img is None:
            print(f"Error loading image: {img_path}")
            continue

        imgList.append(img)
        # Extract ID from the filename
        personIds.append(os.path.splitext(path)[0])

    if not imgList:
        print("No valid images loaded.")
    else:
        print(f"Loaded {len(imgList)} images successfully.")

    return imgList, personIds  # Return the list of images and their IDs


def find_encodings(imageslist):
    """Find and return face encodings for a list of images."""
    encodeList = []
    for img in imageslist:
        # Convert image to RGB format
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(
            img_rgb)  # Get face encodings
        if encodings:
            encodeList.append(encodings[0])
        else:
            print("No faces found in the image.")
    return encodeList  # Return the list of encodings


def save_encodings(encodeListKnown, personIds):
    """Save the known face encodings and IDs to a file."""
    encodeListKnownWithIds = [encodeListKnown,
                              personIds]  # Combine encodings and IDs
    with open("resources/EncodeFile.p", "wb") as file:
        pickle.dump(encodeListKnownWithIds, file)  # Save to file
    print("File saved")


def recognize_face(encoding_to_check):
    """Recognize a face given its encoding and return the corresponding name."""
    # Compare the given encoding with known encodings
    matches = face_recognition.compare_faces(
        encodeListKnown, encoding_to_check)
    face_distances = face_recognition.face_distance(
        encodeListKnown, encoding_to_check)  # Calculate distances
    # Find the index of the closest match
    best_match_index = np.argmin(face_distances)

    if matches[best_match_index]:  # Check if there's a match
        name = studentIds[best_match_index]  # Get the corresponding name
        return name
    else:
        return "Unknown"  # Return "Unknown" if no match


def process_image(image_file):
    """Process an uploaded image to detect faces and return their locations and encodings."""
    image_data = np.frombuffer(image_file.read(), np.uint8)  # Read image bytes
    # Decode image from bytes
    new_image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    if new_image is None:
        raise ValueError("Error: Image could not be loaded.")

    # Convert image to RGB for face recognition
    rgb_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(
        rgb_image)  # Find face locations
    face_encodings = face_recognition.face_encodings(
        rgb_image, face_locations)  # Get face encodings

    # Return locations, encodings, and the image
    return face_locations, face_encodings, new_image


def send_name(image_file):
    """Identify faces in an image and return the name of the first detected face."""
    face_locations, face_encodings, new_image = process_image(image_file)
    for face_encoding in face_encodings:
        identified_name = recognize_face(face_encoding)  # Recognize the face
        return identified_name  # Return the identified name


def draw_box(image_file):
    """Draw bounding boxes and names around detected faces in an image."""
    face_locations, face_encodings, new_image = process_image(image_file)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        name = recognize_face(face_encoding)
        cv2.rectangle(new_image, (left, top), (right, bottom),
                      (0, 255, 0), 2)  # Draw rectangle
        cv2.putText(new_image, name, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)  # Put name above the rectangle

    # Encode the image back to bytes
    _, img_encoded = cv2.imencode('.jpg', new_image)
    # Convert to bytes for sending
    img_bytes = io.BytesIO(img_encoded.tobytes())
    return img_bytes  # Return the processed image bytes


def object_detection(image_file):
    """Detect objects in an image using the YOLO model and return their names."""
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
