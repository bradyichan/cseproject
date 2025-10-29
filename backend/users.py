"""
Module: users.py
Description: Manages user registration, login, and profile retrieval using
mock data for Milestone 5 of the Marketplace project.
Author: Team XX - CSE 2102
Date: 2025-10-27
"""
from datetime import datetime
from flask import Blueprint, jsonify, request

users_bp = Blueprint("users", __name__, url_prefix="/users")

# Mock user data (username: dict)
users = {
    "alex": {
        "username": "alex",
        "password": "test123",  # plain mock password
        "email": "alex@example.com",
        "joined": "2025-10-27"
    }
}


@users_bp.route("/register", methods=["POST"])
def register_user():
    """Register a new user."""
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not all([username, password, email]):
        return jsonify({"status": "error", "message": "Missing username, password, or email"}), 400

    if username in users:
        return jsonify({"status": "error", "message": "Username already exists"}), 400

    users[username] = {
        "username": username,
        "password": password,
        "email": email,
        "joined": datetime.now().strftime("%Y-%m-%d")
    }

    return jsonify({"status": "registered", "username": username}), 201


@users_bp.route("/login", methods=["POST"])
def login_user():
    """Log in an existing user."""
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not all([username, password]):
        return jsonify({"status": "error", "message": "Missing username or password"}), 400

    user = users.get(username)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    if password != user["password"]:
        return jsonify({"status": "error", "message": "Incorrect password"}), 401

    return jsonify({
        "status": "success",
        "message": f"Welcome back, {username}!",
        "user": {
            "username": user["username"],
            "email": user["email"],
            "joined": user["joined"]
        }
    }), 200


@users_bp.route("/<username>", methods=["GET"])
def get_user_profile(username):
    """Get one user's profile."""
    user = users.get(username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "username": user["username"],
        "email": user["email"],
        "joined": user["joined"]
    }), 200


@users_bp.route("/all", methods=["GET"])
def get_all_users():
    """Return all mock users (for testing)."""
    user_list = [
        {"username": u, "email": info["email"], "joined": info["joined"]}
        for u, info in users.items()
    ]
    return jsonify({"users": user_list}), 200
