from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config.from_object('app.config.Config')

# Initialize extensions
bcrypt = Bcrypt(app)
CORS(app)

# Set up database connection
mongo = PyMongo(app)

# Import routes
from app import routes
