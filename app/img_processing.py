import cv2
import face_recognition
import pickle
import os
import numpy as np
import io
from flask import current_app as app
import logging
from app import mongo

from ultralytics import YOLO
# Suppress unnecessary logging from YOLO
logging.getLogger('ultralytics').setLevel(logging.CRITICAL)

# Load the YOLO model
model = YOLO("model/yolov10b.pt")
user_collection = mongo.db.users


def initialize_family(family_id):
    """Initialize encodings for a specific family."""
    encodng_file = f"resources/family_{family_id}_encodefile.p"

    try:
        with open(encodng_file, 'rb') as file:
            global encodeListKnown, userIds
            encodeListKnown, userIds = pickle.load(file)
    except FileNotFoundError:
        print(
            f"Encoding file for family {family_id} not found, starting with an empty list")
        encodeListKnown, userIds = [], []


def save_family_encodings(family_id, encodeListKnown, personIds):
    """Save encodings for a specific family"""
    encoding_file = f"resources/family_{family_id}_encodefile.p"
    with open(encoding_file, 'wb') as file:
        pickle.dump([encodeListKnown, personIds], file)
    print(f"Encodings for family {family_id} saved successfully!")


def recognize_face(encoding_to_check, family_id):
    """Recognize a face for a specific family."""
    initialize_family(family_id)
    matches = face_recognition.compare_faces(
        encodeListKnown, encoding_to_check)
    face_distances = face_recognition.face_distance(
        encodeListKnown, encoding_to_check)
    best_match_index = np.argmin(face_distances)

    if matches[best_match_index]:
        return userIds[best_match_index]
    else:
        return "Unknown"


def process_image(image_file):
    """Process an uploaded image to detect faces and return their locations and encodings."""
    image_data = np.frombuffer(image_file.read(), np.uint8)  # Read image bytes
    new_image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    if new_image is None:
        raise ValueError("Error: Image could not be loaded.")

    print(f"New Image Shape: {new_image.shape}")  # Debugging line
    print(f"Image Data Type: {new_image.dtype}")  # Debugging line

    # Convert image to RGB for face recognition
    rgb_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)

    # Check the RGB image shape
    print(f"RGB Image Shape: {rgb_image.shape}")  # Debugging line

    face_locations = face_recognition.face_locations(
        rgb_image)  # Find face locations
    face_encodings = face_recognition.face_encodings(
        rgb_image, face_locations)  # Get face encodings

    print(f"Detected {len(face_locations)} faces.")  # Debugging line
    print(f"Face locations: {face_locations}")  # Debugging line
    print(f"Face encodings: {face_encodings}")  # Debugging line

    return face_locations, face_encodings, new_image


def send_name(image_file):
    """Identify faces in an image and return the name of the first detected face."""
    face_locations, face_encodings, new_image = process_image(image_file)

    if not face_encodings:  # Check if no faces were found
        return "NO face detected"

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


def save_profile_picture(user_id, family_id, image_file):
    """Save the user's profile picture and generate face encodings for the family"""
    # Define the directory for storing family images
    family_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(family_id))

    # Create the family folder if it doesn't exists
    if not os.path.exists(family_folder):
        os.makedirs(family_folder)

    # Define the path where the profile picture will be saved
    file_path = os.path.join(family_folder, f"{user_id}.jpg")

    # Save the uploaded profile picture
    with open(file_path, 'wb') as f:
        f.write(image_file.read())

    # Adjust based on your server setup
    user_collection.update_one(
        {"userId": user_id},
        {"$set": {"profile_image": file_path}}
    )
    print(file_path)
    # Load the image and extract face encodings
    img = cv2.imread(file_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Find the face emcodings for the uploaded image
    encodings = face_recognition.face_encodings(img_rgb)

    if encodings:
        # If encodings aare found, save them in the family specific pickle file
        family_pickle_file = os.path.join(
            'resources', f"family_{family_id}_encodefile.p")

        try:
            # Load existing encodings if the file exists
            with open(family_pickle_file, 'rb') as f:
                known_encodings, known_ids = pickle.load(f)
        except FileNotFoundError:
            known_encodings, known_ids = [], []

        # Append the new encodings and user ID to the lists
        known_encodings.append(encodings[0])
        known_ids.append(user_id)

        # Save the updated encodings and IDs back to the family pickle file
        with open(family_pickle_file, 'wb') as f:
            pickle.dump([known_encodings, known_ids], f)

        print(
            f"Profile picture saved for user {user_id} in family {family_id}.")

    else:
        print(f"No face found in the profile picture for user {user_id}.")


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
    unique_detected_objects = list(set(detected_objects))

    return unique_detected_objects
