import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import sqlite3
import pytest
from flask import Flask
from backend.items import items_bp, get_db_connection


@pytest.fixture(scope="function")
def app_client(tmp_path):
    """Spin up a Flask app with a temporary SQLite DB for each test."""
    app = Flask(__name__)
    app.register_blueprint(items_bp)

    # Temporary database
    test_db = tmp_path / "test_marketplace.db"
    os.makedirs(test_db.parent, exist_ok=True)

    from backend import items
    items.DB_PATH = str(test_db)

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
            location TEXT NOT NULL,
            seller_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            image_filename TEXT
        )
    """)
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client


def insert_item(title="Lamp", description="Nice", category="Home",
                price=10.0, location="Storrs", seller_id=1):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO items (title, description, category, price, location, seller_id, created_at, image_filename)
        VALUES (?, ?, ?, ?, ?, ?, '2025-11-11T00:00:00', NULL)
    """, (title, description, category, price, location, seller_id))
    conn.commit()
    conn.close()


def test_add_item_success(app_client):
    payload = {
        "title": "Desk Lamp",
        "description": "LED light",
        "category": "Home",
        "price": 25.5,
        "location": "CT",
        "seller_id": 7
    }
    r = app_client.post("/items/add", json=payload)
    assert r.status_code == 201
    assert r.get_json()["status"] == "success"


def test_add_item_missing_fields(app_client):
    r = app_client.post("/items/add", json={"title": "Incomplete"})
    assert r.status_code == 400
    assert r.get_json()["status"] == "error"


def test_get_item_by_id_found(app_client):
    insert_item("Chair", "Wooden", "Furniture", 50, "UConn", 3)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM items LIMIT 1")
    item_id = cur.fetchone()[0]
    conn.close()

    r = app_client.get(f"/items/{item_id}")
    assert r.status_code == 200
    assert r.get_json()["data"]["item_id"] == item_id


def test_get_item_not_found(app_client):
    r = app_client.get("/items/9999")
    assert r.status_code == 404


def test_update_item_success(app_client):
    insert_item("Old", "desc", "misc", 5, "CT", 2)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM items LIMIT 1")
    item_id = cur.fetchone()[0]
    conn.close()

    r = app_client.put(f"/items/update/{item_id}", json={"price": 99.99})
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert data["item_id"] == item_id
    assert "price" in data["updated_fields"]


def test_update_item_invalid(app_client):
    insert_item()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM items LIMIT 1")
    item_id = cur.fetchone()[0]
    conn.close()

    r = app_client.put(f"/items/update/{item_id}", json={"invalid": "oops"})
    assert r.status_code == 400


def test_delete_item_success(app_client):
    insert_item()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM items LIMIT 1")
    item_id = cur.fetchone()[0]
    conn.close()

    r = app_client.delete(f"/items/delete/{item_id}")
    assert r.status_code == 200
    assert "deleted" in r.get_json()["message"]


def test_delete_item_not_found(app_client):
    r = app_client.delete("/items/delete/999")
    assert r.status_code == 404


def test_search_items_ok(app_client):
    insert_item("Red Lamp", "desc", "Home", 10, "CT", 1)
    insert_item("Green Lamp", "desc", "Home", 20, "CT", 1)
    r = app_client.get("/items/search?query=Lamp")
    assert r.status_code == 200
    assert len(r.get_json()["data"]["results"]) >= 1


def test_search_items_missing_query(app_client):
    r = app_client.get("/items/search")
    assert r.status_code == 400


def test_get_all_items(app_client):
    insert_item("Desk", "desc", "Office", 50, "CT", 1)
    insert_item("Chair", "desc", "Office", 75, "CT", 2)
    r = app_client.get("/items/all")
    assert r.status_code == 200
    items = r.get_json()["data"]["items"]
    assert len(items) >= 2
