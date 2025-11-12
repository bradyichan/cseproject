import sys, os
import sqlite3
import pytest
from flask import Flask

# ✅ Make backend importable even if pytest runs from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from users import users_bp  # works after path fix


@pytest.fixture(scope="function")
def app_client(tmp_path):
    """Create a temporary Flask app + isolated SQLite DB for testing."""
    app = Flask(__name__)
    app.register_blueprint(users_bp)

    test_db = tmp_path / "test_users.db"
    os.makedirs(test_db.parent, exist_ok=True)

    # Patch database connection inside users.py
    import users

    def fake_get_connection():
        conn = sqlite3.connect(str(test_db))
        conn.row_factory = sqlite3.Row
        return conn

    users.get_connection = fake_get_connection

    # Initialize database schema
    conn = fake_get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            joined TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------

def test_register_success(app_client):
    """POST /users/register should create a new user"""
    payload = {"username": "sam", "email": "sam@example.com", "password": "123"}
    resp = app_client.post("/users/register", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["data"]["username"] == "sam"


def test_register_missing_fields(app_client):
    """Missing fields should return 400"""
    resp = app_client.post("/users/register", json={"username": "sam"})
    assert resp.status_code == 400
    assert resp.get_json()["status"] == "error"


def test_register_duplicate_username(app_client):
    """Should reject duplicate username or email"""
    payload = {"username": "sam", "email": "sam@example.com", "password": "123"}
    app_client.post("/users/register", json=payload)
    resp = app_client.post("/users/register", json=payload)
    assert resp.status_code == 400
    err = resp.get_json()
    assert err["status"] == "error"
    assert "USER_EXISTS" in err["error"]["code"]


def test_login_success(app_client):
    """POST /users/login with correct credentials"""
    app_client.post("/users/register", json={
        "username": "testuser",
        "email": "t@t.com",
        "password": "abc"
    })
    resp = app_client.post("/users/login", json={"username": "testuser", "password": "abc"})
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["username"] == "testuser"


def test_login_not_found(app_client):
    """Unknown user should return 404"""
    resp = app_client.post("/users/login", json={"username": "nouser", "password": "abc"})
    assert resp.status_code == 404
    assert resp.get_json()["error"]["code"] == "NOT_FOUND"


def test_login_incorrect_password(app_client):
    """Wrong password should return 401"""
    app_client.post("/users/register", json={
        "username": "jane",
        "email": "jane@example.com",
        "password": "secret"
    })
    resp = app_client.post("/users/login", json={"username": "jane", "password": "wrong"})
    assert resp.status_code == 401
    assert resp.get_json()["error"]["code"] == "INVALID_PASSWORD"


def test_get_user_profile_ok(app_client):
    """GET /users/<id> returns user details"""
    reg = app_client.post("/users/register", json={
        "username": "alex",
        "email": "alex@example.com",
        "password": "pw"
    })
    user_id = reg.get_json()["data"]["userId"]
    resp = app_client.get(f"/users/{user_id}")
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["username"] == "alex"
    assert "joined" in data


def test_get_user_profile_not_found(app_client):
    """GET /users/<id> with nonexistent user"""
    resp = app_client.get("/users/999")
    assert resp.status_code == 404
    assert resp.get_json()["error"]["code"] == "NOT_FOUND"


def test_get_all_users(app_client):
    """GET /users/all returns all registered users"""
    app_client.post("/users/register", json={
        "username": "one", "email": "1@a.com", "password": "x"
    })
    app_client.post("/users/register", json={
        "username": "two", "email": "2@a.com", "password": "y"
    })
    resp = app_client.get("/users/all")
    assert resp.status_code == 200
    users = resp.get_json()["data"]["users"]
    assert len(users) >= 2
    assert all("username" in u for u in users)
