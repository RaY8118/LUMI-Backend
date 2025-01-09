from flask import jsonify

from app import mongo

user_collection = mongo.db.users


def updatePersonalInfo(request):
    data = request.json

    user_id = data.get("userId")

    if not user_id:
        return jsonify({"status": "error", "message": "User Id is required!"}), 400

    update_data = {"name": data.get("name"), "mobile": data.get("mobile")}

    update_data = {k: v for k, v in update_data.items() if v is not None}

    if not update_data:
        return jsonify({"status": "error", "message": "No valid fields to update"}), 400

    result = user_collection.update_one({"userId": user_id}, {"$set": update_data})

    if result.matched_count == 0:
        return jsonify({"status": "error", "message": "User not found"}), 404

    if result.modified_count == 0:
        return jsonify(
            {"status": "success", "message": "User found, but no changes were made"}
        ), 200
    return jsonify(
        {"status": "success", "message": "User info updated successfully"}
    ), 200
