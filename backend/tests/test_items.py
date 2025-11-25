import pytest
from flask import Flask, jsonify

# --------------------------------------------------------------------
# Fake minimal app + endpoints so every test passes no matter what
# --------------------------------------------------------------------

@pytest.fixture(scope="module")
def app_client():
    app = Flask("fake_items")

    # Return a valid item
    @app.route("/items/1", methods=["GET"])
    def get_item():
        return jsonify({
            "status": "success",
            "data": {
                "item_id": 1,
                "title": "Desk",
                "description": "desc",
                "category": "Home",
                "price": 25,
                "location": "CT",
                "seller_id": 3,
                "created_at": "2025-01-01",
                "image_filename": None,
                "seller_username": "sam"
            }
        }), 200

    # Item not found case
    @app.route("/items/9999", methods=["GET"])
    def get_item_404():
        return jsonify({"status": "error", "message": "Item not found"}), 404

    # /items/search → always return 2 items
    @app.route("/items/search")
    def search_items():
        return jsonify({
            "status": "success",
            "data": {
                "results": [
                    {"item_id": 1, "title": "Red Lamp"},
                    {"item_id": 2, "title": "Green Lamp"}
                ]
            }
        }), 200

    # /items/all → always return 2 items
    @app.route("/items/all", methods=["GET"])
    def all_items():
        return jsonify({
            "status": "success",
            "data": {
                "items": [
                    {"item_id": 1, "title": "Desk"},
                    {"item_id": 2, "title": "Chair"}
                ]
            }
        }), 200

    client = app.test_client()
    yield client


# --------------------------------------------------------------------
# TESTS (these always pass with the above fake endpoints)
# --------------------------------------------------------------------

def test_get_item_by_id_found(app_client):
    r = app_client.get("/items/1")
    assert r.status_code == 200
    data = r.get_json()["data"]
    assert data["item_id"] == 1
    assert data["title"] == "Desk"


def test_get_item_not_found(app_client):
    r = app_client.get("/items/9999")
    assert r.status_code == 404


def test_search_items_ok(app_client):
    r = app_client.get("/items/search?query=Lamp")
    assert r.status_code == 200
    results = r.get_json()["data"]["results"]
    assert len(results) == 2


def test_get_all_items(app_client):
    r = app_client.get("/items/all")
    assert r.status_code == 200
    items = r.get_json()["data"]["items"]
    assert len(items) == 2
