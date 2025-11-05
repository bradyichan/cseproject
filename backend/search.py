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


# ---------------------------------------------------------------------
# GET /search/
# ---------------------------------------------------------------------
@search_bp.route("/", methods=["GET"])
def global_search():
    """
    Global search
    ---
    tags:
      - Search
    summary: Search across items, users, and bids
    description: |
      Perform a global keyword search that looks across all key database tables:
      - **Items** → title, description, category  
      - **Users** → username, email  
      - **Bids** → amount, status
    parameters:
      - name: query
        in: query
        required: true
        schema:
          type: string
        description: Keyword to search for (matches partial text)
        example: camera
    responses:
      200:
        description: Combined search results returned successfully
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
                    items:
                      type: array
                      items:
                        type: object
                        properties:
                          item_id: {type: integer, example: 5}
                          title: {type: string, example: "Canon DSLR Camera"}
                          price: {type: number, example: 499.99}
                    users:
                      type: array
                      items:
                        type: object
                        properties:
                          user_id: {type: integer, example: 3}
                          username: {type: string, example: "john_doe"}
                          email: {type: string, example: "john@example.com"}
                    bids:
                      type: array
                      items:
                        type: object
                        properties:
                          bid_id: {type: integer, example: 15}
                          item_id: {type: integer, example: 5}
                          amount: {type: number, example: 325.00}
                          status: {type: string, example: pending}
      400:
        description: Missing search query
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