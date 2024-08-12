from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_bcrypt import Bcrypt  # Import Bcrypt from flask_bcrypt
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
client = MongoClient("mongodb://localhost:27017/")
db = client['lumi']
collection = db['users']


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('value')

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Check if user already exists
    existing_user = collection.find_one({"email": email})

    if existing_user:
        return jsonify({
            "status": "error",
            "message": "User already exists"
        }), 400  # Return a 400 Bad Request status code

    # Create a new user document
    new_user = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "role":role
    }
    collection.insert_one(new_user)

    return jsonify({
        "status": "success",
        "message": "Form submitted successfully!!"
    }), 201  # Return a 201 Created status code


@app.route("/login", methods=["GET", "POST"])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = collection.find_one({"email": email})

    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid Credentials"
        }), 401

    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({
            "status": "error",
            "message": "Invalid email or password"
        }), 401

    return jsonify({
        "status": "success",
        "message": "Login Successful"
    })


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
