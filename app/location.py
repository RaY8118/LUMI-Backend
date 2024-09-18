from flask import jsonify
from app import mongo
from geopy.distance import great_circle

location_collection = mongo.db.location


def save_home_location(request):
    data = request.json
    user_id = data.get('userId')
    coords = data.get('coords')

    if not user_id or not coords:
        return jsonify({"status": "error", "message": "User ID and home location data are required"}), 400

    latitude = coords.get('latitude')
    longitude = coords.get('longitude')

    if latitude is None or longitude is None:
        return jsonify({"status": "error", "message": "Latitude and Longitude are required"}), 400

    home_location = {
        "userId": user_id,
        "latitude": latitude,
        "longitude": longitude,
        "type": "home_location"
    }

    location_collection.update_one(
        {"userId": user_id, "type": "home_location"},
        {"$set": home_location},
        upsert=True
    )

    return jsonify({"status": "success", "message": "Home location saved successfully"}), 201


def find_location(request):
    try:
        data = request.json
        user_id = data.get('userId')
        coords = data.get('coords')

        if not user_id or not coords:
            return jsonify({"status": "error", "message": "User ID and current location data are required"}), 400

        latitude = coords.get('latitude')
        longitude = coords.get('longitude')

        if latitude is None or longitude is None:
            return jsonify({"status": "error", "message": "Latitude and Longitude are required"}), 400
        home_location = location_collection.find_one(
            {"userId": user_id, "type": "home_location"})

        if not home_location:
            return jsonify({"status": "error", "message": "Home location not set"}), 404
        home_latitude = home_location['latitude']
        home_longitude = home_location['longitude']
        distance = great_circle((latitude, longitude),
                                (home_latitude, home_longitude)).km
        radius = 2

        if distance > radius:
            return jsonify({"status": "warning", "message": "You are outside the safe zone!"}), 200

        return jsonify({"status": "success", "message": "You are within the safe zone"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": "Internal Server Error", "details": str(e)}), 500
