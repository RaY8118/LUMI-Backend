import random
from datetime import datetime
from string import ascii_uppercase

import pytz
from flask import jsonify, request, session
from flask_socketio import SocketIO, close_room, join_room, leave_room, send

from app import mongo, socketio

rooms_collection = mongo.db.rooms
messages_collection = mongo.db.messages
user_collection = mongo.db.users
families_collection = mongo.db.families

user_sessions = {}


def generate_unique_code(length):
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        if not rooms_collection.find_one({"roomId": code}):
            return code


# Create Room API
def create_room(request):
    data = request.json
    family_id = data.get("familyId")
    if not family_id:
        return (
            jsonify(
                {"status": "error", "message": "Family ID or creator name missing"}
            ),
            400,
        )

    # Check if room for this family already exists
    existing_room = rooms_collection.find_one({"family.familyId": family_id})
    if existing_room:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Room already exists for this family.\nRoom Code: {existing_room['room']}",
                    "room": existing_room["room"],
                }
            ),
            400,
        )

    room_code = generate_unique_code(8)
    rooms_collection.insert_one({"room": room_code, "members": 0, "family": family_id})
    return jsonify(
        {
            "message": f"Room created for family {family_id}",
            "room": room_code,
            "status": "success",
        }
    )


# Join Room API
def join_room_api(request):
    data = request.json
    room = data.get("room")
    name = data.get("name")
    caregiver_id = data.get("CGId")
    patient_id = data.get("PATId")
    role = data.get("role")
    user_id = caregiver_id if role == "CG" else patient_id

    if not room or not name:
        return (
            jsonify(
                {"status": "error", "message": "Please provide proper name and room ID"}
            ),
            404,
        )

    room_data = rooms_collection.find_one({"room": room})
    if not room_data:
        return jsonify({"status": "error", "message": "Room not found"}), 404

    user = user_collection.find_one({"userId": user_id})

    if room_data["family"]["familyId"] != user["family_id"]:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "You don not have the permission to join this room",
                }
            ),
            401,
        )

    messages_data = messages_collection.find_one({"roomId": room})
    messsages = messages_data["messages"] if messages_data else []

    session["name"] = name
    session["room"] = room
    session["user"] = caregiver_id if role == "CG" else patient_id
    return jsonify(
        {
            "status": "success",
            "message": f"{name} joined room {room}",
            "room": room,
            "messages": messsages,
        }
    )


# SocketIO connection event
@socketio.on("connect")
def connect():
    sid = request.sid
    room = session.get("room")
    name = session.get("name")
    user = session.get("user")

    if not room or not name:
        send(
            {
                "status": "error",
                "message": "Room and name are required to join the room",
            },
            to=sid,
        )
        return

    room_data = rooms_collection.find_one({"room": room})
    if not room_data:
        send({"status": "error", "message": "Room not found"}, to=sid)
        return

    user_sessions[sid] = {"room": room, "name": name, "user": user}
    join_room(room)
    rooms_collection.update_one({"room": room}, {"$inc": {"members": 1}}, upsert=True)


# Handle incoming messages
@socketio.on("message")
def handle_message(data):
    sid = request.sid
    room = user_sessions.get(sid, {}).get("room")
    name = user_sessions.get(sid, {}).get("name")
    user = user_sessions.get(sid, {}).get("user")
    message_content = data.get("message")

    if not room or not name or not message_content:
        send({"status": "error", "message": "Invalid data"}, to=sid)
        return

    room_data = rooms_collection.find_one({"room": room})
    if not room_data:
        send({"status": "error", "message": "Room not found"}, to=sid)
        return
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
    ist_time = utc_time.astimezone(pytz.timezone("Asia/Kolkata"))

    content = {
        "name": name,
        "message": message_content,
        "createdAt": ist_time.strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
    }
    send(content, to=room)
    messages_collection.update_one(
        {"roomId": room}, {"$push": {"messages": content}}, upsert=True
    )


# Socket disconnection event
@socketio.on("disconnect")
def disconnect():
    try:
        sid = request.sid
        room = user_sessions.get(sid, {}).get("room")
        name = user_sessions.get(sid, {}).get("name")

        if room:
            leave_room(room)
            rooms_collection.update_one({"room": room}, {"$inc": {"members": -1}})
            updated_room = rooms_collection.find_one({"room": room})

            # Delete the room if empty
            # if updated_room and updated_room["members"] <= 0:
            #     close_room(room)
            #     print(f"Room deleted: {room}")
            #     rooms_collection.delete_one({"room": room})

            del user_sessions[sid]
    except Exception as e:
        print(f"Error during disconnect: {str(e)}")
