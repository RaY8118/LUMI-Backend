from flask import jsonify
from app import mongo
import uuid

reminders_collection = mongo.db.reminders
user_collection = mongo.db.users


def generate_reminder_id():
    unique_id = uuid.uuid4().hex[:8]
    return f"{unique_id.upper()}"


def post_reminders(request):
    data = request.json

    required_fields = ['title', 'description', 'date',
                       'status', 'isUrgent', 'isImportant', 'userId']
    for field in required_fields:
        if field not in data:
            return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400

    title = data.get('title')
    description = data.get('description')
    date = data.get('date')
    status = data.get('status')
    userId = data.get('userId')
    urgent = data.get('isUrgent')
    important = data.get('isImportant')

    remid = generate_reminder_id()

    new_reminder = {
        "title": title,
        "description": description,
        "date": date,
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

    if result.modified_count == 0:
        return jsonify({"status": "error", "message": "Reminder not found or no changes made"}), 404

    return jsonify({"status": "success", "message": " Reminder Updated successfully"}), 200


def post_reminders_for_patients(request):
    data = request.json
    caregiver_id = data.get('caregiverId')
    patient_id = data.get('patientId')

    if not caregiver_id or not patient_id:
        return jsonify({"status": "error", "message": "Caregiver ID and Patient ID are required"}), 400

    caregiver = user_collection.find_one(
        {"userId": caregiver_id, "role": "CG"})
    if not caregiver:
        return jsonify({"status": "error", "mesage": "Caregiver not found"}), 404

    if patient_id not in [p['PATId'] for p in caregiver.get('patients', [])]:
        return jsonify({"status": "error", "message": "Unauthorized to add reminders for this patient"}), 403

    required_fields = ['title', 'description',
                       'date', 'status', 'IsUrgent', 'IsImportant']
    for field in required_fields:
        if field not in data:
            return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400

    title = data.get('title')
    description = data.get('description')
    date = data.get('date')
    status = data.get('status')
    urgent = data.get('IsUrgent')
    important = data.get('IsImportant')

    remid = generate_reminder_id()

    new_reminder = {
        "title": title,
        "description": description,
        "date": date,
        "status": status,
        "urgent": urgent,
        "important": important,
        "userId": patient_id,
        "remId": remid
    }

    reminders_collection.insert_one(new_reminder)

    return jsonify({"status": "success", "message": "Reminder saved successfully for the patient"}), 201


def get_reminders_for_patient(request):
    data = request.json
    caregiver_id = data.get('caregiverId')
    patient_id = data.get('patientId')

    if not caregiver_id or not patient_id:
        return jsonify({"status": "error", "message": "Cargiver ID and Patient ID are required"}), 400

    caregiver = user_collection.find_one(
        {"userId": caregiver_id, "role": "CG"})
    if not caregiver:
        return jsonify({"status": "error", "message": "Caregiver not found"}), 404

    if patient_id not in [p['PATId'] for p in caregiver.get('patients', [])]:
        return jsonify({"status": "error", "message": "Unauthorized to retrieve remnders for this patient"}), 403

    patient_reminders = list(reminders_collection.find({"userId": patient_id}))

    if not patient_reminders:
        return jsonify({"status": "success", "message": "No reminders for this patient", "reminders": []}), 204

    reminder_list = [{
        "_id": str(r["_id"]),
        "title": r["title"],
        "description": r["description"],
        "date": r["date"],
        "status": r["status"],
        "urgent": r["urgent"],
        "important": r["important"],
        "remId": r["remId"]
    } for r in patient_reminders]

    return jsonify({"status": "success", "message": "Retrieved reminders for the patient", "reminders": reminder_list}), 200


def delete_reminders_for_patient(request):
    data = request.json
    caregiver_id = data.get('caregiverId')
    patient_id = data.get('patientId')
    remId = data.get('remId')

    if not caregiver_id or not patient_id or not remId:
        return jsonify({"status": "error", "message": "Caregiver ID, Patient ID, and Reminder ID are required"}), 400

    # Check if caregiver has permission to delete reminders for this patient
    caregiver = user_collection.find_one({"userId": caregiver_id, "role": "CG"})
    if not caregiver:
        return jsonify({"status": "error", "message": "Caregiver not found"}), 404

    if patient_id not in [p['PATId'] for p in caregiver.get('patients', [])]:
        return jsonify({"status": "error", "message": "Unauthorized to delete reminders for this patient"}), 403

    result = reminders_collection.delete_one({"remId": remId, "userId": patient_id})

    if result.deleted_count == 0:
        return jsonify({"status": "error", "message": "Reminder not found"}), 404

    return jsonify({"status": "success", "message": "Reminder deleted successfully for the patient"}), 200


def update_reminders_for_patient(request):
    data = request.json
    caregiver_id = data.get('caregiverId')
    patient_id = data.get('patientId')
    remId = data.get('remId')

    if not caregiver_id or not patient_id or not remId:
        return jsonify({"status": "error", "message": "Caregiver ID, Patient ID, and Reminder ID are required"}), 400

    # Check if caregiver has permission to update reminders for this patient
    caregiver = user_collection.find_one({"userId": caregiver_id, "role": "CG"})
    if not caregiver:
        return jsonify({"status": "error", "message": "Caregiver not found"}), 404

    if patient_id not in [p['PATId'] for p in caregiver.get('patients', [])]:
        return jsonify({"status": "error", "message": "Unauthorized to update reminders for this patient"}), 403

    update_data = {
        "title": data.get('title'),
        "description": data.get('description'),
        "date": data.get('date'),
        "status": data.get('status'),
        "urgent": data.get('isUrgent'),
        "important": data.get('isImportant')
    }

    update_data = {k: v for k, v in update_data.items() if v is not None}

    result = reminders_collection.update_one(
        {"remId": remId, "userId": patient_id},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        return jsonify({"status": "error", "message": "Reminder not found or no changes made"}), 404

    return jsonify({"status": "success", "message": "Reminder updated successfully for the patient"}), 200


