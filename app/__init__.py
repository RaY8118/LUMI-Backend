import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_session import Session
from flask_socketio import SocketIO

from config.config import Config

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Set up extensions
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
mongo = PyMongo(app)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

app.config["SESSION_TYPE"] = "mongodb"
app.config["SESSION_MONGODB"] = mongo.cx
app.config["SESSION_MONGODB_DB"] = "chat_app"
app.config["SESSION_MONGODB_COLLECT"] = "sessions"
app.config["SESSION_PERMANENT"] = False

# Set up logging
app.logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)

from app.auth import auth_bp
from app.chat import chat_bp
from app.chatbot import chatbot_bp
from app.img_processing import image_bp
from app.location import location_bp
from app.notifications import notification_bp
from app.relations import family_bp
from app.reminder import reminder_bp

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(reminder_bp, url_prefix="/reminder")
app.register_blueprint(family_bp, url_prefix="/family")
app.register_blueprint(notification_bp, url_prefix="/notifications")
app.register_blueprint(location_bp, url_prefix="/location")
app.register_blueprint(chat_bp, url_prefix="/chat")
app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
app.register_blueprint(image_bp, url_prefix="/image")

# Ensure the upload folder exists
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])
