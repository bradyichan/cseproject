import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import sqlite3
import pytest
from flask import Flask
from backend.payment import payment_bp, get_db_connection


@pytest.fixture(scope="function")
def app_client(tmp_path):
    """Spin up a Flask app with a temporary SQLite DB for each test."""
    app = Flask(__name__)
    app.register_blueprint(payment_bp)

    # Create temp DB
    test_db = tmp_path / "test_marketplace.db"
    os.makedirs(test_db.parent, exist_ok=True)

    from backend import payment
    payment.DB_PATH = str(test_db)

    # Create schema
    conn = sqlite3.connect(str(test_db))
    c = conn.cursor()
    c.execute("""
        CREATE TABLE payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            payment_method_id TEXT NOT NULL,
            card_last4 TEXT NOT NULL,
            expiry_date TEXT NOT NULL,
            verified INTEGER NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            buyer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            purchased_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------

def test_validate_payment_success(app_client):
    """POST /payment/validate should accept valid credentials."""
    payload = {
        "paymentMethodId": "visa_1234",
        "userId": 1,
        "cardNumber": "4242 4242 4242 4242",
        "cvv": "123",
        "expiryDate": "12/27"
    }
    resp = app_client.post("/payment/validate", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["data"]["valid"] is True


def test_validate_payment_invalid_card(app_client):
    """Invalid card number or CVV should return 400."""
    payload = {
        "paymentMethodId": "visa_5678",
        "userId": 1,
        "cardNumber": "123",
        "cvv": "abc",
        "expiryDate": "01/30"
    }
    resp = app_client.post("/payment/validate", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["status"] == "error"


def test_validate_payment_missing_fields(app_client):
    """Missing required fields should return 400."""
    resp = app_client.post("/payment/validate", json={"userId": 1})
    assert resp.status_code == 400
    assert resp.get_json()["status"] == "error"


def test_create_purchase_success(app_client):
    """POST /payment/purchase should create a transaction if verified."""
    # insert verified payment
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO payments (user_id, payment_method_id, card_last4, expiry_date, verified)
        VALUES (1, 'visa_1234', '4242', '12/27', 1)
    """)
    conn.commit()
    conn.close()

    payload = {
        "itemId": 101,
        "userId": 1,
        "paymentMethodId": "visa_1234",
        "amount": 59.99
    }
    resp = app_client.post("/payment/purchase", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["status"] == "unshipped"
    assert "transactionId" in data


def test_create_purchase_not_verified(app_client):
    """Should fail if no verified payment exists."""
    payload = {
        "itemId": 202,
        "userId": 2,
        "paymentMethodId": "visa_9999",
        "amount": 100.0
    }
    resp = app_client.post("/payment/purchase", json=payload)
    assert resp.status_code == 400
    assert "verified" in resp.get_json()["message"].lower() or "payment" in resp.get_json()["message"].lower()


def test_get_payment_history_empty(app_client):
    """GET /payment/history/<user_id> should return empty array initially."""
    resp = app_client.get("/payment/history/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["transactions"] == []


def test_refund_transaction_success(app_client):
    """PUT /payment/refund/<transaction_id> should mark transaction refunded."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO transactions (item_id, buyer_id, amount, status, purchased_at)
        VALUES (10, 1, 99.99, 'unshipped', '2025-11-11T00:00:00')
    """)
    conn.commit()
    tid = c.lastrowid
    conn.close()

    resp = app_client.put(f"/payment/refund/{tid}")
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["status"] == "refunded"


def test_refund_transaction_not_found(app_client):
    """Refund nonexistent transaction should return 404."""
    resp = app_client.put("/payment/refund/9999")
    assert resp.status_code == 404
    assert resp.get_json()["status"] == "error"
