from flask import jsonify
from app import mongo
from geopy.distance import great_circle

# Access the MongoDB location collection
location_collection = mongo.db.location


def save_home_location(request):
    """Save or update the user's home location in the database."""
    data = request.json  # Get JSON data from the request
    user_id = data.get('userId')  # Extract user ID
    coords = data.get('coords')  # Extract coordinates

    if not user_id or not coords:
        return jsonify({"status": "error", "message": "User ID and home location data are required"}), 400

    latitude = coords.get('latitude')  # Extract latitude
    longitude = coords.get('longitude')  # Extract longitude

    if latitude is None or longitude is None:
        return jsonify({"status": "error", "message": "Latitude and Longitude are required"}), 400

    home_location = {
        "userId": user_id,
        "latitude": latitude,
        "longitude": longitude,
        "type": "home_location"  # Specify the type of location
    }

    # Save the home location, updating if it already exists
    location_collection.update_one(
        {"userId": user_id, "type": "home_location"},
        {"$set": home_location},
        upsert=True  # Create a new document if no match is found
    )

    return jsonify({"status": "success", "message": "Home location saved successfully"}), 201


def get_home_location(request):
    try:
        # Get user ID from route parameters
        userId = request.args.get('userId')

        # Retrieve the user's home location from the database
        home_location = location_collection.find_one(
            {"userId": userId, "type": "home_location"}
        )

        if not home_location:
            return jsonify({"status": "error", "message": "Home location not found"}), 404

        # Return only the coordinates in the response
        return jsonify({"status": "success", "coords": {"latitude": home_location['latitude'], "longitude": home_location['longitude']}}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": "Internal Server Error", "details": str(e)}), 500
