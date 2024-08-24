from app import app
from flask import request, jsonify, send_file
from app.auth import register_user, login_user
from app.img_recog import send_name, draw_box
from app.location import save_location
from app.reminder import get_reminders, post_reminders, delete_reminders, update_reminders
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
    return save_location(request)


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


@app.route('/protected', methods=['POST'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    user_id = current_user.get('userId')
    user_role = current_user.get('role')
    name_role = current_user.get('name')
    email_role = current_user.get('email')
    mobile_role = current_user.get('mobile')

    if user_id and user_role:
        return jsonify({"status": "success", "userId": user_id, "role": user_role, "name": name_role, "email": email_role, "mobile": mobile_role}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid token data"}), 401
