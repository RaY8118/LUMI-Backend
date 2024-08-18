from app import app
from flask import request, jsonify, send_file
from app.auth import register_user, login_user
from app.img_recog import process_image
from app.location import save_location
from app.reminder import get_reminders, post_reminders, delete_reminders, update_reminders
from PIL import Image
import io


@app.route("/register", methods=["POST"])
def register():
    return register_user(request)


@app.route("/login", methods=["POST"])
def login():
    return login_user(request)


def resize_image(image_file):
    # Open the image using Pillow
    image = Image.open(image_file)
    # Resize the image to 640x480
    resized_image = image.resize((600, 720))

    # Save the resized image to a BytesIO stream
    image_stream = io.BytesIO()
    resized_image.save(image_stream, format='JPEG')
    image_stream.seek(0)  # Reset the stream position to the start

    return image_stream


@app.route("/process-image", methods=["POST"])
def process_image_route():
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400

    image_file = request.files['image']
    try:
        # Resize the image
        resized_image_stream = resize_image(image_file)

        # Now process the resized image (modify your process_image function as needed)
        processed_image_stream = process_image(resized_image_stream)

        # Send the processed image as a response
        return send_file(processed_image_stream, mimetype='image/jpeg', as_attachment=False, download_name='processed_image.jpg')

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route("/homelocation", methods=["POST"])
def homelocation():
    return save_location(request)


@app.route("/getreminders", methods=["GET"])
def getreminders():
    return get_reminders(request)


@app.route("/postreminders", methods=["POST"])
def postreminders():
    return post_reminders(request)


@app.route("/deletereminders", methods=["DELETE"])
def deletereminders():
    return delete_reminders(request)


@app.route("/updatereminders", methods=["POST"])
def updatereminders():
    return update_reminders(request)
