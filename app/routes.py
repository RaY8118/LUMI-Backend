from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import app
from app.auth import get_user_data, reset_password, sign_in_user, sign_up_user
from app.img_processing import (
    object_detection,
    process_image,
    recognize_face,
    save_profile_picture,
)
from app.location import (
    get_current_location,
    get_home_location,
    save_current_location,
    save_home_location,
)
from app.notifications import custom_push_notification, get_user_token, store_user_token
from app.relations import (
    add_patient_to_family,
    add_user_to_family,
    create_family,
    save_additional_info,
    get_additional_info,
)
from app.reminder import (
    caregiver_delete_reminder,
    caregiver_get_reminders,
    caregiver_post_reminder,
    caregiver_update_reminder,
    patient_delete_reminder,
    patient_get_reminders,
    patient_post_reminder,
    patient_update_reminder,
)


# Route for user registration
@app.route("/sign-up", methods=["POST"])
def sign_up_route():
    try:
        response = sign_up_user(request)
        return response
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Registration failed, please try again.",
                "error": str(e),
            }
        ), 500


# Route for user login
@app.route("/sign-in", methods=["POST"])
def sign_in_route():
    try:
        response = sign_in_user(request)
        return response
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Login failed, please try again.",
                "error": str(e),
            }
        ), 500


# Route for reseting password
@app.route("/reset-password", methods={"POST"})
def password_reset_route():
    try:
        response = reset_password(request)
        return response
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Password reset failed, please try again.",
                "error": str(e),
            }
        ), 500


# Route for getting user data with JWT protection
@app.route("/get-userdata", methods=["POST"])
@jwt_required()  # Protect this route with JWT
def protected():
    current_user = get_jwt_identity()  # Get the current user's identity
    user_id = current_user.get("userId")

    if user_id:
        user_data = get_user_data(user_id)

        if user_data:
            return jsonify({"status": "success", "userData": user_data}), 200
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404
    else:
        return jsonify({"status": "error", "message": "Invalid token data"}), 401


# Route for patient to fetch reminders
@app.route("/patient/reminders", methods=["GET"])
def get_patient_reminders_route():
    try:
        return patient_get_reminders(request)
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to retrieve patient reminders. Please try again.",
                "error": str(e),
            }
        ), 500


# Route for caregiver to fetch reminders


@app.route("/caregiver/reminders", methods=["GET"])
def get_caregiver_reminders_route():
    try:
        return caregiver_get_reminders(request)
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to retrieve patient reminders. Please try again.",
                "error": str(e),
            }
        ), 500


# Route for patient to create reminders
@app.route("/patient/reminders", methods=["POST"])
def post_patient_reminders_route():
    try:
        response = patient_post_reminder(request)
        return response
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to post patients reminders. Please try again",
                "error": str(e),
            }
        ), 500


# Route for caregiver to create reminders
@app.route("/caregiver/reminders", methods=["POST"])
def post_caregiver_reminders_route():
    try:
        response = caregiver_post_reminder(request)
        return response
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to post patients reminders. Please try again",
                "error": str(e),
            }
        ), 500


# Route for patient to delete reminders


@app.route("/patient/reminders/<user_id>/<rem_id>", methods=["DELETE"])
def delete_patient_reminder_route(user_id, rem_id):
    try:
        return patient_delete_reminder(user_id, rem_id)
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to delete patient reminder. Please try again.",
                "error": str(e),
            }
        ), 500


# Route for caregiver to delete reminders


@app.route(
    "/caregiver/reminders/<caregiver_id>/<patient_id>/<rem_id>", methods=["DELETE"]
)
def delete_caregiver_reminder_route(caregiver_id, patient_id, rem_id):
    try:
        return caregiver_delete_reminder(caregiver_id, patient_id, rem_id)
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to delete caregiver reminder. Please try again.",
                "error": str(e),
            }
        ), 500


