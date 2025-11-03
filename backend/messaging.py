"""
Module: messaging.py
Description: Manages messaging between users in the Marketplace API.
Implements send, retrieve, and delete functionality using SQLite.
Author: Team 22 - CSE 2102
Date: 2025-11-03
"""

from datetime import datetime
from flask import Blueprint, jsonify, request
import sqlite3
import os

messaging_bp = Blueprint("messaging", __name__, url_prefix="/messaging")

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "marketplace.db")


def get_db_connection():
    """Return SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@messaging_bp.route("/send", methods=["POST"])
def send_message():
    """
    Send a message between users.
    Expects JSON: conversation_id, sender_id, receiver_id, content
    """
    data = request.get_json() or {}
    required = ["conversation_id", "sender_id", "receiver_id", "content"]

    if not all(f in data for f in required):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    timestamp = datetime.now().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (conversation_id, sender_id, receiver_id, content, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (data["conversation_id"], data["sender_id"], data["receiver_id"], data["content"], timestamp))
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "message_id": msg_id,
            "conversation_id": data["conversation_id"],
            "sender_id": data["sender_id"],
            "receiver_id": data["receiver_id"],
            "content": data["content"],
            "timestamp": timestamp
        }
    }), 201


@messaging_bp.route("/conversation/<string:conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    """Retrieve all messages in a specific conversation (oldest → newest)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id AS message_id, sender_id, receiver_id, content, timestamp
        FROM messages
        WHERE conversation_id = ?
        ORDER BY timestamp ASC
    """, (conversation_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if not rows:
        return jsonify({"status": "error", "message": "No messages found"}), 404

    return jsonify({"status": "success", "data": {"conversation": rows}}), 200


@messaging_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_conversations(user_id):
    """
    Retrieve all unique conversations a user is part of.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT conversation_id
        FROM messages
        WHERE sender_id = ? OR receiver_id = ?
        ORDER BY conversation_id
    """, (user_id, user_id))
    convos = [row["conversation_id"] for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        "status": "success",
        "data": {"conversations": convos}
    }), 200


@messaging_bp.route("/delete/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    """Delete a specific message by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"status": "error", "message": "Message not found"}), 404

    return jsonify({
        "status": "success",
        "message": f"Message {message_id} deleted"
    }), 200
