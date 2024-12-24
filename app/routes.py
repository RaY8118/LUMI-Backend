from app import app
from flask import request, jsonify, send_file
from app.auth import register_user, login_user, get_user_data, reset_password
from app.img_processing import initialize_family, save_family_encodings, recognize_face, save_profile_picture, send_name, process_image, object_detection, draw_box
from app.location import save_home_location, get_home_location
from app.reminder import get_reminders, post_reminders, delete_reminders, update_reminders
from app.relations import create_family, add_user_to_family
from PIL import Image
import io
from flask_jwt_extended import jwt_required, get_jwt_identity


# Route for user registration
@app.route("/register", methods=["POST"])
def register():
    try:
        response = register_user(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Registration failed, please try again'})


# Route for user login
@app.route("/login", methods=["POST"])
def login():
    try:
        response = login_user(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Login failed, please try again'})


# Route for reseting password
@app.route("/reset-password", methods={"POST"})
def password_reset():
    try:
        response = reset_password(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Password reset failed, please try again'})


def resize_image(image_file):
    """Resize an image to a specified size."""
    image = Image.open(image_file)  # Open the image file
    resized_image = image.resize((600, 720))  # Resize the image
    image_stream = io.BytesIO()  # Create a byte stream
    # Save the resized image to the stream
    resized_image.save(image_stream, format='JPEG')
    image_stream.seek(0)  # Rewind the stream

    return image_stream  # Return the byte stream


# Route for object detection in images
@app.route("/obj-detection", methods=["POST"])
def obj_detection():
    if 'image' not in request.files:
        # Check if the image is in the request
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400

    image_file = request.files['image']

    try:
        identified_objects = object_detection(
            image_file)  # Perform object detection
        # Return identified objects
        return jsonify({'status': 'success', 'message': 'Identified successfully', 'name': identified_objects})

    except ValueError as e:
        # Return error response if something goes wrong
        return jsonify({'status': 'error', 'message': str(e)}), 400


# Route for saving home location
@app.route("/safe-location", methods=["POST"])
def homelocation():
    return save_home_location(request)


# Route for getting home location
@app.route("/safe-location", methods=["GET"])
def gethomelocation():
    return get_home_location(request)


# Route for getting reminders
@app.route("/reminders", methods=["GET"])
def getreminders():
    try:
        response = get_reminders(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to retrieve reminders. Please try again', 'error': str(e)})


# Route for posting reminders
@app.route("/reminders", methods=["POST"])
def postreminders():
    try:
        response = post_reminders(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to post reminders. Please try again', 'error': str(e)})


# Route for deleting reminders
@app.route("/reminders/<reminderId>", methods=["DELETE"])
def deletereminders(reminderId):
    try:
        response = delete_reminders(reminderId)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to delete reminders. Please try again', 'error': str(e)})


# Route for updating reminders
@app.route("/reminders", methods=["PUT"])
def updatereminders():
    try:
        response = update_reminders(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to update reminders. Please try again', 'error': str(e)})


# Route for getting user data with JWT protection
@app.route('/get-userdata', methods=['POST'])
@jwt_required()  # Protect this route with JWT
def protected():
    current_user = get_jwt_identity()  # Get the current user's identity
    user_id = current_user.get('userId')

    if user_id:
        user_data = get_user_data(user_id)

        if user_data:
            return jsonify({"status": "success", "userData": user_data}), 200
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404
    else:
        return jsonify({"status": "error", "message": "Invalid token data"}), 401


# Route to create new family
@app.route("/family", methods=["POST"])
def create_family_route():
    try:
        # Call the function to delete the relationship
        response = create_family(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to create family. Please try again', 'error': str(e)}), 500


# Route to add user to family
@app.route("/family/add_user", methods=["POST"])
def add_user_to_family_route():
    try:
        # Call the add_user_to_family function
        response = add_user_to_family(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to add user to family. Please try again', 'error': str(e)}), 500


@app.route('/save_profile_picture/<user_id>/<family_id>', methods=['POST'])
def save_profile_picture_route(user_id, family_id):
    """Save the profile picture for a user and update the encodings."""
    image_file = request.files['image']
    save_profile_picture(user_id, family_id, image_file)
    return jsonify({"message": f"Profile picture for user {user_id} saved in family {family_id}."}), 200


@app.route('/detect_faces/<family_id>', methods=['POST'])
def detect_faces_route(family_id):
    """Detect faces in the uploaded image and recognize them."""
    image_file = request.files['image']
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

    return jsonify({"status": "success", "message": "Identified person", "name": recognized_faces}), 200
