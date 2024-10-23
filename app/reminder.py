from flask import jsonify
from app import mongo
import uuid

# Access the MongoDB reminders collection
reminders_collection = mongo.db.reminders


def generate_reminder_id():
    """Generate a unique reminder ID using UUID."""
    unique_id = uuid.uuid4().hex[:8]  # Create a unique ID
    return f"{unique_id.upper()}"  # Return the ID in uppercase


def post_reminders(request):
    """Create a new reminder based on the request data."""
    data = request.json  # Get JSON data from the request
    try:
        data = request.json
    except Exception as e:
        return jsonify({"status": "error", "message": "Invalid JSON data"}), 400

    required_fields = ['title', 'description', 'date', 'time',
                       'status', 'userId']
    for field in required_fields:
        if field not in data:
            return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400

    # Extract reminder data from the request
    title = data.get('title')
    description = data.get('description')
    date = data.get('date')
    time = data.get('time')
    status = data.get('status')
    userId = data.get('userId')
    urgent = data.get('isUrgent')
    important = data.get('isImportant')

    remid = generate_reminder_id()  # Generate a unique reminder ID

    # Create a new reminder object
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

    # Insert the new reminder into the database
    reminders_collection.insert_one(new_reminder)

    return jsonify({"status": "success", "message": "Reminder saved successfully"}), 201


def get_reminders(request):
    """Retrieve reminders for a specific user."""
    try:
        data = request.json  # Get JSON data from the request
        userId = data.get('userId')  # Extract user ID

        if not userId:
            return jsonify({"status": "error", "message": "User ID is required"}), 400

        # Query the database for reminders belonging to the user
        user_reminders = list(reminders_collection.find({"userId": userId}))

        if not user_reminders:
            return jsonify({"status": "success", "message": "No reminders for this user", "reminders": []}), 204

        # Create a list of reminders to return
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
    """Delete a reminder based on the provided reminder ID."""
    data = request.json  # Get JSON data from the request
    RemID = data.get('remId')  # Extract reminder ID

    if not RemID:
        return jsonify({"status": "error", "message": "Reminder ID is required"}), 400

    # Attempt to delete the reminder from the database
    result = reminders_collection.delete_one({"remId": RemID})

    if result.deleted_count == 0:
        return jsonify({"status": "error", "message": "Reminder not found"}), 404

    return jsonify({"status": "success", "message": "Reminder Deleted Successfully"}), 200


def update_reminders(request):
    """Update an existing reminder based on the provided data."""
    data = request.json  # Get JSON data from the request
    RemID = data.get('remId')  # Extract reminder ID
    # Prepare data to be updated, filtering out None values
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

    # Remove keys with None values from the update data
    update_data = {k: v for k, v in update_data.items() if v is not None}

    # Attempt to update the reminder in the database
    result = reminders_collection.update_one(
        {"remId": RemID},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"status": "error", "message": "Reminder not found"}), 404

    if result.modified_count == 0:
        return jsonify({"status": "success", "message": "Reminder found, but no changes were made"}), 200

    return jsonify({"status": "success", "message": "Reminder updated successfully"}), 200
