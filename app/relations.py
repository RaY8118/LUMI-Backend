from flask import jsonify
from app import mongo
import uuid

user_collection = mongo.db.users
families_collection = mongo.db.families


def create_family(request):
    data = request.json
    caregiver_id = data.get('caregiverId')

    if not caregiver_id:
        return jsonify({"status": "error", "message": "Caregiver ID is required"}), 400

    # Check if the caregiver exists
    caregiver = user_collection.find_one(
        {"userId": caregiver_id, "role": "CG"})
    if not caregiver:
        return jsonify({"status": "error", "message": "Caregiver not found or invalid role"}), 400

    # Generate a unique family ID
    family_id = str(uuid.uuid4().hex[:8])

    # Create a enw family record in the families collection
    family_record = {
        "family_id": family_id,
        "created_by": caregiver_id,
        "members": [caregiver_id]
    }

    # Inset the family record into the familie collection
    families_collection.insert_one(family_record)

    # Assign the family record into the families collection
    result = user_collection.update_one(
        {"userId": caregiver_id},
        {"$set": {"family_id": family_id}}
    )
    if result.modified_count > 0:
        return jsonify({"status": "success", "familyId": family_id, "message": "Family created successfully"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to create family"}), 500


def add_user_to_family(request):
    data = request.json
    user_id = data.get('userId')
    family_id = data.get('familyId')

    if not user_id or not family_id:
        return jsonify({"status": "error", "message": "User ID and Family ID are required"}), 400

    # Check if the user exists
    user = user_collection.find_one({"userId": user_id})
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # Check if the family exists
    family = families_collection.find_one({"family_id": family_id})
    if not family:
        return jsonify({"status": "error", "message": "Family not found"}), 404

    # Update the user's family_id
    user_update = user_collection.update_one(
        {"userId": user_id},
        {"$set": {"family_id": family_id}}
    )

    # Add the user to the family's members list if not already present
    if user_id not in family.get("members", []):
        family_update = families_collection.update_one(
            {"family_id": family_id},
            {"$push": {"members": user_id}}
        )
    else:
        family_update = None  # User is already in the family, no need to update

    # Ensure both updates succeeded
    if user_update.modified_count > 0 and (not family_update or family_update.modified_count > 0):
        return jsonify({"status": "success", "message": f"User {user_id} added to family {family_id}"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to update user's family ID or family members"}), 500
