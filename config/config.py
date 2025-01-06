import os
import pyrebase


class Config:
    # General app settings
    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    DEBUG = os.getenv("DEBUG", "False") == "True"

    # Firebase settings
    FIREBASE_API_KEY = os.getenv("API_KEY")
    FIREBASE_AUTH_DOMAIN = os.getenv("AUTH_DOMAIN")
    FIREBASE_PROJECT_ID = os.getenv("PROJECTID")
    FIREBASE_DATABASE_URL = os.getenv("DATABASEURL")
    FIREBASE_STORAGE_BUCKET = os.getenv("STORAGEBUCKET")
    FIREBASE_MESSAGING_SENDER_ID = os.getenv("MESSAGINGSENDERID")
    FIREBASE_APP_ID = os.getenv("APPID")

    # Initialize Firebase app
    @classmethod
    def init_firebase(cls):
        firebase_config = {
            "apiKey": cls.FIREBASE_API_KEY,
            "authDomain": cls.FIREBASE_AUTH_DOMAIN,
            "projectId": cls.FIREBASE_PROJECT_ID,
            "databaseURL": cls.FIREBASE_DATABASE_URL,
            "storageBucket": cls.FIREBASE_STORAGE_BUCKET,
            "messagingSenderId": cls.FIREBASE_MESSAGING_SENDER_ID,
            "appId": cls.FIREBASE_APP_ID,
        }
        firebase = pyrebase.initialize_app(firebase_config)
        return firebase.auth()
