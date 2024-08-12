from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
app.config.from_object('app.config.Config')

# Initialize extensions
bcrypt = Bcrypt(app)
CORS(app)

# Set up database connection
client = MongoClient(app.config['MONGO_URI'])
db = client[app.config['MONGO_DB']]
collection = db[app.config['MONGO_COLLECTION']]

# Import routes
from app import routes
