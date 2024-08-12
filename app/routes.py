from app import app
from flask import request, jsonify
from app.auth import register_user, login_user
from app.img_recog import process_image


@app.route("/register", methods=["POST"])
def register():
    return register_user(request)


@app.route("/login", methods=["POST"])
def login():
    return login_user(request)


@app.route("/process-image", methods=["POST"])
def process_image_route():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400

    image_file = request.files['image']
    result = process_image(image_file)
    return jsonify(result)
