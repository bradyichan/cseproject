"""
Module: bidding.py
Description: Handles bid placement, retrieval, and acceptance logic for the
Marketplace API using SQLite for persistence.
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
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------
#  POST /bidding/place
# ---------------------------------------------------------------------
@bidding_bp.route("/place", methods=["POST"])
def place_bid():
    # pylint: disable=duplicate-code
    """
    Place a new bid
    ---
    tags:
      - Bidding
    summary: Submit a new bid for a given item
    description: |
      Create a new bid by providing `item_id`, `bidder_id`, and `amount`.
      The bid will be recorded in the database with a `pending` status until accepted.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [item_id, bidder_id, amount]
            properties:
              item_id:
                type: integer
                example: 12
              bidder_id:
                type: integer
                example: 5
              amount:
                type: number
                example: 250.50
    responses:
      201:
        description: Bid successfully created
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
                    bid_id:
                      type: integer
                      example: 44
                    item_id:
                      type: integer
                      example: 12
                    bidder_id:
                      type: integer
                      example: 5
                    amount:
                      type: number
                      example: 250.5
                    status:
                      type: string
                      example: pending
                    timestamp:
                      type: string
                      example: "2025-11-03T19:00:00"
      400:
        description: Missing required fields
    """
    # pylint: enable=duplicate-code
    data = request.get_json() or {}
    required_fields = ["item_id", "bidder_id", "amount"]
    if not all(f in data for f in required_fields):
        return jsonify({
            "status": "error",
            "message": "Missing required fields"
        }), 400

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


# ---------------------------------------------------------------------
#  GET /bidding/item/<item_id>
# ---------------------------------------------------------------------
@bidding_bp.route("/item/<int:item_id>", methods=["GET"])
def get_bids_for_item(item_id):
    """
    Get bids for an item
    ---
    tags:
      - Bidding
    summary: Retrieve all bids for a specific item
    parameters:
      - name: item_id
        in: path
        required: true
        schema:
          type: integer
        description: The ID of the item to retrieve bids for
    responses:
      200:
        description: List of bids for the specified item
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
                    bids:
                      type: array
                      items:
                        type: object
                        properties:
                          bid_id:
                            type: integer
                            example: 3
                          bidder_id:
                            type: integer
                            example: 9
                          amount:
                            type: number
                            example: 125.0
                          status:
                            type: string
                            example: pending
                          timestamp:
                            type: string
                            example: "2025-11-04T12:30:00"
    """
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
    """
    Accept a bid
    ---
    tags:
      - Bidding
    summary: Accept a bid and reject others for the same item
    parameters:
      - name: bid_id
        in: path
        required: true
        schema:
          type: integer
        description: The ID of the bid to accept
    responses:
      200:
        description: Bid accepted successfully
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
                    bid_id:
                      type: integer
                      example: 7
                    item_id:
                      type: integer
                      example: 12
                    status:
                      type: string
                      example: accepted
      404:
        description: Bid not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT item_id FROM bids WHERE id = ?", (bid_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "Bid not found"}), 404

    item_id = row["item_id"]
    cursor.execute("UPDATE bids SET status = 'accepted' WHERE id = ?", (bid_id,))
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
    """
    Get highest bid
    ---
    tags:
      - Bidding
    summary: Retrieve the highest bid for a specific item
    parameters:
      - name: item_id
        in: path
        required: true
        schema:
          type: integer
        description: The ID of the item
    responses:
      200:
        description: Highest bid for this item
      404:
        description: No bids found
    """
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


# ---------------------------------------------------------------------
#  GET /bidding/history/<username>
# ---------------------------------------------------------------------
@bidding_bp.route("/history/<string:username>", methods=["GET"])
def user_bid_history(username):
    """
    User bid history
    ---
    tags:
      - Bidding
    summary: Retrieve all bids placed by a specific user
    parameters:
      - name: username
        in: path
        required: true
        schema:
          type: string
        description: The username to retrieve bid history for
    responses:
      200:
        description: A list of bids made by the user
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: "sam_mason"
                bids:
                  type: array
                  items:
                    type: object
                    properties:
                      item_id:
                        type: integer
                        example: 10
                      amount:
                        type: number
                        example: 175.25
                      timestamp:
                        type: string
                        example: "2025-11-04T18:00:00"
    """
    bids = []
    user_bids = [b for b in bids if b["bidder"] == username]
    return jsonify({"username": username, "bids": user_bids}), 200
