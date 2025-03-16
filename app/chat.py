import random
from datetime import datetime
from string import ascii_uppercase

import pytz
from flask import jsonify, session
from flask_session import Session
from flask_socketio import SocketIO, join_room, leave_room, send

from app import mongo

rooms_collection = mongo.db.rooms
messages_collection = mongo.db.messages


def generate_unique_code(length):
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        if not rooms_collection.find_one({"roomId": code}):
            return code


def home(request):
    session.clear()
    data = request.json
    name = data.get("name")
    code = data.get("code")
    join = data.get("join")
    create = data.get("create")

    if not name:
        return jsonify({"status": "error", "message": "Please enter a name"}), 400

    if join != False and not code:
        return jsonify({"status": "error", "message": "Please enter a room code"}), 400

    room = code

    if create != False:
        room = generate_unique_code(8)
        rooms_collection.insert_one({"roomId": room, "members": [], "active": 0})
        messages_data = {"roomId": room, "messages": []}
        messages_collection.insert_one(messages_data)
    elif not rooms_collection.find_one({"roomId": room}):
        return jsonify({"status": "error", "message": "Room does not exist"}), 400

    session["room"] = room
    session["name"] = name

    return (
        jsonify(
            {"status": "success", "message": "You have joined the room successfully"}
        ),
        200,
    )
