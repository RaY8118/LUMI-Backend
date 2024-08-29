# config.py

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/lumi')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'model/Testing/faceRecog/images')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
