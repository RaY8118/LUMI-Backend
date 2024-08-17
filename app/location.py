from flask import jsonify
from app import mongo

location_collection = mongo.db.location

def save_location(request):
    data = request.json
    user_id = data.get('userId')
    coords = data.get('coords')

    if not user_id or not coords:
        return jsonify({"status": "error", "message": "User ID and location data are required"}), 400

    latitude = coords.get('latitude')
    longitude = coords.get('longitude')

    if latitude is None or longitude is None:
        return jsonify({"status": "error", "message": "Latitude and Longitude are required"}), 400

    # Prepare the new location data
    new_location = {
        "userId": user_id,
        "latitude": latitude,
        "longitude": longitude,
        "latitudeDelta": 0.0922,
        "longitudeDelta": 0.0421,
    }

    # Check if the user already has a location entry
    existing_location = location_collection.find_one({"userId": user_id})
    
    if existing_location:
        # Update the existing document
        location_collection.update_one(
            {"userId": user_id},  # Filter
            {"$set": new_location}  # Update
        )
    else:
        # Insert a new document
        location_collection.insert_one(new_location)

    return jsonify({"status": "success", "message": "Location saved successfully"}), 201
