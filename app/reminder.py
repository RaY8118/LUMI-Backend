from flask import jsonify
from app import mongo
import uuid

reminders_collection = mongo.db.reminders


def generate_reminder_id():
    unique_id = uuid.uuid4().hex[:8]
    return f"{unique_id.upper()}"


def post_reminders(request):
    data = request.json
    try:
        data = request.json
    except Exception as e:
        return jsonify({"status": "error", "message": "Invalid JSON data"}), 400

    required_fields = ['title', 'description', 'date', 'time',
                       'status', 'userId']
    for field in required_fields:
        if field not in data:
            return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400

    title = data.get('title')
    description = data.get('description')
    date = data.get('date')
    time = data.get('time')
    status = data.get('status')
    userId = data.get('userId')
    urgent = data.get('isUrgent')
    important = data.get('isImportant')

    remid = generate_reminder_id()

    new_reminder = {
        "title": title,
        "description": description,
        "date": date,
        "time": time,
        "status": status,
        "urgent": urgent,
        "important": important,
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
            "time": r["time"],
            "status": r["status"],
            "urgent": r['urgent'],
            "important": r["important"],
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
        "time": data.get('time'),
        "status": data.get('status'),
        "urgent": data.get('isUrgent'),
        "important": data.get('isImportant'),
        "userId": data.get('userId')
    }

    if not RemID:
        return jsonify({"status": "error", "message": "Reminder ID is required"}), 400

    update_data = {k: v for k, v in update_data.items() if v is not None}

    result = reminders_collection.update_one(
        {"remId": RemID},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"status": "error", "message": "Reminder not found"}), 404

    if result.modified_count == 0:
        return jsonify({"status": "success", "message": "Reminder found, but no changes were made"}), 200

    return jsonify({"status": "success", "message": "Reminder updated successfully"}), 200
