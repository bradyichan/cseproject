# tests/test_payment.py
import copy
import re

import pytest
from flask import Flask

import payment  # your payment.py module


@pytest.fixture(scope="function")
def app_client():
    """
    Fresh Flask test client with clean copies of payment.verifications and payment.orders.
    Restores globals after each test to ensure isolation.
    """
    original_verifications = copy.deepcopy(payment.verifications)
    original_orders = copy.deepcopy(payment.orders)

    app = Flask(__name__)
    app.register_blueprint(payment.payment_bp)
    client = app.test_client()

    yield client

    # Restore module globals
    payment.verifications.clear()
    payment.verifications.update(copy.deepcopy(original_verifications))
    payment.orders.clear()
    payment.orders.extend(copy.deepcopy(original_orders))


def test_credentials_missing_fields_returns_400_and_token_created(app_client):
    resp = app_client.post("/payment/credentials", json={"card_number": "4242424242424242"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["status"] == "invalid"
    # Token should be returned even on invalid to allow retry
    assert re.match(r"^VERIF-\d{4}$", data["token"])
    # And verifications should have status=invalid
    assert payment.verifications[data["token"]]["status"] == "invalid"


def test_credentials_invalid_card_format(app_client):
    # Bad length + non-digit cvv
    payload = {"card_number": "1234 567", "cvv": "AB", "name": "Sam", "zip_code": "06511"}
    resp = app_client.post("/payment/credentials", json=payload)
    assert resp.status_code == 400
    j = resp.get_json()
    assert j["status"] == "invalid"
    assert "Invalid card info" in j["message"]


def test_credentials_valid_returns_200_and_verified_status(app_client):
    payload = {"card_number": "4242 4242 4242 4242", "cvv": "123", "name": "Sam", "zip_code": "06511"}
    resp = app_client.post("/payment/credentials", json=payload)
    assert resp.status_code == 200
    j = resp.get_json()
    assert j["status"] == "verified"
    assert re.match(r"^VERIF-\d{4}$", j["token"])
    assert payment.verifications[j["token"]]["status"] == "verified"


def test_tokens_increment_sequentially(app_client):
    p1 = {"card_number": "4242 4242 4242 4242", "cvv": "123", "name": "A", "zip_code": "00000"}
    p2 = {"card_number": "378282246310005", "cvv": "1234", "name": "B", "zip_code": "11111"}  # AmEx length 15
    t1 = app_client.post("/payment/credentials", json=p1).get_json()["token"]
    t2 = app_client.post("/payment/credentials", json=p2).get_json()["token"]
    # Numeric suffix increases
    n1 = int(t1.split("-")[1])
    n2 = int(t2.split("-")[1])
    assert n2 == n1 + 1


def test_confirm_missing_fields(app_client):
    resp = app_client.post("/payment/confirm", json={"token": "VERIF-0001"})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Missing required fields"


def test_confirm_rejects_unverified_token(app_client):
    # Create an invalid token via bad credentials
    bad = app_client.post("/payment/credentials", json={"card_number": "1", "cvv": "1", "name": "x", "zip_code": "y"}).get_json()
    token = bad["token"]
    assert payment.verifications[token]["status"] == "invalid"

    resp = app_client.post("/payment/confirm", json={
        "token": token, "item_id": 1, "amount": 10.0, "buyer": "sam"
    })
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Payment not verified"


def test_confirm_success_and_history(app_client):
    # First verify credentials to get a verified token
    verify = app_client.post("/payment/credentials", json={
        "card_number": "4242 4242 4242 4242",
        "cvv": "321",
        "name": "Sam Mason",
        "zip_code": "06511"
    })
    assert verify.status_code == 200
    token = verify.get_json()["token"]
    assert payment.verifications[token]["status"] == "verified"

    # Confirm payment
    confirm = app_client.post("/payment/confirm", json={
        "token": token,
        "item_id": 42,
        "amount": 19.99,
        "buyer": "sam"
    })
    assert confirm.status_code == 200
    j = confirm.get_json()
    assert j["status"] == "success"
    assert re.match(r"^CONFIRM-\d{4}$", j["confirmation_code"])

    # Order recorded
    assert len(payment.orders) == 1
    order = payment.orders[0]
    assert order["item_id"] == 42
    assert order["amount"] == 19.99
    assert order["buyer"] == "sam"
    assert order["confirmation_code"] == j["confirmation_code"]

    # History endpoint returns the order
    history = app_client.get("/payment/history")
    assert history.status_code == 200
    hist = history.get_json()
    assert isinstance(hist["orders"], list)
    assert len(hist["orders"]) == 1
    assert hist["orders"][0]["confirmation_code"] == j["confirmation_code"]
