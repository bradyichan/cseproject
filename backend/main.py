"""
Module: main.py
Description: Initializes the Flask application, registers all blueprints,
and configures Swagger and CORS for the Marketplace API.
Author: Team 22 - CSE 2102
Date: 2025-10-27
"""
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flasgger import Swagger

# Correct imports based on your folder structure
from backend.db.database import init_db
from backend.users import users_bp
from backend.items import items_bp
from backend.search import search_bp
from backend.bidding import bidding_bp
from backend.payment import payment_bp
from backend.messaging import messaging_bp


# Initialize Flask
app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5173", "http://localhost:5173"])
swagger = Swagger(app)

# Register blueprints
app.register_blueprint(users_bp)
app.register_blueprint(items_bp)
app.register_blueprint(search_bp)
app.register_blueprint(bidding_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(messaging_bp)

# File serving endpoint
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """upload file"""
    upload_folder = os.path.join(os.path.dirname(__file__), "uploads")
    return send_from_directory(upload_folder, filename)

# Root endpoint
@app.route("/")
def home():
    """Home page"""
    return jsonify({
        "message": "Marketplace API is running",
        "endpoints": [
            "/users",
            "/items",
            "/search",
            "/bidding",
            "/payment",
            "/messages",
            "/uploads/<filename>"
        ]
    }), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=6767, debug=True)
