# tests/test_users.py
import copy
import re

import pytest
from flask import Flask

import users  # your users.py module


@pytest.fixture(scope="function")
def app_client():
    """
    Fresh Flask test client with a clean copy of users.users per test.
    Restores globals after each test to ensure isolation.
    """
    original_users = copy.deepcopy(users.users)

    app = Flask(__name__)
    app.register_blueprint(users.users_bp)
    client = app.test_client()

    yield client

    users.users.clear()
    users.users.update(copy.deepcopy(original_users))


def test_register_requires_fields(app_client):
    r = app_client.post("/users/register", json={"username": "sam", "password": "x"})
    assert r.status_code == 400
    j = r.get_json()
    assert j["status"] == "error"
    assert "Missing" in j["message"]


def test_register_duplicate_username(app_client):
    # 'alex' exists in seed data
    r = app_client.post("/users/register", json={
        "username": "alex", "password": "whatever", "email": "x@y.com"
    })
    assert r.status_code == 400
    j = r.get_json()
    assert j["status"] == "error"
    assert "exists" in j["message"].lower()


def test_register_success_sets_joined_and_stores_user(app_client):
    payload = {"username": "sam", "password": "pw123", "email": "sam@example.com"}
    r = app_client.post("/users/register", json=payload)
    assert r.status_code == 201
    j = r.get_json()
    assert j["status"] == "registered"
    assert j["username"] == "sam"

    # User stored in module state with YYYY-MM-DD joined date
    u = users.users["sam"]
    assert u["email"] == "sam@example.com"
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", u["joined"])


def test_login_missing_fields(app_client):
    r = app_client.post("/users/login", json={"username": "alex"})
    assert r.status_code == 400
    j = r.get_json()
    assert j["status"] == "error"
    assert "Missing username or password" in j["message"]


def test_login_user_not_found(app_client):
    r = app_client.post("/users/login", json={"username": "nope", "password": "x"})
    assert r.status_code == 404
    j = r.get_json()
    assert j["status"] == "error"
    assert "not found" in j["message"].lower()


def test_login_incorrect_password(app_client):
    r = app_client.post("/users/login", json={"username": "alex", "password": "wrong"})
    assert r.status_code == 401
    j = r.get_json()
    assert j["status"] == "error"
    assert "incorrect password" in j["message"].lower()


def test_login_success_returns_limited_user_fields(app_client):
    r = app_client.post("/users/login", json={"username": "alex", "password": "test123"})
    assert r.status_code == 200
    j = r.get_json()
    assert j["status"] == "success"
    assert "Welcome back, alex!" in j["message"]
    user_info = j["user"]
    assert user_info["username"] == "alex"
    assert user_info["email"] == "alex@example.com"
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", user_info["joined"])
    # Ensure password is NOT returned
    assert "password" not in user_info


def test_get_user_profile_ok_and_not_found(app_client):
    ok = app_client.get("/users/alex")
    assert ok.status_code == 200
    j = ok.get_json()
    assert j["username"] == "alex"
    assert j["email"] == "alex@example.com"

    nf = app_client.get("/users/ghost")
    assert nf.status_code == 404
    assert nf.get_json()["error"] == "User not found"


def test_get_all_users_lists_every_user(app_client):
    # Baseline should include 'alex'
    resp = app_client.get("/users/all")
    assert resp.status_code == 200
    data = resp.get_json()
    usernames = {u["username"] for u in data["users"]}
    assert "alex" in usernames

    # Register a new user then check again
    app_client.post("/users/register", json={
        "username": "sam", "password": "pw", "email": "sam@example.com"
    })
    resp2 = app_client.get("/users/all")
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    usernames2 = {u["username"] for u in data2["users"]}
    assert {"alex", "sam"}.issubset(usernames2)
