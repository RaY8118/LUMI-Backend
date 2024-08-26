from flask import jsonify
from app import mongo, bcrypt
from flask_jwt_extended import create_access_token
import uuid

user_collection = mongo.db.users


def generate_custom_id():
    prefix = "USID"
    unique_id = uuid.uuid4().hex[:4]
    return f"{prefix}{unique_id.upper()}"


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

    return jsonify({"status": "success", "message": "User created successfully!!"}), 201


def login_user(request):
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = user_collection.find_one({"email": email})

    if not user:
        return jsonify({"status": "error", "message": "Invalid Credentials"}), 401

    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    access_token = create_access_token(identity={"userId": user["userId"]})
    return jsonify({"status": "success", "message": "Login Successful", "token": access_token})


def get_user_data(user_id):
    userId = user_id

    if not userId:
        return None

    user = user_collection.find_one({"userId": userId})

    if not user:
        return None

    if user["role"] == "CG":
        user_data = {
            "name": user["name"],
            "email": user["email"],
            "mobile": user["mobile"],
            "role": user["role"]
        }
    else:
        user_data = {
            "name": user["name"],
            "email": user["email"],
            "mobile": user["mobile"],
            "role": user["role"],
            "caregivers": user.get("caregivers", [])
        }

    return user_data
