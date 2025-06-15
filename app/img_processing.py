import os
import pickle

import cv2
import face_recognition
import numpy as np
import PIL.Image
from flask import Blueprint
from flask import current_app as App
from flask import jsonify, request
from google import genai
from google.genai import types
from ultralytics import YOLO

from app import mongo

# Load the YOLO model
image_bp = Blueprint("image", __name__)
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
    print(f"RGB Image Shape: {rgb_image.shape}")

    face_locations = face_recognition.face_locations(rgb_image)  # Find face locations
    face_encodings = face_recognition.face_encodings(
        rgb_image, face_locations
    )  # Get face encodings

    print(f"Detected {len(face_locations)} faces.")
    print(f"Face locations: {face_locations}")
    print(f"Face encodings: {face_encodings}")

    return face_locations, face_encodings, new_image


@image_bp.route("/detect_faces/<family_id>", methods=["POST"])
def detect_faces_route(family_id):
    """Detect faces in the uploaded image and recognize them."""
    try:
        image_file = request.files["image"]
        face_locations, face_encodings, new_image = process_image(image_file)

        if not image_file:
            return jsonify({"status": "error", "message": "No image provided."}), 400
        if not face_encodings:  # If no faces were found
            return jsonify({"status": "success", "message": "No faces found."}), 200

        # Recognize each face
        recognized_faces = []
        for face_encoding in face_encodings:
            recognized_name = recognize_face(face_encoding, family_id)
            recognized_faces.append(recognized_name)
            print(recognized_faces)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Identified person",
                    "name": recognized_faces,
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "An error occured while identifying the person",
                    "error": str(e),
                }
            ),
            400,
        )


@image_bp.route("/save_profile_picture/<user_id>/<family_id>", methods=["POST"])
def save_profile_picture(user_id, family_id):
    """Save the user's profile picture and generate face encodings for the family"""
    # Define the directory for storing family images
    try:
        if "image" not in request.files:
            return (
                jsonify({"status": "error", "message": "No image file provided"}),
                400,
            )
        image_file = request.files["image"]

        family_folder = os.path.join(App.config["UPLOAD_FOLDER"], str(family_id))

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

            return (
                jsonify(
                    {
                        "status": "success",
                        "message": f"Profile picture for user {user_id} saved in family {family_id}.",
                    }
                ),
                200,
            )

        else:
            print(f"No face found in the profile picture for user {user_id}.")

            return (
                jsonify(
                    {
                        "status": "success",
                        "message": f"No face found in the profile picture for user {user_id}.",
                    }
                ),
                200,
            )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "An error occured while saving the profile picture",
                    "error": str(e),
                }
            ),
            500,
        )


@image_bp.route("/detect_object", methods=["POST"])
def detect_objects():
    """Try YOLO detection first, fallback to Gemini if YOLO detects nothing."""
    try:
        if "image" not in request.files:
            return jsonify({"status": "error", "message": "No image provided"}), 400

        image_file = request.files["image"]

        image_bytes = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Invalid image format.")

        results = model.predict(image)
        yolo_detected = [model.names[int(box.cls)] for box in results[0].boxes]
        unique_yolo = list(set(yolo_detected))

        if unique_yolo:
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": "Identified by YOLO",
                        "name": unique_yolo,
                    }
                ),
                200,
            )

        image_file.stream.seek(0)
        pil_image = PIL.Image.open(image_file)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing in the environment.")

        client = genai.Client(api_key=api_key)
        prompt = "Just state the object name, do not form any sentence."
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL"),
            contents=[pil_image, prompt],
        )

        gemini_detected = response.text.strip().split(" ")
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Identified by Gemini",
                    "name": gemini_detected,
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
