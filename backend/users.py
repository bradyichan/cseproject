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

# ---------------------------------------------------------------------
# POST /users/register
# ---------------------------------------------------------------------
@users_bp.route("/register", methods=["POST"])
def register_user():
    """
    Register a new user
    ---
    tags: [Users]
    summary: Create a new user account
    description: Create a user with a unique username and email.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [username, email, password]
            properties:
              username: {type: string, example: "sam_mason"}
              email: {type: string, example: "sam@example.com"}
              password: {type: string, example: "hunter2"}
    responses:
      201:
        description: User successfully registered
        content:
          application/json:
            schema:
              type: object
              properties:
                status: {type: string, example: success}
                data:
                  type: object
                  properties:
                    userId: {type: integer, example: 12}
                    username: {type: string, example: "sam_mason"}
                    email: {type: string, example: "sam@example.com"}
      400:
        description: Missing fields or user already exists
      500:
        description: Database error
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
            "data": {"userId": user_id, "username": username, "email": email}
        }), 201
    except ValueError as err:
        return handle_db_error(err)
    finally:
        conn.close()

def handle_db_error(error):
    """Handles errors to prevent pylint from getting mad over exception"""
    return jsonify({
        "status": "error",
        "error": {"code": "DB_ERROR", "message": str(error)}
    }), 500


# ---------------------------------------------------------------------
# POST /users/login
# ---------------------------------------------------------------------
@users_bp.route("/login", methods=["POST"])
def login_user():
    """
    Log in a user
    ---
    tags: [Users]
    summary: Authenticate a user with username and password
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [username, password]
            properties:
              username: {type: string, example: "sam_mason"}
              password: {type: string, example: "hunter2"}
    responses:
      200:
        description: Login successful
        content:
          application/json:
            schema:
              type: object
              properties:
                status: {type: string, example: success}
                data:
                  type: object
                  properties:
                    userId: {type: integer, example: 12}
                    username: {type: string, example: "sam_mason"}
                    email: {type: string, example: "sam@example.com"}
      400:
        description: Missing fields
      401:
        description: Incorrect password
      404:
        description: User not found
    """
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
        "data": {"userId": row["id"], "username": username, "email": row["email"]}
    }), 200


# ---------------------------------------------------------------------
# GET /users/<user_id>
# ---------------------------------------------------------------------
@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user_profile(user_id):
    """
    Get user profile by ID
    ---
    tags: [Users]
    summary: Retrieve one user's profile by ID
    parameters:
      - name: user_id
        in: path
        required: true
        schema: {type: integer}
    responses:
      200:
        description: User profile returned
        content:
          application/json:
            schema:
              type: object
              properties:
                status: {type: string, example: success}
                data:
                  type: object
                  properties:
                    userId: {type: integer, example: 12}
                    username: {type: string, example: "sam_mason"}
                    email: {type: string, example: "sam@example.com"}
                    joined: {type: string, example: "2025-10-01"}
      404:
        description: User not found
    """
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


# ---------------------------------------------------------------------
# GET /users/all
# ---------------------------------------------------------------------
@users_bp.route("/all", methods=["GET"])
def get_all_users():
    """
    Get all users
    ---
    tags: [Users]
    summary: Return all registered users
    responses:
      200:
        description: List of users
        content:
          application/json:
            schema:
              type: object
              properties:
                status: {type: string, example: success}
                data:
                  type: object
                  properties:
                    users:
                      type: array
                      items:
                        type: object
                        properties:
                          userId: {type: integer, example: 12}
                          username: {type: string, example: "sam_mason"}
                          email: {type: string, example: "sam@example.com"}
                          joined: {type: string, example: "2025-10-01"}
    """
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
    return jsonify({"status": "success", "data": {"users": users_list}}), 200
