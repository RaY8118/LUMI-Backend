from flask import jsonify
from app import mongo

user_collection = mongo.db.users


def add_caregiver(request):
    data = request.json
    care_giver_id = data.get('CGId')  # Get caregiver ID from request
    patient_id = data.get('PATId')  # Get patient ID from request

    # Check if both IDs are provided
    if not care_giver_id or not patient_id:
        return jsonify({'error': 'Patient ID  and Caregiver information are required'}), 404

     # Check if the caregiver exists
    caregiver = user_collection.find_one(
        {"userId": care_giver_id, "role": "CG"})

    if not caregiver:
        return jsonify({'error': 'Caregiver not found'}), 404

    # Check if the patient exists
    patient = user_collection.find_one({"userId": patient_id})
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    # Check if caregiver is already added to the patient
    existing_caregiver = next((cg for cg in patient.get(
        'caregivers', []) if cg['CGId'] == care_giver_id), None)
    if existing_caregiver:
        return jsonify({'error': 'Caregiver already added for this patient'}), 400

    # Prepare caregiver data to be added
    caregiver_data = {
        "CGId": care_giver_id,
        "name": caregiver.get('name'),
        "mobile": caregiver.get('mobile')
    }

    # Update the patient document by adding the caregiver
    result = user_collection.update_one(
        {"userId": patient_id},
        {"$push": {"caregivers": caregiver_data}})

    # Check if the update was successful
    if result.modified_count > 0:
        return jsonify({'message': 'Caregiver added successfully'}), 200
    else:
        return jsonify({'error': 'Failed to add caregiver'}), 500


def delete_caregiver(request):
    data = request.json
    care_giver_id = data.get('CGId')  # Get caregiver ID from request
    patient_id = data.get('PATId')  # Get patient ID from request

    # Check if both IDs are provided
    if not care_giver_id and not patient_id:
        return jsonify({'error': 'Patient ID and Caregiver ID are required '}), 404

    # Check if the patient exists
    patient = user_collection.find_one({"userId": patient_id})
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    # Remove the caregiver from the patient's list
    result = user_collection.update_one(
        {'userId': patient_id},
        {'$pull': {'caregivers': {'CGId': care_giver_id}}}
    )

    # Check if the caregiver was successfully removed
    if result.modified_count > 0:
        return jsonify({'status': 'success', 'message': 'Caregiver successfully removed'})
    else:
        return jsonify({'error': 'Caregiver not found or no changes made'})