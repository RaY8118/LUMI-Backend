from flask import jsonify
from app import mongo

user_collection = mongo.db.users


def add_caregiver_patient(request):
    data = request.json
    caregiver_id = data.get('CGId')  # Get caregiver ID from request
    patient_id = data.get('PATId')  # Get patient ID from request

    # Check if both IDs are provided
    if not caregiver_id or not patient_id:
        return jsonify({"status": "error", "message": "Caregiver ID and Patient ID are required"}), 400

    # Check if the patient exists
    patient = user_collection.find_one({"userId": patient_id})
    if not patient:
        return jsonify({"status": "error", "message": "Patient not found"}), 404

    # Check if the caregiver exists
    caregiver = user_collection.find_one(
        {"userId": caregiver_id, "role": "CG"})
    if not caregiver:
        return jsonify({"status": "error", "message": "Caregiver not found or invalid role"}), 404

    # Check if the patient is already assigned to this caregiver
    existing_patient = next((p for p in caregiver.get(
        'patients', []) if p["PATId"] == patient_id), None)
    if existing_patient:
        return jsonify({"status": "error", "message": " Patient already assigned to this caregiver"}), 400

    # Check if the caregiver is already added for this patient
    exisiting_caregiver = next((cg for cg in patient.get(
        'Caregivers', []) if cg["CGId"] == caregiver_id), None)
    if exisiting_caregiver:
        return jsonify({"status": "error", "message": "Caregiver already added to this patient"}), 400

    # Prepare data to be added to both caregiver and patient documents
    caregiver_data = {
        "CGId": caregiver_id,
        "name": caregiver.get("name"),
        "mobile": caregiver.get("mobile")
    }
    patient_data = {
        "PATId": patient_id,
        "name": patient.get("name"),
        "mobile": patient.get("mobile")
    }

    # Update the caregiver's document by adding the patient
    caregiver_update = user_collection.update_one(
        {"userId": caregiver_id},
        {"$push": {"patients": patient_data}}
    )

    # Update the patient's document by adding the caregiver
    patient_update = user_collection.update_one(
        {"userId": patient_id},
        {"$push": {"caregivers": caregiver_data}}
    )
    # Check if both updates were successful
    if caregiver_update.modified_count > 0 and patient_update.modified_count > 0:
        return jsonify({"status": "success", "message": "Caregiver successfully added to patient and patient successfully added to caregiver"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to update caregiver and patient documents"}), 500


def delete_caregiver_patient(request):
    data = request.json  # Get JSON data from the request

    care_giver_id = data.get('CGId')  # Get caregiver ID from request
    patient_id = data.get('PATId')  # Get patient ID from request

    # Check if both IDs are provided
    if not care_giver_id or not patient_id:
        return jsonify({"status": "error", "message": "Patient ID and Caregiver ID are required"}), 404

    # Check if the caregiver exists
    caregiver = user_collection.find_one(
        {"userId": care_giver_id, "role": "CG"})
    if not caregiver:
        return jsonify({"status": "error", "message": "Caregiver not found"}), 404

    # Check if the patient exists
    patient = user_collection.find_one({"userId": patient_id})
    if not patient:
        return jsonify({"status": "error", "message": "Patient not found"}), 404

    # Remove the caregiver from the patient's caregivers list
    result_patient = user_collection.update_one(
        {"userId": patient_id},
        {"$pull": {"caregivers": {"CGId": care_giver_id}}}
    )

    # Check if the update was successful
    if result_patient.modified_count == 0:
        return jsonify({"status": "error", "message": "Caregiver not found in patient\'s caregivers list"}), 404

    # Remove the patient from the caregiver's patients list
    result_caregiver = user_collection.update_one(
        {"userId": care_giver_id},
        {"$pull": {"patients": {"PATId": patient_id}}}
    )

    # Check if the update was successful
    if result_caregiver.modified_count > 0:
        return jsonify({"status": "success", "message": "Caregiver and Patient relationship deleted successfully"}), 200
    else:
        return jsonify({"status": "error", "message": "Patient not found in caregiver\'s patients list"}), 404
