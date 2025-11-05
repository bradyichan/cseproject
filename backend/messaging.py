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


# ---------------------------------------------------------------------
# POST /messaging/send
# ---------------------------------------------------------------------
@messaging_bp.route("/send", methods=["POST"])
def send_message():
    """
    Send a message
    ---
    tags:
      - Messaging
    summary: Send a new message between users
    description: Create a message in a specific conversation between two users.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [conversation_id, sender_id, receiver_id, content]
            properties:
              conversation_id:
                type: string
                example: "conv_1234"
              sender_id:
                type: integer
                example: 2
              receiver_id:
                type: integer
                example: 7
              content:
                type: string
                example: "Hey, is this still available?"
    responses:
      201:
        description: Message sent successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                data:
                  type: object
                  properties:
                    message_id:
                      type: integer
                      example: 45
                    conversation_id:
                      type: string
                      example: "conv_1234"
                    sender_id:
                      type: integer
                      example: 2
                    receiver_id:
                      type: integer
                      example: 7
                    content:
                      type: string
                      example: "Hey, is this still available?"
                    timestamp:
                      type: string
                      example: "2025-11-03T18:00:00"
      400:
        description: Missing required fields
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


# ---------------------------------------------------------------------
# GET /messaging/conversation/<conversation_id>
# ---------------------------------------------------------------------
@messaging_bp.route("/conversation/<string:conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    """
    Get conversation messages
    ---
    tags:
      - Messaging
    summary: Retrieve all messages in a specific conversation
    parameters:
      - name: conversation_id
        in: path
        required: true
        schema:
          type: string
        description: The unique ID of the conversation
    responses:
      200:
        description: Messages retrieved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                data:
                  type: object
                  properties:
                    conversation:
                      type: array
                      items:
                        type: object
                        properties:
                          message_id:
                            type: integer
                            example: 101
                          sender_id:
                            type: integer
                            example: 2
                          receiver_id:
                            type: integer
                            example: 7
                          content:
                            type: string
                            example: "Sure, it's available!"
                          timestamp:
                            type: string
                            example: "2025-11-03T19:15:00"
      404:
        description: No messages found
    """
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


# ---------------------------------------------------------------------
# GET /messaging/user/<user_id>
# ---------------------------------------------------------------------
@messaging_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_conversations(user_id):
    """
    Get user's conversations
    ---
    tags:
      - Messaging
    summary: Retrieve all conversations a user is part of
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
        description: The user ID
    responses:
      200:
        description: List of conversation IDs
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                data:
                  type: object
                  properties:
                    conversations:
                      type: array
                      items:
                        type: string
                        example: "conv_5678"
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


# ---------------------------------------------------------------------
# DELETE /messaging/delete/<message_id>
# ---------------------------------------------------------------------
@messaging_bp.route("/delete/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    """
    Delete a message
    ---
    tags:
      - Messaging
    summary: Delete a specific message by its ID
    parameters:
      - name: message_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Message deleted successfully
      404:
        description: Message not found
    """
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