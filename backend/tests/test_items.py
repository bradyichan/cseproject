# tests/test_items.py
import copy
import re

import pytest
from flask import Flask

import items  # your items.py module


@pytest.fixture(scope="function")
def app_client():
    """
    Fresh Flask test client with clean copies of items.items and items.next_id.
    Restores globals after each test to avoid state leakage.
    """
    original_items = copy.deepcopy(items.items)
    original_next_id = copy.deepcopy(items.next_id)

    app = Flask(__name__)
    app.register_blueprint(items.items_bp)
    client = app.test_client()

    yield client

    # Restore module globals
    items.items.clear()
    items.items.update(copy.deepcopy(original_items))
    items.next_id.clear()
    items.next_id.update(copy.deepcopy(original_next_id))


def test_get_all_items(app_client):
    resp = app_client.get("/items/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == len(items.items)
    assert isinstance(data["items"], list)
    assert any(it["title"] == "Gaming Laptop" for it in data["items"])


def test_get_item_ok_and_not_found(app_client):
    ok = app_client.get("/items/1")
    assert ok.status_code == 200
    assert ok.get_json()["title"] == "Gaming Laptop"

    nf = app_client.get("/items/999")
    assert nf.status_code == 404
    assert nf.get_json()["error"] == "Item not found"


def test_create_item_requires_fields(app_client):
    r = app_client.post("/items/create", json={"title": "X", "price": 10})
    assert r.status_code == 400
    assert "Missing" in r.get_json()["error"]


def test_create_item_success_increments_id_and_sets_created_at(app_client):
    starting_next = items.next_id["value"]
    payload = {
        "title": "Desk Chair",
        "category": "Furniture",
        "price": 129.99,
        "seller": "sam",
    }
    resp = app_client.post("/items/create", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "created"
    created = data["item"]

    # ID assigned from next_id and then incremented
    assert created["id"] == starting_next
    assert items.next_id["value"] == starting_next + 1

    # Basic field echoes
    assert created["title"] == "Desk Chair"
    assert created["category"] == "Furniture"
    assert created["seller"] == "sam"
    # Price coerced to float
    assert isinstance(created["price"], float)
    assert created["price"] == pytest.approx(129.99)

    # created_at present and YYYY-MM-DD HH:MM:SS-ish
    assert "created_at" in created
    assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", created["created_at"])

    # Item is stored in module state
    assert created["id"] in items.items


def test_update_item_ok_and_not_found(app_client):
    # Update existing
    upd = app_client.put("/items/1/update", json={"price": 799, "status": "reserved"})
    assert upd.status_code == 200
    j = upd.get_json()
    assert j["status"] == "updated"
    assert j["item"]["price"] == 799
    assert j["item"]["status"] == "reserved"

    # Update missing
    nf = app_client.put("/items/999/update", json={"title": "Nope"})
    assert nf.status_code == 404
    assert nf.get_json()["error"] == "Item not found"


def test_delete_item_ok_and_not_found(app_client):
    # Delete existing
    d = app_client.delete("/items/3/delete")
    assert d.status_code == 200
    j = d.get_json()
    assert j["status"] == "deleted"
    assert j["item"]["id"] == 3
    assert 3 not in items.items

    # Delete missing
    nf = app_client.delete("/items/999/delete")
    assert nf.status_code == 404
    assert nf.get_json()["error"] == "Item not found"


def test_get_items_by_seller(app_client):
    resp = app_client.get("/items/seller/alex")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["seller"] == "alex"
    # In seed data, alex sells ids 1 and 3
    returned_ids = sorted([it["id"] for it in data["items"]])
    assert returned_ids == [1, 3]
