from flask import Flask
from config.config import Config
from dotenv import load_dotenv
import os

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
CORS(app) # Enable CORS for all routes
mongo = PyMongo(app)
jwt = JWTManager(app)

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Import routes
from app import routes