# Route for patient to update reminders
@app.route("/patient/reminders/<reminder_id>", methods=["PUT"])
def update_patient_reminder_route(reminder_id):
    try:
        return patient_update_reminder(request, reminder_id)
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to update patient reminder. Please try again.",
                "error": str(e),
            }
        ), 500


# Route for caregiver to delete reminders
@app.route("/caregiver/reminders/<reminder_id>", methods=["PUT"])
def update_caregiver_reminder_route(reminder_id):
    try:
        return caregiver_update_reminder(request, reminder_id)
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to update caregiver reminder. Please try again.",
                "error": str(e),
            }
        ), 500


# Route for saving home location
@app.route("/safe-location", methods=["POST"])
def save_home_location_route():
    return save_home_location(request)


# Route for getting home location
@app.route("/safe-location", methods=["GET"])
def get_home_location_route():
    return get_home_location(request)


# Route for saving current location
@app.route("/curr-location", methods=["POST"])
def save_curr_location_route():
    return save_current_location(request)


# Route for getting home location
@app.route("/curr-location", methods=["GET"])
def get_curr_location_route():
    return get_current_location(request)


# Route to create new family
@app.route("/family", methods=["POST"])
def create_family_route():
    try:
        # Call the function to delete the relationship
        response = create_family(request)
        return response
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to create family. Please try again.",
                "error": str(e),
            }
        ), 500


# Route to add user to family
@app.route("/family/add_user", methods=["POST"])
def add_user_to_family_route():
    try:
        # Call the add_user_to_family function
        response = add_user_to_family(request)
        return response
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to add user to family. Please try again.",
                "error": str(e),
            }
        ), 500


# Route to add user to family
@app.route("/family/add_patient", methods=["POST"])
def add_patient_to_family_route():
    try:
        # Call the add_user_to_family function
        response = add_patient_to_family(request)
        return response
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to add patient to family. Please try again.",
                "error": str(e),
            }
        ), 500


@app.route("/save_profile_picture/<user_id>/<family_id>", methods=["POST"])
def save_profile_picture_route(user_id, family_id):
    """Save the profile picture for a user and update the encodings."""
    image_file = request.files["image"]
    save_profile_picture(user_id, family_id, image_file)
    return jsonify(
        {"message": f"Profile picture for user {user_id} saved in family {family_id}."}
    ), 200


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

    return jsonify(
        {"status": "success", "message": "Identified person", "name": recognized_faces}
    ), 200


# Route for object detection in images
@app.route("/obj-detection", methods=["POST"])
def obj_detection_route():
    if "image" not in request.files:
        # Check if the image is in the request
        return jsonify({"status": "error", "message": "No image provided"}), 400

    image_file = request.files["image"]

    try:
        identified_objects = object_detection(image_file)  # Perform object detection
        # Return identified objects
        return jsonify(
            {
                "status": "success",
                "message": "Identified successfully",
                "name": identified_objects,
            }
        )

    except ValueError as e:
        # Return error response if something goes wrong
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/store-token", methods=["POST"])
def store_token():
    data = request.get_json()
    return store_user_token(data)


@app.route("/send-push-notification", methods=["POST"])
def send_push_notification():
    try:
        response = custom_push_notification(request)
        return response
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to send notification. Please try again.",
                "error": str(e),
            }
        ), 500


@app.route("/get-user-token", methods=["GET"])
def get_token():
    try:
        response = get_user_token(request)
        return response
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to get token. Please try again.",
                "error": str(e),
            }
        ), 500


@app.route("/save-additional-info", methods=["POST"])
def save_info():
    try:
        response = save_additional_info(request)
        return response
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to save info. Please try again.",
                "error": str(e),
            },
            500,
        )


@app.route("/get-additional-info", methods=["GET"])
def get_info():
    try:
        response = get_additional_info(request)
        return response
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to get info. Please try again.",
                "error": str(e),
            },
            500,
        )
