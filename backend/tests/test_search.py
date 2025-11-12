import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import sqlite3
import pytest
from flask import Flask
from backend.search import search_bp, get_db_connection


@pytest.fixture(scope="function")
def app_client(tmp_path):
    """Spin up a Flask app with a temporary SQLite DB for each test."""
    app = Flask(__name__)
    app.register_blueprint(search_bp)

    # Temporary database
    test_db = tmp_path / "test_marketplace.db"
    os.makedirs(test_db.parent, exist_ok=True)

    from backend import search
    search.DB_PATH = str(test_db)

    # Create schema
    conn = sqlite3.connect(str(test_db))
    c = conn.cursor()
    c.execute("""
        CREATE TABLE items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            location TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE bids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            bidder_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------
# Helper: Insert sample data
# ---------------------------------------------------------------------
def insert_sample_data():
    conn = get_db_connection()
    c = conn.cursor()
    # Items
    c.execute("INSERT INTO items (title, description, category, price, location) VALUES (?, ?, ?, ?, ?)",
              ("Canon DSLR Camera", "Used camera in great condition", "Electronics", 499.99, "Storrs"))
    c.execute("INSERT INTO items (title, description, category, price, location) VALUES (?, ?, ?, ?, ?)",
              ("Desk Lamp", "Adjustable LED lamp", "Home", 25.00, "Hartford"))
    # Users
    c.execute("INSERT INTO users (username, email) VALUES (?, ?)", ("john_doe", "john@example.com"))
    c.execute("INSERT INTO users (username, email) VALUES (?, ?)", ("camera_guy", "cam@example.com"))
    # Bids
    c.execute("INSERT INTO bids (item_id, bidder_id, amount, status) VALUES (?, ?, ?, ?)", (1, 1, 325.00, "pending"))
    c.execute("INSERT INTO bids (item_id, bidder_id, amount, status) VALUES (?, ?, ?, ?)", (1, 2, 350.00, "accepted"))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------

def test_search_success(app_client):
    """GET /search/?query=camera should return matching results from all tables."""
    insert_sample_data()
    resp = app_client.get("/search/?query=camera")
    assert resp.status_code == 200
    data = resp.get_json()["data"]

    # Items should include the camera
    assert any("Camera" in i["title"] for i in data["items"])
    # Users should include 'camera_guy'
    assert any("camera_guy" in u["username"] for u in data["users"])
    # Bids should exist
    assert len(data["bids"]) >= 1


def test_search_by_category(app_client):
    """Should match results by category (case-insensitive)."""
    insert_sample_data()
    resp = app_client.get("/search/?query=home")
    assert resp.status_code == 200
    items = resp.get_json()["data"]["items"]
    assert any("Lamp" in i["title"] for i in items)


def test_search_missing_query(app_client):
    """GET /search/ with no query should return 400."""
    resp = app_client.get("/search/")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["status"] == "error"
    assert "Missing search query" in data["message"]
