from flask import jsonify

from app import mongo

# Access the MongoDB location collection
location_collection = mongo.db.location
user_collection = mongo.db.users


def save_home_location(request):
    """Save or update the user's home location in the database."""
    data = request.json  # Get JSON data from the request
    user_id = data.get("userId")  # Extract user ID
    coords = data.get("coords")  # Extract coordinates

    if not user_id or not coords:
        return jsonify(
            {
                "status": "error",
                "message": "User ID and home location data are required",
            }
        ), 400

    latitude = coords.get("latitude")  # Extract latitude
    longitude = coords.get("longitude")  # Extract longitude

    if latitude is None or longitude is None:
        return jsonify(
            {"status": "error", "message": "Latitude and Longitude are required"}
        ), 400

    user_data = {
        "userId": user_id,
        "home_location": {"latitude": latitude, "longitude": longitude},
    }

    # Save the home location, updating if it already exists
    location_collection.update_one(
        {"userId": user_id},  # Match by userId only
        # Update or set home_location
        {"$set": {"home_location": user_data["home_location"]}},
        upsert=True,  # Create a new document if no match is found
    )
    return jsonify(
        {"status": "success", "message": "Home location saved successfully"}
    ), 201


def save_patient_home_location(request):
    """Save or update the user's home location in the database."""
    data = request.json  # Get JSON data from the request
    caregiver_id = data.get("CGId")  # Extract user ID
    patient_id = data.get("PATId")  # Extract user ID
    coords = data.get("coords")  # Extract coordinates

    if not caregiver_id or not patient_id or not coords:
        return jsonify(
            {
                "status": "error",
                "message": "Patient ID, Caregiver ID and home location data are required",
            }
        ), 400

    caregiver = user_collection.find_one({"userId": caregiver_id})
    patient = user_collection.find_one({"userId": patient_id})
    if caregiver["family_id"] != patient["family_id"]:
        return jsonify(
            {
                "status": "error",
                "message": "You don not have the permission to handle reminders for this patient",
            }
        ), 400

    latitude = coords.get("latitude")  # Extract latitude
    longitude = coords.get("longitude")  # Extract longitude

    if latitude is None or longitude is None:
        return jsonify(
            {"status": "error", "message": "Latitude and Longitude are required"}
        ), 400

    user_data = {
        "userId": patient_id,
        "home_location": {"latitude": latitude, "longitude": longitude},
    }

    # Save the home location, updating if it already exists
    location_collection.update_one(
        {"userId": patient_id},  # Match by userId only
        # Update or set home_location
        {"$set": {"home_location": user_data["home_location"]}},
        upsert=True,  # Create a new document if no match is found
    )
    return jsonify(
        {"status": "success", "message": "Home location saved successfully"}
    ), 201


def get_home_location(request):
    try:
        # Get user ID from route parameters
        userId = request.args.get("userId")

        # Retrieve the user's home location from the database
        user_data = location_collection.find_one({"userId": userId})

        if not user_data:
            return jsonify(
                {
                    "status": "error",
                    "message": "Home location not found! \n Please save your home location now!!!",
                }
            ), 404

        home_location = user_data["home_location"]
        latitude = home_location.get("latitude")
        longitude = home_location.get("longitude")

        if latitude is None or longitude is None:
            return jsonify(
                {
                    "status": "error",
                    "message": "Home location coordinates are incomplete",
                }
            ), 400

        # Return the coordinates in the response
        return jsonify(
            {
                "status": "success",
                "coords": {"latitude": latitude, "longitude": longitude},
            }
        ), 200

    except Exception as e:
        return jsonify(
            {"status": "error", "message": "Internal Server Error", "details": str(e)}
        ), 500


def save_current_location(request):
    """Save and update user's current location in the database"""
    data = request.json
    user_id = data.get("userId")
    coords = data.get("coords")

    if not user_id or not coords:
        return jsonify(
            {
                "status": "error",
                "message": "User ID and current location data is required",
            }
        ), 400

    latitude = coords.get("latitude")
    longitude = coords.get("longitude")

    if latitude is None or longitude is None:
        return jsonify(
            {"status": "success", "message": "Latitude and Longitude are required"}
        ), 400

    user_data = {"curr_location": {"latitude": latitude, "longitude": longitude}}

    location_collection.update_one(
        {"userId": user_id},
        {"$set": {"curr_location": user_data["curr_location"]}},
    )

    return jsonify(
        {"status": "success", "message": "Current location updated successfully"}
    ), 201


def get_current_location(request):
    """Get patient's current location from the database"""
    caregiver_id = request.args.get("CGId")
    patient_id = request.args.get("PATId")

    if not caregiver_id or not patient_id:
        return jsonify(
            {"status": "error", "message": "Caregiver ID and Patient ID is required"}
        ), 400

    user_data = location_collection.find_one({"userId": patient_id})

    if not user_data:
        return jsonify(
            {
                "status": "error",
                "message": "Current location not found! \n Please save your current location now!!!",
            }
        ), 404

    curr_location = user_data["curr_location"]
    latitude = curr_location.get("latitude")
    longitude = curr_location.get("longitude")

    if latitude is None or longitude is None:
        return jsonify(
            {
                "status": "error",
                "message": "Current location coordinates are incomplete",
            }
        ), 400

    # Return the coordinates in the response
    return jsonify(
        {"status": "success", "coords": {"latitude": latitude, "longitude": longitude}}
    ), 200
