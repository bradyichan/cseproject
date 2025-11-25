"""
Module: bidding.py
Description: Clean bidding system without modifying item price.
Author: Team 22 - CSE 2102
"""

import sqlite3
import os
from datetime import datetime
from flask import Blueprint, jsonify, request

bidding_bp = Blueprint("bidding", __name__, url_prefix="/bidding")

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "marketplace.db")


def get_db_connection():
    """Return a SQLite3 connection for bidding operations."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@bidding_bp.route("/place", methods=["POST"])
def place_bid():
    """Create a new bid. Does not modify the item price."""
    data = request.get_json() or {}
    required = ["item_id", "bidder_id", "amount"]

    if not all(f in data for f in required):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    item_id = int(data["item_id"])
    bidder_id = int(data["bidder_id"])
    amount = float(data["amount"])
    timestamp = datetime.now().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO bids (item_id, bidder_id, amount, status, timestamp)
        VALUES (?, ?, ?, 'pending', ?)
        """,
        (item_id, bidder_id, amount, timestamp),
    )

    bid_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "bid_id": bid_id,
                    "item_id": item_id,
                    "bidder_id": bidder_id,
                    "amount": amount,
                    "status": "pending",
                    "timestamp": timestamp,
                },
            }
        ),
        201,
    )


@bidding_bp.route("/item/<int:item_id>", methods=["GET"])
def get_bids_for_item(item_id):
    """Return all bids for an item sorted by highest amount."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id AS bid_id, bidder_id, amount, status, timestamp
        FROM bids
        WHERE item_id = ?
        ORDER BY amount DESC
        """,
        (item_id,),
    )

    bids = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"status": "success", "data": {"bids": bids}}), 200


@bidding_bp.route("/highest/<int:item_id>", methods=["GET"])
def get_highest_bid(item_id):
    """Return only the highest bid for the given item."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id AS bid_id, bidder_id, amount, timestamp
        FROM bids
        WHERE item_id = ?
        ORDER BY amount DESC
        LIMIT 1
        """,
        (item_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"status": "error", "message": "No bids"}), 404

    return jsonify({"status": "success", "data": dict(row)}), 200


@bidding_bp.route("/accept/<int:bid_id>", methods=["PUT"])
def accept_bid(bid_id):
    """Accept one bid and reject all others for that item."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT item_id FROM bids WHERE id = ?", (bid_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "Bid not found"}), 404

    item_id = row["item_id"]

    cursor.execute("UPDATE bids SET status = 'accepted' WHERE id = ?", (bid_id,))
    cursor.execute(
        "UPDATE bids SET status = 'rejected' WHERE item_id = ? AND id != ?",
        (item_id, bid_id),
    )

    conn.commit()
    conn.close()

    return (
        jsonify(
            {
                "status": "success",
                "data": {"bid_id": bid_id, "item_id": item_id, "status": "accepted"},
            }
        ),
        200,
    )


@bidding_bp.route("/history/<string:username>", methods=["GET"])
def user_bid_history(username):
    """Return all bids placed by a specific username."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT b.item_id, b.amount, b.timestamp
        FROM bids b
        JOIN users u ON b.bidder_id = u.id
        WHERE u.username = ?
        ORDER BY b.timestamp DESC
        """,
        (username,),
    )

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return (
        jsonify({"status": "success", "username": username, "bids": rows}),
        200,
    )
