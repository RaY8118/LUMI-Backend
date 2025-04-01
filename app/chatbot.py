import os

from flask import jsonify
from google import genai


def chatbot(request):
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
    except Exception as e:
        return jsonify({"error": str(e), "reply": "An eror occured"})
