from flask import jsonify
from app import mongo

user_collection = mongo.db.users


def add_caregiver(request):
    data = request.json
    care_giver_id = data.get('CGId')
    patient_id = data.get('PATId')

    if not care_giver_id or not patient_id:
        return jsonify({'error': 'Patient ID  and Caregiver information are required'}), 404

    caregiver = user_collection.find_one(
        {"userId": care_giver_id, "role": "CG"})

    if not caregiver:
        return jsonify({'error': 'Caregiver not found'}), 404

    patient = user_collection.find_one({"userId": patient_id})
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    existing_caregiver = next((cg for cg in patient.get(
        'caregivers', []) if cg['CGId'] == care_giver_id), None)
    if existing_caregiver:
        return jsonify({'error': 'Caregiver already added for this patient'}), 400

    caregiver_data = {
        "CGId": care_giver_id,
        "name": caregiver.get('name'),
        "mobile": caregiver.get('mobile')
    }

    result_patient = user_collection.update_one(
        {"userId": patient_id},
        {"$push": {'caregivers': caregiver_data}})
    
    patient_data = {
        "PATId": patient_id,
        "name": patient.get("name"),
        "mobile": patient.get("mobile")
    }
    
    result_caregiver = user_collection.update_one(
        {"userId": care_giver_id},
        {"$push" : {'patients': patient_data}}
    )

    if result_patient.modified_count > 0 and result_caregiver.modified_count > 0:
        return jsonify({'message': 'Caregiver and Patient Linked successfully'}), 200
    else:
        return jsonify({'error': 'Failed to add caregiver or patient'}), 500


def delete_caregiver(request):
    data = request.json
    care_giver_id = data.get('CGId')
    patient_id = data.get('PATId')

    if not care_giver_id or not patient_id:
        return jsonify({'error': 'Patient ID and Caregiver ID are required '}), 404

    patient = user_collection.find_one({"userId": patient_id})
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    result_patient = user_collection.update_one(
        {'userId': patient_id},
        {'$pull': {'caregivers': {'CGId': care_giver_id}}}
    )
    
    caregiver = user_collection.find_one({"userId":care_giver_id})
    if not caregiver:
        return jsonify({'error':'Caregiver not found'}),404
    
    result_caregiver = user_collection.update_one(
        {'userId': care_giver_id},
        {'$pull': {'patients': {'PATId': patient_id}}}
    )

    if result_patient.modified_count > 0 and result_caregiver.modified_count > 0:
        return jsonify({'status': 'success', 'message': 'Caregiver and Patient successfully removed'})
    else:
        return jsonify({'error': 'Caregiver or Patient not found or no changes made'})

