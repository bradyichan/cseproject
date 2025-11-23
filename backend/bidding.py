"""
Module: bidding.py
Description: Handles bid placement, retrieval, acceptance, and price-updating logic.
Author: Team 22 - CSE 2102
Date: 2025-11-03
"""

import sqlite3
import os
from datetime import datetime
from flask import Blueprint, jsonify, request

bidding_bp = Blueprint("bidding", __name__, url_prefix="/bidding")

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "marketplace.db")


def get_db_connection():
    """Create database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------
#  POST /bidding/place  (NEW BID + UPDATE ITEM PRICE)
# ---------------------------------------------------------------------
@bidding_bp.route("/place", methods=["POST"])
def place_bid():
    """
    Place a new bid AND update the item price automatically.
    Required JSON: { "item_id": int, "bidder_id": int, "amount": float }
    """
    data = request.get_json() or {}
    required = ["item_id", "bidder_id", "amount"]

    if not all(f in data for f in required):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    item_id = data["item_id"]
    bidder_id = data["bidder_id"]
    amount = float(data["amount"])
    timestamp = datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert bid
    cursor.execute("""
        INSERT INTO bids (item_id, bidder_id, amount, status, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (item_id, bidder_id, amount, "pending", timestamp))

    bid_id = cursor.lastrowid

    # 🚨 NEW FEATURE:
    # Update the item’s price to match the highest bid
    cursor.execute("""
        UPDATE items SET price = ?
        WHERE id = ?
    """, (amount, item_id))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "bid_id": bid_id,
            "item_id": item_id,
            "bidder_id": bidder_id,
            "amount": amount,
            "status": "pending",
            "timestamp": timestamp
        }
    }), 201


# ---------------------------------------------------------------------
#  GET /bidding/item/<item_id>
# ---------------------------------------------------------------------
@bidding_bp.route("/item/<int:item_id>", methods=["GET"])
def get_bids_for_item(item_id):
    """Return all bids for an item sorted by amount desc."""
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


# ---------------------------------------------------------------------
#  PUT /bidding/accept/<bid_id>
# ---------------------------------------------------------------------
@bidding_bp.route("/accept/<int:bid_id>", methods=["PUT"])
def accept_bid(bid_id):
    """Accept a specific bid and reject the rest."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if exists
    cursor.execute("SELECT item_id FROM bids WHERE id = ?", (bid_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "Bid not found"}), 404

    item_id = row["item_id"]

    # Accept this bid
    cursor.execute("UPDATE bids SET status = 'accepted' WHERE id = ?", (bid_id,))

    # Reject others
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


# ---------------------------------------------------------------------
#  GET /bidding/highest/<item_id>
# ---------------------------------------------------------------------
@bidding_bp.route("/highest/<int:item_id>", methods=["GET"])
def get_highest_bid(item_id):
    """Return the highest bid for an item."""
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

    return jsonify({"status": "success", "data": dict(row)}), 200


# ---------------------------------------------------------------------
#  GET /bidding/history/<username>
# ---------------------------------------------------------------------
@bidding_bp.route("/history/<string:username>", methods=["GET"])
def user_bid_history(username):
    """Bid history for a given user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bids.item_id, bids.amount, bids.timestamp
        FROM bids
        JOIN users ON bids.bidder_id = users.id
        WHERE users.username = ?
        ORDER BY bids.timestamp DESC
    """, (username,))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"username": username, "bids": rows}), 200
