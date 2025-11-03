"""
Module: bidding.py
Description: Handles bid placement, retrieval, and acceptance logic for the
Marketplace API using SQLite for persistence.
Author: Team 22 - CSE 2102
Date: 2025-11-03
"""

from datetime import datetime
from flask import Blueprint, jsonify, request
import sqlite3
import os

bidding_bp = Blueprint("bidding", __name__, url_prefix="/bidding")

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "marketplace.db")


def get_db_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@bidding_bp.route("/place", methods=["POST"])
def place_bid():
    """
    Place a new bid for a given item.
    Expects JSON with: item_id, bidder_id, amount
    """
    data = request.get_json() or {}

    required_fields = ["item_id", "bidder_id", "amount"]
    if not all(f in data for f in required_fields):
        return jsonify({
            "status": "error",
            "message": "Missing required fields"
        }), 400

    # Insert bid into DB
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO bids (item_id, bidder_id, amount, status, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (data["item_id"], data["bidder_id"], data["amount"], "pending", timestamp))

    conn.commit()
    bid_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "bid_id": bid_id,
            "item_id": data["item_id"],
            "bidder_id": data["bidder_id"],
            "amount": data["amount"],
            "status": "pending",
            "timestamp": timestamp
        }
    }), 201


@bidding_bp.route("/item/<int:item_id>", methods=["GET"])
def get_bids_for_item(item_id):
    """Retrieve all bids for a specific item."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id AS bid_id, bidder_id, amount, status, timestamp
        FROM bids
        WHERE item_id = ?
        ORDER BY amount DESC
    """, (item_id,))
    bids = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        "status": "success",
        "data": {"bids": bids}
    }), 200


@bidding_bp.route("/accept/<int:bid_id>", methods=["PUT"])
def accept_bid(bid_id):
    """
    Accept a bid, mark others for the same item as rejected.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find which item this bid belongs to
    cursor.execute("SELECT item_id FROM bids WHERE id = ?", (bid_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "Bid not found"}), 404

    item_id = row["item_id"]

    # Accept this bid
    cursor.execute("UPDATE bids SET status = 'accepted' WHERE id = ?", (bid_id,))
    # Reject all others
    cursor.execute("""
        UPDATE bids SET status = 'rejected'
        WHERE item_id = ? AND id != ?
    """, (item_id, bid_id))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "data": {"bid_id": bid_id, "item_id": item_id, "status": "accepted"}
    }), 200


@bidding_bp.route("/highest/<int:item_id>", methods=["GET"])
def get_highest_bid(item_id):
    """Return the highest bid for a specific item."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id AS bid_id, bidder_id, amount, timestamp
        FROM bids
        WHERE item_id = ?
        ORDER BY amount DESC
        LIMIT 1
    """, (item_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"status": "error", "message": "No bids found"}), 404

    return jsonify({
        "status": "success",
        "data": dict(row)
    }), 200

@bidding_bp.route("/history/<string:username>", methods=["GET"])
def user_bid_history(username):
    """Return all bids placed by a given user."""
    user_bids = [b for b in bids if b["bidder"] == username]
    return jsonify({"username": username, "bids": user_bids}), 200
