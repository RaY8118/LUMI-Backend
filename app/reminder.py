from flask import jsonify
from app import mongo
from bson import ObjectId

reminders_collection = mongo.db.reminders


def generate_reminder_id():
    prefix = "REMID"
    count = reminders_collection.count_documents({})
    number = count + 1
    return f"{prefix}{str(number).zfill(3)}"


def post_reminders(request):
    data = request.json
    title = data.get('title')
    description = data.get('description')
    date = data.get('date')
    status = data.get('status')
    userId = data.get('userId')

    remid = generate_reminder_id()

    new_reminder = {
        "title": title,
        "description": description,
        "date": date,
        "status": status,
        "userId": userId,
        "remId": remid
    }

    reminders_collection.insert_one(new_reminder)

    return jsonify({"status": "success", "message": "Reminder saved successfully"}), 201


def get_reminders(request):
    try:
        data = request.json
        userId = data.get('userId')

        if not userId:
            return jsonify({"status": "error", "message": "User ID is required"}), 400

        user_reminders = list(reminders_collection.find({"userId": userId}))

        if not user_reminders:
            return jsonify({"status": "success", "message": "No reminders for this user", "reminders": []}), 204

        reminder_list = [{
            "_id": str(r["_id"]),
            "title": r["title"],
            "description": r["description"],
            "date": r["date"],
            "status": r["status"],
            "remId": r["remId"]
        } for r in user_reminders]

        return jsonify({"status": "success", "message": "Retrieved all reminders", "reminders": reminder_list}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": "Internal Server Error", "details": str(e)}), 500


def delete_reminders(request):
    data = request.json
    RemID = data.get('remId')

    if not RemID:
        return jsonify({"status": "error", "message": "Reminder ID is required"}), 400

    result = reminders_collection.delete_one({"remId": RemID})

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
        {"remId": RemID},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        return jsonify({"status": "error", "message": "Reminder not found or no changes made"}), 404

    return jsonify({"status": "success", "message": " Reminder Updated successfully"}), 200
