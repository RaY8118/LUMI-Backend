import random
from datetime import datetime
from string import ascii_uppercase

import pytz
from flask import jsonify, request, session
from flask_socketio import SocketIO, join_room, leave_room, send

from app import mongo, socketio

rooms_collection = mongo.db.rooms
messages_collection = mongo.db.messages

user_sessions = {}


def generate_unique_code(length):
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        if not rooms_collection.find_one({"roomId": code}):
            return code


# Create Room API
def create_room():
    try:
        room_code = generate_unique_code(8)
        print(
            f"Generated room code: {room_code}"
        )  # Add this line to check the generated code
        rooms_collection.insert_one({"room": room_code, "members": 0})
        return jsonify(
            {"message": "Room created", "room": room_code, "status": "success"}
        )
    except Exception as e:
        print(f"Error in create_room: {e}")  # Log the error to see it
        raise e


# Join Room API
def join_room_api(request):
    data = request.json
    print(data)
    room = data.get("room")
    name = data.get("name")

    room_data = rooms_collection.find_one({"room": room})
    print(f"Room data : {room_data}")
    if not room_data:
        return jsonify({"status": "error", "message": "Room not found"}), 404

    session["room"] = room
    session["name"] = name
    print(f"Session data: {session}")
    return jsonify(
        {"message": f"{name} joined room {room}", "room": room, "status": "success"}
    )


# SocketIO connection event
@socketio.on("connect")
def connect():
    sid = request.sid
    room = session.get("room")
    name = session.get("name")

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

    user_sessions[sid] = {"room": room, "name": name}
    join_room(room)
    send({"name": name, "message": f"{name} has joined the room"}, to=room)
    rooms_collection.update_one({"room": room}, {"$inc": {"members": 1}})
    print(f"{name} joined room {room}")


# Handle incoming messages
@socketio.on("message")
def handle_message(data):
    sid = request.sid
    room = user_sessions.get(sid, {}).get("room")
    name = user_sessions.get(sid, {}).get("name")
    message_content = data.get("message")

    if not room or not name or not message_content:
        send({"status": "error", "message": "Invalid data"}, to=sid)
        return

    room_data = rooms_collection.find_one({"room": room})
    if not room_data:
        send({"status": "error", "message": "Room not found"}, to=sid)
        return

    content = {"name": name, "message": message_content}
    messages_collection.insert_one(
        {"room": room, "name": name, "message": message_content}
    )
    send(content, to=room)
    print(f"Message from {name} in room {room}: {message_content}")


# Socket disconnection event
@socketio.on("disconnect")
def disconnect():
    sid = request.sid
    room = user_sessions.get(sid, {}).get("room")
    name = user_sessions.get(sid, {}).get("name")

    if room:
        leave_room(room)
        rooms_collection.update_one({"room": room}, {"$inc": {"members": -1}})
        updated_room = rooms_collection.find_one({"room": room})

        # # Delete the room if empty
        # if updated_room and updated_room["members"] <= 0:
        #     rooms_collection.delete_one({"room": room})

        send({"name": name, "message": f"{name} has left the room"}, to=room)
        print(f"{name} has left the room {room}")
        del user_sessions[sid]
