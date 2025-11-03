# tests/test_messaging.py
import copy
import re

import pytest
from flask import Flask

import messaging  # your messaging.py module


@pytest.fixture(scope="function")
def app_client():
    """
    Fresh Flask test client with a clean copy of messaging.conversations.
    Restores globals after each test.
    """
    original_convos = copy.deepcopy(messaging.conversations)

    app = Flask(__name__)
    app.register_blueprint(messaging.messaging_bp)
    client = app.test_client()

    yield client

    # Restore module global
    messaging.conversations.clear()
    messaging.conversations.update(copy.deepcopy(original_convos))


def test_get_all_conversations_initial_empty(app_client):
    resp = app_client.get("/messages/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["chats"] == []


def test_send_message_requires_fields(app_client):
    r1 = app_client.post("/messages/chatA/send", json={"sender": "sam", "message": "hi"})
    r2 = app_client.post("/messages/chatA/send", json={"receiver": "alex", "message": "hi"})
    r3 = app_client.post("/messages/chatA/send", json={"sender": "sam", "receiver": "alex"})
    for r in (r1, r2, r3):
        assert r.status_code == 400
        assert "Missing" in r.get_json()["error"]


def test_send_message_creates_chat_and_returns_201(app_client):
    payload = {"sender": "sam", "receiver": "alex", "message": "hello"}
    resp = app_client.post("/messages/room1/send", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "sent"
    assert data["chat_id"] == "room1"
    msg = data["message"]
    assert msg["sender"] == "sam"
    assert msg["receiver"] == "alex"
    assert msg["message"] == "hello"
    # Timestamp present and formatted like YYYY-MM-DD HH:MM:SS
    assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", msg["timestamp"])

    # Chat should now appear in list of conversations
    chats = app_client.get("/messages/").get_json()["chats"]
    assert "room1" in chats


def test_get_conversation_ok_and_not_found(app_client):
    # Seed one chat with a message
    app_client.post(
        "/messages/room2/send",
        json={"sender": "sam", "receiver": "alex", "message": "first"},
    )

    ok = app_client.get("/messages/room2")
    assert ok.status_code == 200
    conv = ok.get_json()
    assert conv["chat_id"] == "room2"
    assert isinstance(conv["messages"], list)
    assert len(conv["messages"]) == 1
    assert conv["messages"][0]["message"] == "first"

    nf = app_client.get("/messages/nope")
    assert nf.status_code == 404
    assert nf.get_json()["error"] == "Chat not found"


def test_get_latest_message_ok_and_missing(app_client):
    # Missing chat -> 404
    missing = app_client.get("/messages/ghost/latest")
    assert missing.status_code == 404
    assert "No messages" in missing.get_json()["error"]

    # Send two messages, ensure latest is the second
    app_client.post(
        "/messages/room3/send",
        json={"sender": "sam", "receiver": "alex", "message": "one"},
    )
    app_client.post(
        "/messages/room3/send",
        json={"sender": "alex", "receiver": "sam", "message": "two"},
    )
    latest = app_client.get("/messages/room3/latest")
    assert latest.status_code == 200
    last = latest.get_json()
    assert last["message"] == "two"
    assert last["sender"] == "alex"
    assert last["receiver"] == "sam"


def test_latest_404_when_chat_exists_but_empty(app_client):
    # Manually create an empty conversation to hit the second 404 branch
    messaging.conversations["emptyRoom"] = []
    resp = app_client.get("/messages/emptyRoom/latest")
    assert resp.status_code == 404
    assert "No messages" in resp.get_json()["error"]
