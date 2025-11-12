import sys, os

# Ensure backend package is discoverable before any imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import sqlite3
import pytest
from flask import Flask
from backend.messaging import messaging_bp, get_db_connection


@pytest.fixture(scope="function")
def app_client(tmp_path):
    """Spin up a Flask app with a temporary SQLite DB for each test."""
    app = Flask(__name__)
    app.register_blueprint(messaging_bp)

    # Temporary DB
    test_db = tmp_path / "test_marketplace.db"
    os.makedirs(test_db.parent, exist_ok=True)

    from backend import messaging
    messaging.DB_PATH = str(test_db)

    # Create schema
    conn = sqlite3.connect(str(test_db))
    c = conn.cursor()
    c.execute("""
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client


def insert_message(conversation_id="conv_1", sender_id=1, receiver_id=2,
                   content="Hi!", timestamp="2025-11-11T00:00:00"):
    """Helper to insert a message into the temporary DB."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO messages (conversation_id, sender_id, receiver_id, content, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (conversation_id, sender_id, receiver_id, content, timestamp))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------

def test_send_message_success(app_client):
    payload = {
        "conversation_id": "conv_123",
        "sender_id": 1,
        "receiver_id": 2,
        "content": "Hello!"
    }
    resp = app_client.post("/messaging/send", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["data"]["conversation_id"] == "conv_123"


def test_send_message_missing_fields(app_client):
    resp = app_client.post("/messaging/send", json={"sender_id": 1})
    assert resp.status_code == 400
    assert resp.get_json()["status"] == "error"


def test_get_conversation_success(app_client):
    insert_message("conv_1", 1, 2, "Hi!")
    insert_message("conv_1", 2, 1, "Hey back!")
    resp = app_client.get("/messaging/conversation/conv_1")
    assert resp.status_code == 200
    messages = resp.get_json()["data"]["conversation"]
    assert len(messages) == 2
    assert messages[0]["sender_id"] == 1


def test_get_conversation_not_found(app_client):
    resp = app_client.get("/messaging/conversation/conv_x")
    assert resp.status_code == 404
    assert resp.get_json()["status"] == "error"


def test_get_user_conversations(app_client):
    insert_message("conv_1", 1, 2, "Msg1")
    insert_message("conv_2", 2, 1, "Msg2")
    insert_message("conv_3", 3, 4, "Other users")
    resp = app_client.get("/messaging/user/1")
    assert resp.status_code == 200
    data = resp.get_json()["data"]["conversations"]
    assert set(data) == {"conv_1", "conv_2"}


def test_delete_message_success(app_client):
    insert_message("conv_1", 1, 2, "Delete me")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM messages LIMIT 1")
    msg_id = cur.fetchone()[0]
    conn.close()

    resp = app_client.delete(f"/messaging/delete/{msg_id}")
    assert resp.status_code == 200
    assert "deleted" in resp.get_json()["message"]


def test_delete_message_not_found(app_client):
    resp = app_client.delete("/messaging/delete/9999")
    assert resp.status_code == 404
    assert resp.get_json()["status"] == "error"
