from flask_socketio import join_room, leave_room, send
import random
from flask import jsonify
from string import ascii_uppercase
from app import mongo
from datetime import datetime
import pytz

rooms_collection = mongo.db.rooms
messages_collection = mongo.db.messages


def generate_unique_code(length):
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        if not rooms_collection.find_one({"roomId": code}):
            return code


def home(request):
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

    return jsonify(
        {
            "status": "success",
            "message": "You have joined the room successfully",
            "roomId": room,
            "name": name,
        }
    ), 200


def room(request):
    data = request.json
    name = data.get("name")
    room = data.get("roomId")

    if not room or not name:
        return jsonify({"status": "error", "message": "Missing roomId or name"}), 400

    room_data = messages_collection.find_one({"roomId": room})

    if not room_data:
        return jsonify({"status": "error", "message": "Room does not exist"}), 404

    message_data = messages_collection.find_one({"roomId": room})
    messages = message_data["messages"] if message_data else []

    return jsonify({"status": "success", "messages": messages, "roomId": room}), 200


def message(data):
    room = data.get("roomId")
    name = data.get("name")

    if not room or not name:
        return

    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
    ist_time = utc_time.astimezone(pytz.timezone("Asia/Kolkata"))

    content = {
        "name": name,
        "message": data["data"],
        "timestamp": ist_time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    send(content, to=room)
    messages_collection.update_one({"roomId": room}, {"$push": {"messages": content}})

    print(f"{name} said {data['data']} at {content['timestamp']} ")


def connect(auth):
    room = auth.get("roomId")
    name = auth.get("name")

    if not room or not name:
        return

    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms_collection.update_one(
        {"roomId": room}, {"$addToSet": {"members": name}, "$inc": {"activeMembers": 1}}
    )
    print(f"{name} joined room {room}")


def disconnet(request):
    data = request.args
    room = data.get("roomId")
    name = data.get("name")

    if not room or not name:
        return

    leave_room(room)
    rooms_collection.update_one(
        {"roomId": room}, {"$pull": {"members": name}, "$inc": {"activeMembers": -1}}
    )

    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")
