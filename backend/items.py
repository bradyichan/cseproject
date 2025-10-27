"""
Module: items.py
Description: Provides CRUD endpoints for item listings including create,
read, update, and delete operations using mock item data.
Author: Team XX - CSE 2102
Date: 2025-10-27
"""

from flask import Blueprint, jsonify, request
from datetime import datetime

items_bp = Blueprint("items", __name__, url_prefix="/items")

# Mock item data
items = {
    1: {"id": 1, "title": "Gaming Laptop", "category": "Electronics", "price": 750, "seller": "alex", "status": "available"},
    2: {"id": 2, "title": "Vintage Lamp", "category": "Home Decor", "price": 40, "seller": "ethan", "status": "available"},
    3: {"id": 3, "title": "Mountain Bike", "category": "Sports", "price": 300, "seller": "alex", "status": "available"},
}

# Counter for next available item ID
next_id = {"value": 4}


@items_bp.route("/", methods=["GET"])
def get_all_items():
    """Return all listed items."""
    return jsonify({"count": len(items), "items": list(items.values())}), 200


@items_bp.route("/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Return one item by ID."""
    item = items.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@items_bp.route("/create", methods=["POST"])
def create_item():
    """Create a new mock item listing."""
    data = request.get_json() or {}

    title = data.get("title")
    category = data.get("category")
    price = data.get("price")
    seller = data.get("seller")

    if not all([title, category, price, seller]):
        return jsonify({"error": "Missing title, category, price, or seller"}), 400

    # Generate new ID safely (no global variable)
    new_id = next_id["value"]
    next_id["value"] += 1

    new_item = {
        "id": new_id,
        "title": title,
        "category": category,
        "price": float(price),
        "seller": seller,
        "status": "available",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    items[new_id] = new_item

    return jsonify({"status": "created", "item": new_item}), 201


@items_bp.route("/<int:item_id>/update", methods=["PUT"])
def update_item(item_id):
    """Update item details."""
    item = items.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json() or {}
    for field in ["title", "category", "price", "status"]:
        if field in data:
            item[field] = data[field]

    return jsonify({"status": "updated", "item": item}), 200


@items_bp.route("/<int:item_id>/delete", methods=["DELETE"])
def delete_item(item_id):
    """Remove an item listing."""
    if item_id not in items:
        return jsonify({"error": "Item not found"}), 404
    deleted = items.pop(item_id)
    return jsonify({"status": "deleted", "item": deleted}), 200


@items_bp.route("/seller/<string:username>", methods=["GET"])
def get_items_by_seller(username):
    """Return all items from a specific seller."""
    user_items = [item for item in items.values() if item["seller"] == username]
    return jsonify({"seller": username, "items": user_items}), 200
