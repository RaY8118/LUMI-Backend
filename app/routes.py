from app import app
from flask import request, jsonify, send_file
from app.auth import register_user, login_user
from app.img_recog import process_image
from app.location import save_location
from app.reminder import get_reminders, post_reminders, delete_reminders, update_reminders
from PIL import Image
import io
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route("/register", methods=["POST"])
def register():
    return register_user(request)


@app.route("/login", methods=["POST"])
def login():
    return login_user(request)


def resize_image(image_file):
    image = Image.open(image_file)
    resized_image = image.resize((600, 720))
    image_stream = io.BytesIO()
    resized_image.save(image_stream, format='JPEG')
    image_stream.seek(0)

    return image_stream


@app.route("/process-image", methods=["POST"])
def process_image_route():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400

    image_file = request.files['image']
    try:
        resized_image_stream = resize_image(image_file)
        processed_image_stream = process_image(resized_image_stream)

        return send_file(processed_image_stream, mimetype='image/jpeg', as_attachment=False, download_name='processed_image.jpg')

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route("/homelocation", methods=["POST"])
def homelocation():
    return save_location(request)


@app.route("/getreminders", methods=["POST"])
def getreminders():
    return get_reminders(request)


@app.route("/postreminders", methods=["POST"])
def postreminders():
    return post_reminders(request)


@app.route("/deletereminders", methods=["POST"])
def deletereminders():
    return delete_reminders(request)


@app.route("/updatereminders", methods=["POST"])
def updatereminders():
    return update_reminders(request)


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
