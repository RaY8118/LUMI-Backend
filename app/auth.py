from flask import jsonify
from app import mongo, bcrypt
from app import jwt
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token

# TODO: add JWT authentication
user_collection = mongo.db.users


def generate_custom_id():
    prefix = "USID"
    count = user_collection.count_documents({})
    number = count + 1
    return f"{prefix}{str(number).zfill(3)}"


def register_user(request):
    data = request.json
    name = data.get('name')
    email = data.get('email')
    mobile = data.get('mobile')
    password = data.get('password')
    role = data.get('value')

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    existing_user = user_collection.find_one({"email": email})

    if existing_user:
        return jsonify({"status": "error", "message": "User already exists"}), 400

    custom_id = generate_custom_id()

    new_user = {
        "name": name,
        "email": email,
        "mobile": mobile,
        "password": hashed_password,
        "role": role,
        "userId": custom_id
    }
    user_collection.insert_one(new_user)

    return jsonify({"status": "success", "message": "Form submitted successfully!!"}), 201


def login_user(request):
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = user_collection.find_one({"email": email})

    if not user:
        return jsonify({"status": "error", "message": "Invalid Credentials"}), 401

    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    access_token = create_access_token(identity={"userId": user["userId"],
                                                 "name": user["name"],
                                                 "email": user["email"],
                                                 "mobile": user["mobile"],
                                                 "role": user["role"]})
    user_data = {
        "userId": user["userId"],
        "name": user["name"],
        "email": user["email"],
        "mobile": user["mobile"],
        "role": user["role"],
    }
    return jsonify({"status": "success", "message": "Login Successful", "user": user_data, "token": access_token})
