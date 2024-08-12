from flask import jsonify
from app import db, collection, bcrypt


def register_user(request):
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    existing_user = collection.find_one({"email": email})

    if existing_user:
        return jsonify({"status": "error", "message": "User already exists"}), 400

    new_user = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": role
    }
    collection.insert_one(new_user)

    return jsonify({"status": "success", "message": "Form submitted successfully!!"}), 201


def login_user(request):
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = collection.find_one({"email": email})

    if not user:
        return jsonify({"status": "error", "message": "Invalid Credentials"}), 401

    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    user_data = {
        "name": user["name"],
        "email": user["email"],
        "role": user.get("role")
    }
    return jsonify({"status": "success", "message": "Login Successful", "user": user_data})

