"""
Module: items.py
Description: Handles item creation, retrieval, update, and deletion
for the Marketplace API using SQLite for persistence.
Author: Team 22 - CSE 2102
Date: 2025-11-03
"""

import sqlite3
import os
from datetime import datetime
from flask import Blueprint, jsonify, request

items_bp = Blueprint("items", __name__, url_prefix="/items")

# Path to local SQLite database
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "marketplace.db")


def get_db_connection():
    """Establish connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------------------------------------------------
# POST /items/add (supports JSON and multipart/form-data)
# ---------------------------------------------------------------------
@items_bp.route("/add", methods=["POST"])
def add_item():
    """
    Add a new item (supports JSON or multipart/form-data)
    ---
    tags:
      - Items
    summary: Add a new item to the marketplace
    consumes:
      - application/json
    produces:
      - application/json

    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - description
            - category
            - price
            - location
            - seller_id
          properties:
            title:
              type: string
              example: "Desk Lamp"
            description:
              type: string
              example: "Adjustable LED lamp, great for studying."
            category:
              type: string
              example: "Home"
            price:
              type: number
              example: 25.99
            location:
              type: string
              example: "Storrs, CT"
            seller_id:
              type: integer
              example: 4

    responses:
      201:
        description: Item successfully created
      400:
        description: Missing required fields
    """
    data = request.get_json() or {}

    required_fields = ["title", "description", "category", "price", "location", "seller_id"]
    if not all(f in data for f in required_fields):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400


    # Save to DB
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO items (title, description, category, price, location, seller_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
        data["title"],
        data["description"],
        data["category"],
        data["price"],
        data["location"],
        data["seller_id"],
        created_at
    )
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "item_id": item_id,
            "title": data["title"],
            "price": data["price"],
            "created_at": created_at
        }
    }), 201


# ---------------------------------------------------------------------
# GET /items/all
# ---------------------------------------------------------------------
@items_bp.route("/all", methods=["GET"])
def get_all_items():
    """Retrieve all items in the marketplace."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id AS item_id, title, description, category, price, location, seller_id, created_at
        FROM items
        ORDER BY created_at DESC
        """
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"status": "success", "data": {"items": rows}}), 200


# ---------------------------------------------------------------------
# GET /items/<item_id>
# ---------------------------------------------------------------------
@items_bp.route("/<int:item_id>", methods=["GET"])
def get_item_by_id(item_id):
    """Retrieve a specific item by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id AS item_id, title, description, category, price, location, seller_id, created_at
        FROM items
        WHERE id = ?
        """,
        (item_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"status": "error", "message": "Item not found"}), 404

    return jsonify({"status": "success", "data": dict(row)}), 200


# ---------------------------------------------------------------------
# PUT /items/update/<item_id>
# ---------------------------------------------------------------------
@items_bp.route("/update/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    """Update one or more fields for an existing item."""
    data = request.get_json() or {}
    allowed = ["title", "description", "category", "price", "location"]
    updates = {k: v for k, v in data.items() if k in allowed}

    if not updates:
        return jsonify({"status": "error", "message": "No valid fields to update"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
    values = list(updates.values()) + [item_id]
    cursor.execute(f"UPDATE items SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()

    return jsonify(
        {
            "status": "success",
            "data": {"item_id": item_id, "updated_fields": list(updates.keys())},
        }
    ), 200


# ---------------------------------------------------------------------
# DELETE /items/delete/<item_id>
# ---------------------------------------------------------------------
@items_bp.route("/delete/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Delete an item listing from the marketplace."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"status": "error", "message": "Item not found"}), 404

    return jsonify({
        "status": "success",
        "message": f"Item {item_id} deleted"
    }), 200

# ---------------------------------------------------------------------
# GET /items/search
# ---------------------------------------------------------------------
@items_bp.route("/search", methods=["GET"])
def search_items():
    """Search for items by title or category."""
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"status": "error", "message": "Missing search query"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id AS item_id, title, description, category, price, location, seller_id
        FROM items
        WHERE title LIKE ? OR category LIKE ?
        ORDER BY created_at DESC
        """,
        (f"%{query}%", f"%{query}%"),
    )
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"status": "success", "data": {"results": results}}), 200
