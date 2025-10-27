"""
Module: messaging.py
Description: Provides basic message send, receive, and conversation endpoints
to simulate user communication within the Marketplace app.
Author: Team XX - CSE 2102
Date: 2025-10-27
"""

from flask import Blueprint, jsonify, request
from datetime import datetime

messaging_bp = Blueprint("messaging", __name__, url_prefix="/messages")

# Mock in-memory data
# conversations = { "chat_id": [ {sender, receiver, message, timestamp}, ... ] }
conversations = {}


@messaging_bp.route("/", methods=["GET"])
def get_all_conversations():
    """Return list of all chat IDs (used when user opens messages menu)."""
    return jsonify({"chats": list(conversations.keys())}), 200


@messaging_bp.route("/<chat_id>", methods=["GET"])
def get_conversation(chat_id):
    """Return entire conversation history for given chat ID."""
    if chat_id not in conversations:
        return jsonify({"error": "Chat not found"}), 404
    return jsonify({
        "chat_id": chat_id,
        "messages": conversations[chat_id]
    }), 200


@messaging_bp.route("/<chat_id>/send", methods=["POST"])
def send_message(chat_id):
    """Send a new message and append to the chat."""
    data = request.get_json() or {}
    sender = data.get("sender")
    receiver = data.get("receiver")
    message = data.get("message")

    if not all([sender, receiver, message]):
        return jsonify({"error": "Missing sender, receiver, or message"}), 400

    new_msg = {
        "sender": sender,
        "receiver": receiver,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if chat_id not in conversations:
        conversations[chat_id] = []
    conversations[chat_id].append(new_msg)

    return jsonify({
        "status": "sent",
        "chat_id": chat_id,
        "message": new_msg
    }), 201


@messaging_bp.route("/<chat_id>/latest", methods=["GET"])
def get_latest_message(chat_id):
    """Return the most recent message in a conversation."""
    if chat_id not in conversations or not conversations[chat_id]:
        return jsonify({"error": "No messages found"}), 404
    return jsonify(conversations[chat_id][-1]), 200
