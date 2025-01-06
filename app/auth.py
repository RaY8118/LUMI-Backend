import uuid
from datetime import timedelta

from flask import jsonify
from flask_jwt_extended import create_access_token

from app import bcrypt, mongo
from config.config import Config

# Access the MongoDB users collection
user_collection = mongo.db.users
families_collection = mongo.db.families
authenticate = Config.init_firebase()


def generate_custom_id():
    """Generate a unique user ID with a 'USID' prefix."""
    prefix = "USID"
    unique_id = uuid.uuid4().hex[:4]  # Generate a unique ID
    return f"{prefix}{unique_id.upper()}"  # Return the ID with prefix


def validate_password(password):
    """Validate the user's password against certain criteria."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."  # Check minimum length
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one digit."  # Check for digit
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter."  # Check for uppercase
    if not any(char.islower() for char in password):
        return "Password must contain at least one lowercase letter."  # Check for lowercase
    return None  # Return None if all checks pass


def sign_up_user(request):
    """Register a new user and store their information in the database."""
    data = request.json  # Get JSON data from the request
    name = data.get("name")
    email = data.get("email")
    mobile = data.get("mobile")
    password = data.get("password")
    role = data.get("value")  # Assuming role is passed as 'value'

    validation_error = validate_password(password)  # Validate the password
    if validation_error:
        return jsonify({"status": "error", "message": validation_error}), 400

    existing_user = user_collection.find_one(
        {"email": email}
    )  # Check if user already exists

    if existing_user:
        return jsonify({"status": "error", "message": "User already exists"}), 400

    try:
        firebase_user = authenticate.create_user_with_email_and_password(
            email, password
        )
        firebase_uid = firebase_user["localId"]

        custom_id = generate_custom_id()

        new_user = {
            "name": name,
            "email": email,
            "mobile": mobile,
            "password": bcrypt.generate_password_hash(password).decode("utf-8"),
            "role": role,
            "userId": custom_id,
            "firebase_uid": firebase_uid,
            "family_id": None,
            "profile_image": None,
        }
        user_collection.insert_one(new_user)

        return jsonify(
            {"status": "success", "message": "User created successfully!!"}
        ), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


def sign_in_user(request):
    """Authenticate a user and generate a JWT access token."""
    data = request.json  # Get JSON data from the request
    email = data.get("email")
    password = data.get("password")

    try:
        firebase_user = authenticate.sign_in_with_email_and_password(email, password)
        firebase_uid = firebase_user["localId"]

        user = user_collection.find_one({"firebase_uid": firebase_uid})
        if not user:
            return jsonify(
                {"status": "error", "message": "User not found in database"}
            ), 404

        access_token = create_access_token(
            identity={"userId": user["userId"]}, expires_delta=timedelta(weeks=1)
        )
        return jsonify(
            {"status": "success", "message": "Login Successful", "token": access_token}
        )

    except Exception as e:
        # Handle the error by checking for INVALID_LOGIN_CREDENTIALS specifically
        error_message = str(e)

        # Check if the error message contains "INVALID_LOGIN_CREDENTIALS"
        if "INVALID_LOGIN_CREDENTIALS" in error_message:
            return jsonify(
                {"status": "error", "message": "Invalid email or password"}
            ), 401

        # For any other errors, return a generic error message
        return jsonify(
            {"status": "error", "message": "Authentication failed. Please try again."}
        ), 401


def get_user_data(user_id):
    """Retrieve user data based on user ID."""
    userId = user_id  # Assign user ID

    if not userId:
        return None  # Return None if no user ID provided

    user = user_collection.find_one({"userId": userId})  # Find user by ID
    if not user:
        return None
    family = families_collection.find_one({"family_id": user["family_id"]})
    members_details = []
    patient_details = []
    if family and "members" in family:
        members_ids = family["members"]
        members_details = list(
            user_collection.find(
                {"userId": {"$in": members_ids}},
                {"_id": 0, "userId": 1, "name": 1},  # Project only necessary fields
            )
        )

    if family and "patient" in family:
        patient_id = family["patient"]
        patient_details = list(
            user_collection.find(
                {"userId": patient_id},
                {"_id": 0, "userId": 1, "name": 1},  # Project only necessary fields
            )
        )

    user_data = {
        "userId": user["userId"],
        "name": user["name"],
        "email": user["email"],
        "mobile": user["mobile"],
        "role": user["role"],
        "familyId": user["family_id"],
        "patient": patient_details,
        "members": members_details,
    }
    return user_data  # Return the structured user data


def reset_password(request):
    """Send a password reset email"""
    email = request.json.get("email")

    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400

    try:
        authenticate.send_password_reset_email(email)
        return jsonify(
            {"status": "success", "message": "Password reset email sent successfully"}
        ), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
