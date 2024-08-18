from flask import jsonify
from app import mongo
from bson import ObjectId

reminders_collection = mongo.db.reminders


def post_reminders(request):
    data = request.json
    title = data.get('title')
    description = data.get('description')
    date = data.get('date')
    status = data.get('status')
    userId = data.get('userId')

    new_reminder = {
        "title": title,
        "description": description,
        "date": date,
        "status": status,
        "userId": userId
    }

    reminders_collection.insert_one(new_reminder)

    return jsonify({"status": "success", "message": "Reminder saved successfully"}), 201


def get_reminders(request):
    data = request.json
    userId = data.get('userId')

    if not userId:
        return jsonify({"status": "error", "message": "User ID is required"}), 400

    user_reminders = list(reminders_collection.find({"userId": userId}))

    if not user_reminders:
        return jsonify({"status": "error", "message": "No reminders for this user"}), 401

    reminder_list = [{
        "_id": str(r["_id"]),
        "title": r["title"],
        "description": r["description"],
        "date": r["date"],
        "status": r["status"]
    } for r in user_reminders]

    return jsonify({"status": "success", "message": "Retrieved all reminders", "reminders": reminder_list}), 200


def delete_reminders(request):
    data = request.json
    RemID = data.get('remId')

    if not RemID:
        return jsonify({"status": "error", "message": "Reminder ID is required"}), 400

    result = reminders_collection.delete_one({"_id": ObjectId(RemID)})

    if result.deleted_count == 0:
        return jsonify({"status": "error", "message": "Reminder not found"}), 404

    return jsonify({"status": "success", "message": "Reminder Deleted Successfully"}), 200


def update_reminders(request):
    data = request.json
    RemID = data.get('remId')
    update_data = {
        "title": data.get('title'),
        "description": data.get('description'),
        "date": data.get('date'),
        "status": data.get('status'),
        "userId": data.get('userId')
    }

    if not RemID:
        return jsonify({"status": "error", "message": "Reminder ID is required"}), 400

    update_data = {k: v for k, v in update_data.items() if v is not None}

    result = reminders_collection.update_one(
        {"_id": ObjectId(RemID)},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        return jsonify({"status": "error", "message": "Reminder not found or no changes made"}), 404

    return jsonify({"status": "success", "message": " Reminder Updated successfully"}), 200
