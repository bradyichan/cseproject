"""
Module: items.py
Description: Full item CRUD with image upload + serving images.
Author: Team 22 - CSE 2102
"""

import sqlite3
import os
from datetime import datetime
from flask import Blueprint, jsonify, request, send_from_directory

items_bp = Blueprint("items", __name__, url_prefix="/items")

# DB PATH
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "marketplace.db")

# SAVE IMAGES HERE → backend/items/images
IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------
# SERVE IMAGES BACK TO FRONTEND
# ---------------------------------------------------------
@items_bp.route("/image/<filename>")
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)


# ---------------------------------------------------------
# POST /items/add  (JSON or multipart with image)
# ---------------------------------------------------------
@items_bp.route("/add", methods=["POST"])
def add_item():
    """Add item with optional image upload."""

    image_filename = None

    # If multipart (form-data with file)
    if request.content_type and request.content_type.startswith("multipart/form-data"):
        form = request.form
        data = form.to_dict()
        image = request.files.get("image")

        if image:
            image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}"
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
            data.get("image_filename"),  # may be None
        ),
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
            "image_filename": data.get("image_filename"),
            "created_at": created_at
        }
    }), 201


# ---------------------------------------------------------
# GET /items/all  (NOW RETURNS image_filename)
# ---------------------------------------------------------
@items_bp.route("/all", methods=["GET"])
def get_all_items():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id AS item_id,
            title,
            description,
            category,
            price,
            location,
            seller_id,
            created_at,
            image_filename
        FROM items
        ORDER BY created_at DESC
        """
    )

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"status": "success", "data": {"items": rows}}), 200


# ---------------------------------------------------------
# GET /items/<item_id>
# ---------------------------------------------------------
@items_bp.route("/<int:item_id>", methods=["GET"])
def get_item_by_id(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id AS item_id,
            title,
            description,
            category,
            price,
            location,
            seller_id,
            created_at,
            image_filename
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


# ---------------------------------------------------------
# PUT /items/update/<item_id>
# ---------------------------------------------------------
@items_bp.route("/update/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json() or {}
    allowed = ["title", "description", "category", "price", "location"]

    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"status": "error", "message": "No valid fields to update"}), 400

    set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
    values = list(updates.values()) + [item_id]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE items SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "data": {"item_id": item_id, "updated_fields": list(updates.keys())}
    }), 200


# ---------------------------------------------------------
# DELETE /items/delete/<item_id>
# ---------------------------------------------------------
@items_bp.route("/delete/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
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
    query = request.args.get("query", "").strip()

    if not query:
        return jsonify({"status": "error", "message": "Missing search query"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id AS item_id,
            title,
            description,
            category,
            price,
            location,
            seller_id,
            created_at,
            image_filename
        FROM items
        WHERE title LIKE ? OR category LIKE ?
        ORDER BY created_at DESC
        """,
        (f"%{query}%", f"%{query}%")
    )

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"status": "success", "data": {"results": results}}), 200
