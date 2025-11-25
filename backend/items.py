"""
Module: items.py
Description: Full item CRUD with image upload, image serving, and seller username.
Author: Team 22 - CSE 2102
"""

import sqlite3
import os
from datetime import datetime
from flask import Blueprint, jsonify, request, send_from_directory

items_bp = Blueprint("items", __name__, url_prefix="/items")

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "marketplace.db")
IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)


def get_db_connection():
    """Return a SQLite DB connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------
# Serve images
# ---------------------------------------------------------
@items_bp.route("/image/<filename>")
def serve_image(filename):
    """Serve an uploaded item image by filename."""
    return send_from_directory(IMAGE_FOLDER, filename)


# ---------------------------------------------------------
# POST /items/add
# Create a new item
# ---------------------------------------------------------
@items_bp.route("/add", methods=["POST"])
def add_item():
    """Create a new item with optional image upload."""
    image_filename = None

    if request.content_type and request.content_type.startswith("multipart/form-data"):
        form = request.form
        data = form.to_dict()
        image = request.files.get("image")

        if image:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            image_filename = f"{timestamp}_{image.filename}"
            image.save(os.path.join(IMAGE_FOLDER, image_filename))
            data["image_filename"] = image_filename
    else:
        data = request.get_json() or {}

    required = ["title", "description", "category", "price", "location", "seller_id"]
    if not all(field in data for field in required):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    created_at = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO items (
            title, description, category, price, location,
            seller_id, created_at, image_filename
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["title"],
            data["description"],
            data["category"],
            float(data["price"]),
            data["location"],
            int(data["seller_id"]),
            created_at,
            data.get("image_filename"),
        ),
    )

    conn.commit()
    item_id = cursor.lastrowid
    conn.close()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "item_id": item_id,
                    "title": data["title"],
                    "price": float(data["price"]),
                    "image_filename": data.get("image_filename"),
                    "created_at": created_at,
                },
            }
        ),
        201,
    )


# ---------------------------------------------------------
# GET /items/all
# Return all items
# ---------------------------------------------------------
@items_bp.route("/all", methods=["GET"])
def get_all_items():
    """Return all items, including seller username."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            items.id AS item_id,
            items.title,
            items.description,
            items.category,
            items.price,
            items.location,
            items.seller_id,
            items.created_at,
            items.image_filename,
            users.username AS seller_username
        FROM items
        LEFT JOIN users ON items.seller_id = users.id
        ORDER BY items.created_at DESC
        """
    )

    items = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"status": "success", "data": {"items": items}}), 200


# ---------------------------------------------------------
# GET /items/seller/<seller_id>
# ---------------------------------------------------------
@items_bp.route("/seller/<int:seller_id>", methods=["GET"])
def get_items_by_seller(seller_id):
    """Return all items created by a given seller."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            items.id AS item_id,
            items.title,
            items.description,
            items.category,
            items.price,
            items.location,
            items.seller_id,
            items.created_at,
            items.image_filename,
            users.username AS seller_username
        FROM items
        LEFT JOIN users ON items.seller_id = users.id
        WHERE items.seller_id = ?
        ORDER BY items.created_at DESC
        """,
        (seller_id,),
    )

    items = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"status": "success", "data": {"items": items}}), 200


# ---------------------------------------------------------
# GET /items/<item_id>
# ---------------------------------------------------------
@items_bp.route("/<int:item_id>", methods=["GET"])
def get_item_by_id(item_id):
    """Return a single item by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            items.id AS item_id,
            items.title,
            items.description,
            items.category,
            items.price,
            items.location,
            items.seller_id,
            items.created_at,
            items.image_filename,
            users.username AS seller_username
        FROM items
        LEFT JOIN users ON items.seller_id = users.id
        WHERE items.id = ?
        """,
        (item_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"status": "error", "message": "Item not found"}), 404

    return jsonify({"status": "success", "data": dict(row)}), 200


# ---------------------------------------------------------
# PUT /items/update/<item_id>
# ---------------------------------------------------------
@items_bp.route("/update/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    """Update editable item fields (title, description, category, price, location)."""
    data = request.get_json() or {}
    allowed_fields = ["title", "description", "category", "price", "location"]

    updates = {key: data[key] for key in data if key in allowed_fields}
    if not updates:
        return jsonify({"status": "error", "message": "No valid fields to update"}), 400

    set_clause = ", ".join(f"{field} = ?" for field in updates.keys())
    values = list(updates.values()) + [item_id]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE items SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()

    return jsonify(
        {"status": "success", "data": {"item_id": item_id, "updated_fields": list(updates)}}
    ), 200


# ---------------------------------------------------------
# DELETE /items/delete/<item_id>
# ---------------------------------------------------------
@items_bp.route("/delete/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Delete an item by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"status": "error", "message": "Item not found"}), 404

    return jsonify({"status": "success", "message": f"Item {item_id} deleted"}), 200


# ---------------------------------------------------------
# GET /items/search
# ---------------------------------------------------------
@items_bp.route("/search", methods=["GET"])
def search_items():
    """Search items by title or category."""
    query = request.args.get("query", "").strip()

    if not query:
        return jsonify({"status": "error", "message": "Missing search query"}), 400

    search_term = f"%{query}%"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            items.id AS item_id,
            items.title,
            items.description,
            items.category,
            items.price,
            items.location,
            items.seller_id,
            items.created_at,
            items.image_filename,
            users.username AS seller_username
        FROM items
        LEFT JOIN users ON items.seller_id = users.id
        WHERE items.title LIKE ? OR items.category LIKE ?
        ORDER BY items.created_at DESC
        """,
        (search_term, search_term),
    )

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"status": "success", "data": {"results": results}}), 200
