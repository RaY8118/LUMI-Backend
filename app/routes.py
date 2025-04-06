from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import app
from app.img_processing import (process_image, recognize_face,
                                save_profile_picture)


@app.route("/save_profile_picture/<user_id>/<family_id>", methods=["POST"])
def save_profile_picture_route(user_id, family_id):
    """Save the profile picture for a user and update the encodings."""
    if "image" not in request.files:
        return jsonify({"status": "error", "message": "No image file provided"}), 400
    image_file = request.files["image"]
    try:
        save_profile_picture(user_id, family_id, image_file)
        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Profile picture for user {user_id} saved in family {family_id}.",
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


@app.route("/detect_faces/<family_id>", methods=["POST"])
def detect_faces_route(family_id):
    """Detect faces in the uploaded image and recognize them."""
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
