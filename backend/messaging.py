"""
Module: messaging.py
Description: Manages messaging between users in the Marketplace API.
Now includes proper inbox endpoint for SellerDashboard.
Author: Team 22 - CSE 2102
"""

import sqlite3
import os
from datetime import datetime
from flask import Blueprint, jsonify, request

messaging_bp = Blueprint("messaging", __name__, url_prefix="/messaging")

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "marketplace.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------
# POST /messaging/send
# ---------------------------------------------------------------------
@messaging_bp.route("/send", methods=["POST"])
def send_message():
    data = request.get_json() or {}
    required = ["conversation_id", "sender_id", "receiver_id", "content"]

    if not all(f in data for f in required):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    timestamp = datetime.now().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO messages (conversation_id, sender_id, receiver_id, content, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data["conversation_id"],
            data["sender_id"],
            data["receiver_id"],
            data["content"],
            timestamp,
        ),
    )

    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "message_id": msg_id,
                    "conversation_id": data["conversation_id"],
                    "sender_id": data["sender_id"],
                    "receiver_id": data["receiver_id"],
                    "content": data["content"],
                    "timestamp": timestamp,
                },
            }
        ),
        201,
    )


# ---------------------------------------------------------------------
# GET /messaging/conversation/<conversation_id>
# ---------------------------------------------------------------------
@messaging_bp.route("/conversation/<string:conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id AS message_id, sender_id, receiver_id, content, timestamp
        FROM messages
        WHERE conversation_id = ?
        ORDER BY timestamp ASC
        """,
        (conversation_id,),
    )

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
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT DISTINCT conversation_id
        FROM messages
        WHERE sender_id = ? OR receiver_id = ?
        ORDER BY conversation_id
        """,
        (user_id, user_id),
    )

    convos = [row["conversation_id"] for row in cursor.fetchall()]
    conn.close()

    return jsonify({"status": "success", "data": {"conversations": convos}}), 200


# ---------------------------------------------------------------------
# DELETE /messaging/delete/<message_id>
# ---------------------------------------------------------------------
@messaging_bp.route("/delete/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    conn.commit()

    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"status": "error", "message": "Message not found"}), 404

    return (
        jsonify(
            {"status": "success", "message": f"Message {message_id} deleted"}
        ),
        200,
    )


# ---------------------------------------------------------------------
# ⭐ NEW: GET /messaging/inbox/<seller_id>
# Returns all unique buyers who messaged this seller about an item.
#
# conversation_id format we assume:
#   "conv_<buyer_id>_<seller_id>_<item_id>"
# ---------------------------------------------------------------------
@messaging_bp.route("/inbox/<int:seller_id>", methods=["GET"])
def get_inbox(seller_id):
    """
    Example return:
    {
      "status": "success",
      "data": {
        "conversations": [
          {
            "buyer_id": 3,
            "buyer_username": "alex",
            "item_id": 10,
            "item_title": "Xbox",
            "conversation_id": "conv_3_7_10"
          }
        ]
      }
    }
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all distinct conversations where this user was the receiver (seller)
    cursor.execute(
        """
        SELECT DISTINCT conversation_id
        FROM messages
        WHERE receiver_id = ?
        """,
        (seller_id,),
    )

    rows = cursor.fetchall()

    conversations = []

    for row in rows:
        conv_id = row["conversation_id"]
        parts = conv_id.split("_")

        # Expect: ["conv", buyerId, sellerIdInConv, itemId]
        if len(parts) != 4 or parts[0] != "conv":
            # Skip malformed conversation IDs
            continue

        try:
            buyer_id = int(parts[1])
            seller_id_in_conv = int(parts[2])
            item_id = int(parts[3])
        except ValueError:
            # Skip if any part isn't an int
            continue

        # Make sure this convo is really for this seller
        if seller_id_in_conv != seller_id:
            continue

        # Look up buyer username
        cursor.execute(
            "SELECT username FROM users WHERE id = ?",
            (buyer_id,),
        )
        buyer_row = cursor.fetchone()
        if not buyer_row:
            continue
        buyer_username = buyer_row["username"]

        # Look up item title
        cursor.execute(
            "SELECT title FROM items WHERE id = ?",
            (item_id,),
        )
        item_row = cursor.fetchone()
        if not item_row:
            continue
        item_title = item_row["title"]

        conversations.append(
            {
                "buyer_id": buyer_id,
                "buyer_username": buyer_username,
                "item_id": item_id,
                "item_title": item_title,
                "conversation_id": conv_id,
            }
        )

    conn.close()

    return jsonify({"status": "success", "data": {"conversations": conversations}}), 200
