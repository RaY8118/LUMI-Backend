from app import app
from flask import request, jsonify, send_file
from app.auth import register_user, login_user, get_user_data, reset_password
from app.img_processing import get_images, find_encodings, save_encodings, send_name, draw_box, object_detection
from app.location import find_location, save_home_location, get_home_location
from app.reminder import get_reminders, post_reminders, delete_reminders, update_reminders
from app.relations import add_caregiver_patient, delete_caregiver_patient
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


# Route for encoding images
@app.route("/encode-images", methods=["POST"])
def encode_images():
    imgList, personIds = get_images()

    if not imgList:
        return jsonify({"status": "error", "message": "No valid images found to encode"}), 400

    try:
        print("Finding encodings...")
        encodeListKnown = find_encodings(imgList)
        print("Encodings found:", len(encodeListKnown))

        if not encodeListKnown:
            return jsonify({"status": "error", "message": "No valid face encodings found."}), 400

        print("Saving encodings...")
        save_encodings(encodeListKnown, personIds)
    except Exception as e:
        print(f"Error during encoding or saving: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({
        "status": "success",
        "message": "Images encoded and file saved successfully",
        "encodedPersons": personIds
    }), 201


def resize_image(image_file):
    """Resize an image to a specified size."""
    image = Image.open(image_file)  # Open the image file
    resized_image = image.resize((600, 720))  # Resize the image
    image_stream = io.BytesIO()  # Create a byte stream
    # Save the resized image to the stream
    resized_image.save(image_stream, format='JPEG')
    image_stream.seek(0)  # Rewind the stream

    return image_stream  # Return the byte stream


# Route for identifying a name from an image
@app.route("/send-name", methods=["POST"])
def identify_name():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400

    image_file = request.files['image']
    try:
        # Identify the name from the image
        identified_name = send_name(image_file)
        return jsonify({'status': 'success', 'message': 'Identified successfully', 'name': identified_name})

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


# Route for drawing a box around faces in an image
@app.route("/draw-box", methods=["POST"])
def draw_box_route():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400

    image_file = request.files['image']  # Get the image file
    try:
        img_bytes = draw_box(image_file)  # Draw boxes around detected faces
        return send_file(img_bytes, mimetype='image/jpeg', as_attachment=False, download_name='annotated_image.jpg')

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


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
@app.route("/homelocation", methods=["POST"])
def homelocation():
    return save_home_location(request)


# Route for finding location
@app.route("/findlocation", methods=["POST"])
def findlocation():
    return find_location(request)


# Route for getting home location
@app.route("/gethomelocation", methods=["POST"])
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


# Route for adding a caregiver and patient relationship
@app.route("/add-caregiver-patient", methods=["POST"])
def add_caregiver_patient_route():
    try:
        response = add_caregiver_patient(request)  # Call the combined function
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to add caregiver and patient. Please try again', 'error': str(e)})

# Route for deleting a caregiver-patient relationship


@app.route("/delete-caregiver-patient", methods=["DELETE"])
def delete_caregiver_patient_route():
    try:
        # Call the function to delete the relationship
        response = delete_caregiver_patient(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to delete caregiver and patient relationship. Please try again', 'error': str(e)})


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
