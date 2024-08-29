from flask import Flask
from config import Config
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager

bcrypt = Bcrypt(app)
CORS(app)
mongo = PyMongo(app)
jwt = JWTManager(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

from app.img_processing import initialize
with app.app_context():
    initialize()

from app import routes
