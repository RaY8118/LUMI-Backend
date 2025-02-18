import requests
from flask_apscheduler import APScheduler
from app import mongo
from flask import jsonify

reminders_collection = mongo.db.reminders
user_collection = mongo.db.users
tokens_collection = mongo.db.tokens
scheduler = APScheduler()


def custom_push_notification(request):
    data = request.get_json()
    patient_id = data.get("PATId")
    message = data.get("message")

    # Retrieve patient's push token from the database
    patient = tokens_collection.find_one({"userId": patient_id})
    push_token = patient.get("token")

    if not push_token:
        return jsonify({"error": "Push token not found for patient."}), 400

    # Create the notification payload
    payload = {
        "to": push_token,
        "title": "Message from Caregiver",
        "body": message,
        "sound": "default",
    }

    # Send the notification using the Expo push service
    try:
        response = requests.post(
            "https://exp.host/--/api/v2/push/send", json=payload)
        response.raise_for_status()

        return jsonify({"success": "Notification sent successfully"}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


def store_user_token(data):
    """Function to handle storing user tokens."""
    token = data.get("token")
    user_id = data.get("userId")

    if not token:
        return jsonify({"status": "error", "message": "Missing token"}), 400

    # Insert or update the token in the database
    tokens_collection.update_one(
        {"userId": user_id}, {"$set": {"token": token}}, upsert=True
    )

    return jsonify({"status": "success", "message": "Token stored successfully"}), 200


def get_user_token(request):
    """Function to get stored token"""
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify({"status": "error", "message": "Missing UserId"}), 400

    data = tokens_collection.find_one({"userId": user_id})
    push_token = data.get("token")

    if not push_token:
        return jsonify({"error": "Push token not found for user."}), 400

    return jsonify(
        {
            "status": "success",
            "message": "Token retrievied successfully",
            "token": push_token,
        }
    )
