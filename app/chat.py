import random
from datetime import datetime
from string import ascii_uppercase

import pytz
from flask import Blueprint, jsonify, request, session
from flask_socketio import close_room, join_room, leave_room, send
from pymongo.errors import PyMongoError
from werkzeug.exceptions import BadRequest

from app import mongo, socketio

chat_bp = Blueprint("chat", __name__)
rooms_collection = mongo.db.rooms
messages_collection = mongo.db.messages
user_collection = mongo.db.users
families_collection = mongo.db.families

user_sessions = {}


def generate_unique_code(length):
    """Function ot generate a unique code for room creation"""
    while True:
        code = "".join(random.choice(ascii_uppercase) for _ in range(length))
        if not rooms_collection.find_one({"roomId": code}):
            return code


# Create Room API
@chat_bp.route("/create-room", methods=["POST"])
def create_room():
    """Function to create socket rooms"""
    try:
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
        existing_room = rooms_collection.find_one({"family": family_id})
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
        rooms_collection.insert_one(
            {"room": room_code, "members": 0, "family": family_id}
        )
        return jsonify(
            {
                "message": f"Room created for family {family_id}",
                "room": room_code,
                "status": "success",
            }
        )
    except BadRequest as e:
        print(f"Bad request error: {str(e)}")
        return jsonify({"status": "error", "message": "Invalid request data"}), 400
    except PyMongoError as e:
        print(f"Database error: {str(e)}")
        return jsonify({"status": "error", "message": "Database error occurred"}), 500
    except KeyError as e:
        print(f"Key error: {str(e)}")
        return (
            jsonify(
                {"status": "error", "message": "Missing required data in the database"}
            ),
            500,
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return (
            jsonify({"status": "error", "message": "An unexpected error occurred"}),
            500,
        )


# Join Room API
@chat_bp.route("/join-room", methods=["POST"])
def join_room_api():
    """Function to join room using name and roomId"""
    try:
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
                    {
                        "status": "error",
                        "message": "Please provide proper name and room ID",
                    }
                ),
                404,
            )

        room_data = rooms_collection.find_one({"room": room})
        if not room_data:
            return jsonify({"status": "error", "message": "Room not found"}), 404

        user = user_collection.find_one({"userId": user_id})

        if room_data["family"] != user["family_id"]:
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
    except BadRequest as e:
        print(f"Bad request error: {str(e)}")
        return jsonify({"status": "error", "message": "Invalid request data"}), 400
    except PyMongoError as e:
        print(f"Database error: {str(e)}")
        return jsonify({"status": "error", "message": "Database error occurred"}), 500
    except KeyError as e:
        print(f"Key error: {str(e)}")
        return jsonify({"status": "error", "message": "Required data not found"}), 404
    except TypeError as e:
        print(f"Type error: {str(e)}")
        return (
            jsonify({"status": "error", "message": "Invalid data type in request"}),
            400,
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return (
            jsonify({"status": "error", "message": "An unexpected error occurred"}),
            500,
        )


# SocketIO connection event
@socketio.on("connect")
def connect():
    """Function to connect to a socket room"""
    sid = request.sid
    try:
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
        rooms_collection.update_one(
            {"room": room}, {"$inc": {"members": 1}}, upsert=True
        )
    except PyMongoError as e:
        print(f"Database error during connection: {str(e)}")
        send({"status": "error", "message": "Database error occurred"}, to=sid)
    except BadRequest as e:
        print(f"Bad request error: {str(e)}")
        send(
            {"status": "error", "message": "Bad request. Invalid data or session"},
            to=sid,
        )
    except Exception as e:
        print(f"Unexpected error during connectionL {str(e)}")
        send({"status": "error", "message": "An unexpected error occurred"}, to=sid)


# Handle incoming messages
@socketio.on("message")
def handle_message(data):
    """Function to send message in the socket room"""
    sid = request.sid
    try:
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
    except KeyError as e:
        print(f"Key error: {str(e)}")
        send(
            {"status": "error", "message": "Missing required user session data"}, to=sid
        )
    except PyMongoError as e:
        print(f"Database error: {str(e)}")
        send({"status": "error", "message": "Database error occurred"}, to=sid)
    except ValueError as e:
        print(f"Value error: {str(e)}")
        send({"status": "error", "message": "Invalid data provided"}, to=sid)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        send({"status": "error", "message": "An unexpected error occurred"}, to=sid)


# Socket disconnection event
@socketio.on("disconnect")
def disconnect():
    """Function to disconnect from the socket room"""
    try:
        sid = request.sid
        room = user_sessions.get(sid, {}).get("room")

        if room:
            leave_room(room)
            try:
                rooms_collection.update_one({"room": room}, {"$inc": {"members": -1}})
                updated_room = rooms_collection.find_one({"room": room})

                if updated_room and updated_room["members"] <= 0:
                    close_room(room)
                    print(f"Room deleted: {room}")
                    rooms_collection.delete_one({"room": room})
            except PyMongoError as db_error:
                print(f"Database error during room update or deletion: {str(db_error)}")
            del user_sessions[sid]
    except (KeyError, TypeError, AttributeError) as e:
        print(f"Error during disconnect: {str(e)}")
