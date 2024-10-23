from flask import jsonify
from app import mongo, bcrypt
from flask_jwt_extended import create_access_token
import uuid

# Access the MongoDB users collection
user_collection = mongo.db.users


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


def register_user(request):
    """Register a new user and store their information in the database."""
    data = request.json  # Get JSON data from the request
    name = data.get('name')
    email = data.get('email')
    mobile = data.get('mobile')
    password = data.get('password')
    role = data.get('value')  # Assuming role is passed as 'value'

    validation_error = validate_password(password)  # Validate the password
    if validation_error:
        return jsonify({"status": "error", "message": validation_error}), 400

    hashed_password = bcrypt.generate_password_hash(
        password).decode('utf-8')  # Hash the password
    existing_user = user_collection.find_one(
        {"email": email})  # Check if user already exists

    if existing_user:
        return jsonify({"status": "error", "message": "User already exists"}), 400

    custom_id = generate_custom_id()  # Generate a unique user ID

    # Create a new user object
    new_user = {
        "name": name,
        "email": email,
        "mobile": mobile,
        "password": hashed_password,
        "role": role,
        "userId": custom_id
    }
    # Insert the new user into the database
    user_collection.insert_one(new_user)

    return jsonify({"status": "success", "message": "User created successfully!!"}), 201


def login_user(request):
    """Authenticate a user and generate a JWT access token."""
    data = request.json  # Get JSON data from the request
    email = data.get('email')
    password = data.get('password')

    user = user_collection.find_one({"email": email})  # Find user by email

    if not user:
        return jsonify({"status": "error", "message": "Invalid Credentials"}), 401

    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    access_token = create_access_token(
        identity={"userId": user["userId"]})  # Generate access token
    return jsonify({"status": "success", "message": "Login Successful", "token": access_token})


def get_user_data(user_id):
    """Retrieve user data based on user ID."""
    userId = user_id  # Assign user ID

    if not userId:
        return None  # Return None if no user ID provided

    user = user_collection.find_one({"userId": userId})  # Find user by ID

    if not user:
        return None

    # Structure user data differently based on role
    if user["role"] == "CG":  # Caregiver role
        user_data = {
            "name": user["name"],
            "email": user["email"],
            "mobile": user["mobile"],
            "role": user["role"],
            "patients": user.get("patients", [])  # Get patients list if exists

        }
    else:  # Other roles
        user_data = {
            "name": user["name"],
            "email": user["email"],
            "mobile": user["mobile"],
            "role": user["role"],
            # Get caregivers list if exists
            "caregivers": user.get("caregivers", [])
        }

    return user_data  # Return the structured user data
