from flask import Flask
from config.config import Config
from dotenv import load_dotenv
import os
from flask_socketio import SocketIO
from flask_session import Session

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager

# Set up extensions
bcrypt = Bcrypt(app)
CORS(app)  # Enable CORS for all routes
mongo = PyMongo(app)
jwt = JWTManager(app)

app.config["SESSION_TYPE"] = "mongodb"
app.config["SESSION_MONGODB"] = mongo.cx
app.config["SESSION_MONGODB_DB"] = "chat_app"
app.config["SESSION_MONGODB_COLLECT"] = "sessions"
app.config["SESSION_PERMANENT"] = False

socketio = SocketIO(app, cors_allowed_origins="*")

# Ensure the upload folder exists
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# Import routes
from app import routes
