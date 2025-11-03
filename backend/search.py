"""
Module: search.py
Description: Implements a lightweight global search across items, users, and bids
for the Marketplace API using SQLite queries.
Author: Team 22 - CSE 2102
Date: 2025-11-03
"""

from flask import Blueprint, jsonify, request
import sqlite3
import os

search_bp = Blueprint("search", __name__, url_prefix="/search")

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "marketplace.db")


def get_db_connection():
    """Establish connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@search_bp.route("/", methods=["GET"])
def global_search():
    """
    Perform a global search for a keyword across items, users, and bids.
    Example: /search/?query=camera
    """
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({
            "status": "error",
            "message": "Missing search query"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Search items
    cursor.execute("""
        SELECT id AS item_id, title, description, category, price, location
        FROM items
        WHERE title LIKE ? OR description LIKE ? OR category LIKE ?
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    items = [dict(row) for row in cursor.fetchall()]

    # Search users
    cursor.execute("""
        SELECT id AS user_id, username, email
        FROM users
        WHERE username LIKE ? OR email LIKE ?
    """, (f"%{query}%", f"%{query}%"))
    users = [dict(row) for row in cursor.fetchall()]

    # Search bids
    cursor.execute("""
        SELECT id AS bid_id, item_id, bidder_id, amount, status
        FROM bids
        WHERE CAST(amount AS TEXT) LIKE ? OR status LIKE ?
    """, (f"%{query}%", f"%{query}%"))
    bids = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "items": items,
            "users": users,
            "bids": bids
        }
    }), 200
