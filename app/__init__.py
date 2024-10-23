from flask import Flask
from config import Config
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

# Initialize image processing module if needed
from app.img_processing import initialize
with app.app_context():
    initialize() # Call any setup functions within the application context

# Import routes
from app import routes
