import os
import pickle

import cv2
import face_recognition
import numpy as np
import PIL.Image
from flask import current_app as app
from google import genai
from google.genai import types
from ultralytics import YOLO

from app import mongo

# Load the YOLO model
model = YOLO("model/yolov10b.pt")
user_collection = mongo.db.users
info_collection = mongo.db.infomation


def initialize_family(family_id):
    """Initialize encodings for a specific family."""
    encodng_file = f"resources/family_{family_id}_encodefile.p"

    try:
        with open(encodng_file, "rb") as file:
            global encodeListKnown, userIds
            encodeListKnown, userIds = pickle.load(file)
    except FileNotFoundError:
        print(
            f"Encoding file for family {family_id} not found, starting with an empty list"
        )
        encodeListKnown, userIds = [], []


def save_family_encodings(family_id, encodeListKnown, personIds):
    """Save encodings for a specific family"""
    encoding_file = f"resources/family_{family_id}_encodefile.p"
    with open(encoding_file, "wb") as file:
        pickle.dump([encodeListKnown, personIds], file)
    print(f"Encodings for family {family_id} saved successfully!")


def recognize_face(encoding_to_check, family_id):
    """Recognize a face for a specific family."""
    initialize_family(family_id)
    matches = face_recognition.compare_faces(encodeListKnown, encoding_to_check)
    face_distances = face_recognition.face_distance(encodeListKnown, encoding_to_check)
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

    face_locations = face_recognition.face_locations(rgb_image)  # Find face locations
    face_encodings = face_recognition.face_encodings(
        rgb_image, face_locations
    )  # Get face encodings

    print(f"Detected {len(face_locations)} faces.")  # Debugging line
    print(f"Face locations: {face_locations}")  # Debugging line
    print(f"Face encodings: {face_encodings}")  # Debugging line

    return face_locations, face_encodings, new_image


def save_profile_picture(user_id, family_id, image_file):
    """Save the user's profile picture and generate face encodings for the family"""
    # Define the directory for storing family images
    family_folder = os.path.join(app.config["UPLOAD_FOLDER"], str(family_id))

    # Create the family folder if it doesn't exists
    if not os.path.exists(family_folder):
        os.makedirs(family_folder)

    # Define the path where the profile picture will be saved
    file_path = os.path.join(family_folder, f"{user_id}.jpg")

    # Save the uploaded profile picture
    with open(file_path, "wb") as f:
        f.write(image_file.read())

    # Adjust based on your server setup
    user_collection.update_one(
        {"userId": user_id}, {"$set": {"profile_image": file_path}}
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
            "resources", f"family_{family_id}_encodefile.p"
        )

        try:
            # Load existing encodings if the file exists
            with open(family_pickle_file, "rb") as f:
                known_encodings, known_ids = pickle.load(f)
        except FileNotFoundError:
            known_encodings, known_ids = [], []

        # Append the new encodings and user ID to the lists
        known_encodings.append(encodings[0])
        known_ids.append(user_id)

        # Save the updated encodings and IDs back to the family pickle file
        with open(family_pickle_file, "wb") as f:
            pickle.dump([known_encodings, known_ids], f)

        print(f"Profile picture saved for user {user_id} in family {family_id}.")

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
            "Error decoding the image. Unsupported or invalid image format."
        )

    # Predict objects in the image using YOLO
    results = model.predict(image)

    # Extract detected objects' names
    detected_objects = [model.names[int(box.cls)] for box in results[0].boxes]
    unique_detected_objects = list(set(detected_objects))

    return unique_detected_objects


def gemini_detection(image_file):
    """Detect objects in an image using the gemini 2.0 model"""
    # Open the image using Pillow lib
    image = PIL.Image.open(image_file)

    if image is None:
        raise ValueError(
            "Error decoding the image. Unsupported or invalid image format."
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("API key is missing. Checking your .env file.")

    # Send request to gemini 2.0 api endpoint
    client = genai.Client(api_key=api_key)
    prompt = "Just state the object name dont form any sentence"
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[image, prompt],
    )

    # Extract detected objects from the response
    detected_objects = response.text
    unique_detected_objects = list(detected_objects.split(" "))

    return unique_detected_objects
