from app import app
from flask import request, jsonify, send_file
from app.auth import register_user, login_user, get_user_data
from app.img_processing import get_images, find_encodings, save_encodings, send_name, draw_box
from app.location import find_location, save_home_location
from app.reminder import get_reminders, post_reminders, delete_reminders, update_reminders, post_reminders_for_patients, get_reminders_for_patient, delete_reminders_for_patient, update_reminders_for_patient
from app.relations import add_caregiver, delete_caregiver
from PIL import Image
import io
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route("/register", methods=["POST"])
def register():
    try:
        response = register_user(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Registration failed, please try again'})


@app.route("/login", methods=["POST"])
def login():
    try:
        respone = login_user(request)
        return respone
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Login failed, please try again'})


@app.route("/encode-images", methods=["POST"])
def encode_images():
    imgList, personIds = get_images()

    if not imgList:
        return jsonify({"status": "error", "message": "No valid images found to encode"}), 400

    encodeListKnown = find_encodings(imgList)
    save_encodings(encodeListKnown, personIds)

    return jsonify({
        "status": "success",
        "message": "Images encoded and file saved successfully",
        "encodedPersons": personIds
    }), 201


def resize_image(image_file):
    image = Image.open(image_file)
    resized_image = image.resize((600, 720))
    image_stream = io.BytesIO()
    resized_image.save(image_stream, format='JPEG')
    image_stream.seek(0)

    return image_stream


@app.route("/send-name", methods=["POST"])
def identify_name():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400

    image_file = request.files['image']
    try:
        identified_name = send_name(image_file)
        return jsonify({'status': 'success', 'message': 'Identified successfully', 'name': identified_name})

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route("/draw-box", methods=["POST"])
def draw_box_route():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400

    image_file = request.files['image']
    try:
        img_bytes = draw_box(image_file)
        return send_file(img_bytes, mimetype='image/jpeg', as_attachment=False, download_name='annotated_image.jpg')

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route("/homelocation", methods=["POST"])
def homelocation():
    return save_home_location(request)


@app.route("/findlocation", methods=["POST"])
def findlocation():
    return find_location(request)


@app.route("/getreminders", methods=["POST"])
def getreminders():
    try:
        response = get_reminders(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to retrieve reminders. Please try again', 'error': str(e)})


@app.route("/postreminders", methods=["POST"])
def postreminders():
    try:
        response = post_reminders(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to post reminders. Please try again', 'error': str(e)})


@app.route("/deletereminders", methods=["POST"])
def deletereminders():
    try:
        response = delete_reminders(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to delete reminders. Please try again', 'error': str(e)})


@app.route("/updatereminders", methods=["POST"])
def updatereminders():
    try:
        response = update_reminders(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to update reminders. Please try again', 'error': str(e)})


@app.route("/add-caregiver", methods=["POST"])
def addcaregivers():
    try:
        response = add_caregiver(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to delete reminders. Please try again', 'error': str(e)})


@app.route("/delete-caregiver", methods=["POST"])
def deletecaregivers():
    try:
        response = delete_caregiver(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to delete reminders. Please try again', 'error': str(e)})


@app.route('/get-userdata', methods=['POST'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    user_id = current_user.get('userId')

    if user_id:
        user_data = get_user_data(user_id)

        if user_data:
            return jsonify({"status": "success", "userData": user_data}), 200
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404
    else:
        return jsonify({"status": "error", "message": "Invalid token data"}), 401


@app.route('/caregiver/reminders', methods=['POST'])
def caregiver_add_reminder():
    try:
        response = post_reminders_for_patients(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to add reminders. Please try again', 'error': str(e)})


@app.route('/caregiver/reminders', methods=['GET'])
def caregiver_get_reminder():
    try:
        response = get_reminders_for_patient(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to get reminders. Please try again', 'error': str(e)})


@app.route('/caregiver/reminders', methods=['DELETE'])
def caregiver_delete_reminder():
    try:
        response = delete_reminders_for_patient(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to delete reminders. Please try again', 'error': str(e)})


@app.route('/caregiver/reminders', methods=['PUT'])
def caregiver_update_reminder():
    try:
        response = update_reminders_for_patient(request)
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to update reminders. Please try again', 'error': str(e)})
