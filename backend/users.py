"""
Module: users.py
Description: Manages user registration, login, and profile retrieval using
SQLite database for Milestone 6 of the Marketplace project.
Author: Team 22 - CSE 2102
Date: 2025-11-02
"""

from datetime import datetime
from flask import Blueprint, jsonify, request
from backend.db.database import get_connection

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/register", methods=["POST"])
def register_user():
    """
    Register a new user.
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: UserRegister
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
    responses:
      201:
        description: User successfully registered
      400:
        description: Missing or invalid fields
    """
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({
            "status": "error",
            "error": {"code": "MISSING_FIELDS",
                      "message": "Username, email, and password are required."}
        }), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        )
        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "error": {"code": "USER_EXISTS",
                          "message": "Username or email already registered."}
            }), 400

        cursor.execute(
            "INSERT INTO users (username, email, password, joined) VALUES (?, ?, ?, ?)",
            (username, email, password, datetime.now().strftime("%Y-%m-%d"))
        )
        conn.commit()
        user_id = cursor.lastrowid
        return jsonify({
            "status": "success",
            "data": {
                "userId": user_id,
                "username": username,
                "email": email
            }
        }), 201
    except Exception as err:
        return jsonify({
            "status": "error",
            "error": {"code": "DB_ERROR", "message": str(err)}
        }), 500
    finally:
        conn.close()


@users_bp.route("/login", methods=["POST"])
def login_user():
    """Log in an existing user."""
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not all([username, password]):
        return jsonify({
            "status": "error",
            "error": {"code": "MISSING_FIELDS",
                      "message": "Username and password required."}
        }), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password, email FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({
            "status": "error",
            "error": {"code": "NOT_FOUND", "message": "User not found."}
        }), 404

    if row["password"] != password:
        return jsonify({
            "status": "error",
            "error": {"code": "INVALID_PASSWORD",
                      "message": "Incorrect password."}
        }), 401

    return jsonify({
        "status": "success",
        "data": {
            "userId": row["id"],
            "username": username,
            "email": row["email"]
        }
    }), 200


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user_profile(user_id):
    """Retrieve one user's profile by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, joined FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({
            "status": "error",
            "error": {"code": "NOT_FOUND", "message": "User not found."}
        }), 404

    return jsonify({
        "status": "success",
        "data": {
            "userId": user["id"],
            "username": user["username"],
            "email": user["email"],
            "joined": user["joined"]
        }
    }), 200


@users_bp.route("/all", methods=["GET"])
def get_all_users():
    """Return all registered users."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, joined FROM users")
    rows = cursor.fetchall()
    conn.close()

    users_list = [
        {"userId": row["id"], "username": row["username"],
         "email": row["email"], "joined": row["joined"]}
        for row in rows
    ]
    return jsonify({
        "status": "success",
        "data": {"users": users_list}
    }), 200
