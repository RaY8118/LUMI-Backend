from flask import jsonify

from app import mongo

user_collection = mongo.db.users


def update_personal_info(request):
    data = request.json

    user_id = data.get("userId")

    if not user_id:
        return jsonify({"status": "error", "message": "User Id is required!"}), 400

    update_data = {}
    if "name" in data and data["name"]:
        update_data["name"] = data["name"]
    if "mobile" in data and data["mobile"]:
        update_data["mobile"] = data["mobile"]

    if not update_data:
        return jsonify({"status": "error", "message": "No valid fields to update"}), 400

    result = user_collection.update_one({"userId": user_id}, {"$set": update_data})

    if result.matched_count == 0:
        return jsonify({"status": "error", "message": "User not found"}), 404

    if result.modified_count == 0:
        return (
            jsonify(
                {"status": "success", "message": "User found, but no changes were made"}
            ),
            200,
        )
    return (
        jsonify({"status": "success", "message": "User info updated successfully"}),
        200,
    )
