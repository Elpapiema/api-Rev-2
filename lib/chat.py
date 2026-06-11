import json
import os
import time
import uuid

import requests
from flask import jsonify, request
from werkzeug.utils import secure_filename


AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://localhost:5832")
AI_SERVER_TOKEN = os.getenv("AI_SERVER_TOKEN", "secret-token")
CHATS_DIR = os.getenv("CHATS_DIR", "./chats")
CHAT_EXPIRATION_DAYS = int(os.getenv("CHAT_EXPIRATION_DAYS", "10"))
CHAT_EXPIRATION_SECONDS = CHAT_EXPIRATION_DAYS * 24 * 60 * 60


def get_chat_path(chat_id):
    safe_chat_id = secure_filename(chat_id)
    if safe_chat_id != chat_id or not chat_id.startswith("chat-"):
        return None
    return os.path.join(CHATS_DIR, f"{chat_id}.json")


def ensure_chats_dir():
    os.makedirs(CHATS_DIR, exist_ok=True)


def generate_chat_id():
    ensure_chats_dir()
    while True:
        chat_id = f"chat-{uuid.uuid4().hex[:8]}"
        if not os.path.exists(os.path.join(CHATS_DIR, f"{chat_id}.json")):
            return chat_id


def load_chat(chat_id):
    chat_path = get_chat_path(chat_id)
    if not chat_path or not os.path.isfile(chat_path):
        return None

    with open(chat_path, "r", encoding="utf-8") as chat_file:
        return json.load(chat_file)


def save_chat(chat):
    ensure_chats_dir()
    chat_path = get_chat_path(chat["chat_id"])
    if not chat_path:
        raise ValueError("chat_id inválido")

    tmp_path = f"{chat_path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as chat_file:
        json.dump(chat, chat_file, ensure_ascii=False, indent=2)
    os.replace(tmp_path, chat_path)


def delete_chat_file(chat_id):
    chat_path = get_chat_path(chat_id)
    if not chat_path or not os.path.isfile(chat_path):
        return False
    os.remove(chat_path)
    return True


def cleanup_expired_chats():
    ensure_chats_dir()
    current_time = int(time.time())

    for filename in os.listdir(CHATS_DIR):
        if not filename.endswith(".json"):
            continue

        chat_path = os.path.join(CHATS_DIR, filename)
        try:
            with open(chat_path, "r", encoding="utf-8") as chat_file:
                chat = json.load(chat_file)

            last_activity = int(chat.get("last_activity", 0))
            if current_time - last_activity > CHAT_EXPIRATION_SECONDS:
                os.remove(chat_path)
        except Exception:
            continue


def extract_ai_response(response_data):
    if isinstance(response_data, str):
        return response_data

    if not isinstance(response_data, dict):
        return str(response_data)

    for key in ("response", "message", "content", "text", "answer"):
        value = response_data.get(key)
        if isinstance(value, str):
            return value

    choices = response_data.get("choices")
    if isinstance(choices, list) and choices:
        first_choice = choices[0]
        if isinstance(first_choice, dict):
            message = first_choice.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"]
            if isinstance(first_choice.get("text"), str):
                return first_choice["text"]

    return json.dumps(response_data, ensure_ascii=False)


def call_ai_server(messages):
    latest_message = messages[-1]["content"] if messages else ""
    payload = {
        "message": latest_message,
        "messages": messages
    }
    headers = {
        "Authorization": f"Bearer {AI_SERVER_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        AI_SERVER_URL,
        json=payload,
        headers=headers,
        timeout=60
    )
    response.raise_for_status()

    try:
        return extract_ai_response(response.json())
    except ValueError:
        return response.text


def get_request_message():
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return None
    return message.strip()


def register(app):
    cleanup_expired_chats()

    @app.before_request
    def cleanup_chats_before_request():
        cleanup_expired_chats()

    @app.route("/chat", methods=["POST"])
    def create_chat():
        message = get_request_message()
        if not message:
            return jsonify({"error": "Falta el campo message"}), 400

        current_time = int(time.time())
        chat = {
            "chat_id": generate_chat_id(),
            "created_at": current_time,
            "last_activity": current_time,
            "messages": []
        }

        user_message = {"role": "user", "content": message}
        messages = [user_message]

        try:
            ai_response = call_ai_server(messages)
        except requests.RequestException:
            return jsonify({"error": "Error al comunicarse con el servidor de IA"}), 502

        chat["messages"].append(user_message)
        chat["messages"].append({"role": "assistant", "content": ai_response})
        chat["last_activity"] = int(time.time())
        save_chat(chat)

        return jsonify({
            "chat_id": chat["chat_id"],
            "response": ai_response
        })

    @app.route("/chat/<chat_id>", methods=["POST"])
    def continue_chat(chat_id):
        message = get_request_message()
        if not message:
            return jsonify({"error": "Falta el campo message"}), 400

        chat = load_chat(chat_id)
        if not chat:
            return jsonify({"error": "Conversación no encontrada"}), 404

        user_message = {"role": "user", "content": message}
        messages = chat.get("messages", []) + [user_message]

        try:
            ai_response = call_ai_server(messages)
        except requests.RequestException:
            return jsonify({"error": "Error al comunicarse con el servidor de IA"}), 502

        chat["messages"] = messages + [{"role": "assistant", "content": ai_response}]
        chat["last_activity"] = int(time.time())
        save_chat(chat)

        return jsonify({
            "chat_id": chat["chat_id"],
            "response": ai_response
        })

    @app.route("/chat/<chat_id>", methods=["GET"])
    def get_chat(chat_id):
        chat = load_chat(chat_id)
        if not chat:
            return jsonify({"error": "Conversación no encontrada"}), 404

        return jsonify({
            "chat_id": chat["chat_id"],
            "messages": chat.get("messages", [])
        })

    @app.route("/chat/<chat_id>", methods=["DELETE"])
    def delete_chat(chat_id):
        if not delete_chat_file(chat_id):
            return jsonify({"error": "Conversación no encontrada"}), 404
        return jsonify({"chat_id": chat_id, "deleted": True})

    @app.route("/chats", methods=["GET"])
    def list_chats():
        ensure_chats_dir()
        chats = []

        for filename in os.listdir(CHATS_DIR):
            if not filename.endswith(".json"):
                continue

            chat_path = os.path.join(CHATS_DIR, filename)
            try:
                with open(chat_path, "r", encoding="utf-8") as chat_file:
                    chat = json.load(chat_file)
                chats.append({
                    "chat_id": chat.get("chat_id"),
                    "created_at": chat.get("created_at"),
                    "last_activity": chat.get("last_activity")
                })
            except Exception:
                continue

        chats.sort(key=lambda chat: chat.get("last_activity") or 0, reverse=True)
        return jsonify({
            "total": len(chats),
            "chats": chats
        })
