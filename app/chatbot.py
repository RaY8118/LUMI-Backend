import os

from flask import Blueprint, jsonify, request
from google import genai

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/", methods=["POST"])
def chatbot():
    try:
        data = request.json
        user_message = data.get("message", "").strip()

        if not user_message:
            return (
                jsonify({"status": "error", "message": "Please enter a message"}),
                400,
            )
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API key is missing. Checking your .env file.")

        client = genai.Client(api_key=api_key)
        prompt = "Don't use text styling keep the text plain and concise"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[user_message, prompt],
        )
        reply = response.text if response.text else "I couldn't understand that"

        return jsonify({"status": "success", "reply": reply}), 200
    except ValueError as e:
        print(f"Value Error: {str(e)}")
        return jsonify({"status": "error", "message": "An error occurred"}), 400
    except KeyError as e:
        print(f"Key Error: {str(e)}")
        return jsonify({"status": "error", "message": "Missing expected key"}), 400
