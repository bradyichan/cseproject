"""
Pytest suite for bidding.py
Tests all bidding endpoints using a temporary SQLite database.
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import tempfile
import sqlite3
import pytest
from flask import Flask

from backend.bidding import bidding_bp, DB_PATH, get_db_connection

# ---------------------------------------------------------------------
#  FIXTURE: Flask test client + temporary DB
# ---------------------------------------------------------------------
@pytest.fixture(scope="function")
def app_client(tmp_path):
    """Spin up a Flask app with a temporary SQLite DB for each test."""
    app = Flask(__name__)
    app.register_blueprint(bidding_bp)

    # Create temp DB path
    test_db = tmp_path / "test_marketplace.db"
    os.makedirs(test_db.parent, exist_ok=True)

    # Monkeypatch the DB_PATH used by bidding.py
    from backend import bidding
    bidding.DB_PATH = str(test_db)

    # Create schema
    conn = sqlite3.connect(str(test_db))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE bids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            bidder_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------
#  Helper: Insert test bid rows
# ---------------------------------------------------------------------
def insert_bid(item_id, bidder_id, amount, status="pending", timestamp="2025-11-01T00:00:00"):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO bids (item_id, bidder_id, amount, status, timestamp) VALUES (?, ?, ?, ?, ?)",
        (item_id, bidder_id, amount, status, timestamp),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
#  TESTS
# ---------------------------------------------------------------------

def test_place_bid_success(app_client):
    """POST /bidding/place should create a new bid"""
    payload = {"item_id": 1, "bidder_id": 2, "amount": 50.5}
    resp = app_client.post("/bidding/place", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["data"]["item_id"] == 1
    assert data["data"]["bidder_id"] == 2
    assert data["data"]["amount"] == 50.5


def test_place_bid_missing_fields(app_client):
    """POST /bidding/place should return 400 if required fields are missing"""
    resp = app_client.post("/bidding/place", json={"item_id": 1})
    assert resp.status_code == 400
    assert resp.get_json()["status"] == "error"


def test_get_bids_for_item(app_client):
    """GET /bidding/item/<id> returns list of bids"""
    insert_bid(1, 10, 100)
    insert_bid(1, 20, 120)
    resp = app_client.get("/bidding/item/1")
    assert resp.status_code == 200
    data = resp.get_json()["data"]["bids"]
    assert len(data) == 2
    assert data[0]["amount"] >= data[1]["amount"]  # Sorted desc


def test_accept_bid_success(app_client):
    """PUT /bidding/accept/<id> should accept target bid and reject others"""
    insert_bid(1, 10, 100)
    insert_bid(1, 20, 200)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM bids WHERE amount = 200")
    bid_id = cur.fetchone()[0]
    conn.close()

    resp = app_client.put(f"/bidding/accept/{bid_id}")
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["status"] == "accepted"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM bids WHERE status='rejected'")
    rejected_count = cur.fetchone()[0]
    conn.close()
    assert rejected_count == 1


def test_accept_bid_not_found(app_client):
    """PUT /bidding/accept/<id> for nonexistent bid should return 404"""
    resp = app_client.put("/bidding/accept/999")
    assert resp.status_code == 404
    assert resp.get_json()["status"] == "error"


def test_get_highest_bid_ok(app_client):
    """GET /bidding/highest/<id> returns highest bid"""
    insert_bid(2, 10, 100)
    insert_bid(2, 11, 150)
    resp = app_client.get("/bidding/highest/2")
    assert resp.status_code == 200
    highest = resp.get_json()["data"]
    assert highest["amount"] == 150


def test_get_highest_bid_not_found(app_client):
    """GET /bidding/highest/<id> returns 404 when no bids exist"""
    resp = app_client.get("/bidding/highest/999")
    assert resp.status_code == 404


def test_user_bid_history_empty(app_client):
    """GET /bidding/history/<username> returns empty list (no in-memory data)"""
    resp = app_client.get("/bidding/history/sam")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["username"] == "sam"
    assert data["bids"] == []
