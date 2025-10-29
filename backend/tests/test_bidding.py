# tests/test_bidding.py
import copy
import importlib

import pytest
from flask import Flask

from ..bidding import *


@pytest.fixture(scope="function")
def app_client():
    """
    Fresh Flask test client with a clean copy of bidding.items and bidding.bids
    for each test. Restores globals after test completes.
    """
    # Snapshot originals
    original_items = copy.deepcopy(items)
    original_bids = copy.deepcopy(bids)

    # Build app & register blueprint
    app = Flask(__name__)
    app.register_blueprint(bidding_bp)
    client = app.test_client()

    yield client

    # Restore globals
    items.clear()
    items.update(copy.deepcopy(original_items))
    bids.clear()
    bids.extend(copy.deepcopy(original_bids))


def test_get_all_items(app_client):
    resp = app_client.get("/bidding/items")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "items" in data
    assert 1 in data["items"] and 2 in data["items"]


def test_get_item_ok_and_not_found(app_client):
    ok = app_client.get("/bidding/item/1")
    assert ok.status_code == 200
    assert ok.get_json()["name"] == "Gaming Laptop"

    nf = app_client.get("/bidding/item/999")
    assert nf.status_code == 404
    assert nf.get_json()["error"] == "Item not found"


def test_place_bid_requires_bidder_and_amount(app_client):
    r1 = app_client.post("/bidding/item/1/bid", json={"bidder": "sam"})
    r2 = app_client.post("/bidding/item/1/bid", json={"amount": 600})
    assert r1.status_code == 400
    assert r2.status_code == 400
    assert r1.get_json()["error"] == "Missing bidder or amount"
    assert r2.get_json()["error"] == "Missing bidder or amount"


def test_place_bid_not_found_and_too_low(app_client):
    nf = app_client.post("/bidding/item/999/bid", json={"bidder": "sam", "amount": 10})
    assert nf.status_code == 404
    assert nf.get_json()["error"] == "Item not found"

    # Too low (<= current bid of 500)
    low = app_client.post("/bidding/item/1/bid", json={"bidder": "sam", "amount": 500})
    assert low.status_code == 400
    j = low.get_json()
    assert j["status"] == "failed"
    assert "low" in j["message"].lower()


def test_place_bid_success_and_status_reflects_change(app_client):
    # Place a valid higher bid on item 1 (current bid is 500)
    resp = app_client.post("/bidding/item/1/bid", json={"bidder": "sam", "amount": 550})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["new_highest_bid"] == 550

    # Status reflects the update
    status = app_client.get("/bidding/item/1/status")
    assert status.status_code == 200
    s = status.get_json()
    assert s["current_bid"] == 550
    assert s["highest_bidder"] == "sam"
    assert s["status"] == "open"

    # History shows the bid
    hist = app_client.get("/bidding/history/sam")
    assert hist.status_code == 200
    h = hist.get_json()
    assert h["username"] == "sam"
    assert len(h["bids"]) == 1
    assert h["bids"][0]["item_id"] == 1
    assert h["bids"][0]["amount"] == 550


def test_buy_now_happy_path_and_blocks_further_bids(app_client):
    # Buy-now on item 2
    buy = app_client.post("/bidding/item/2/buy", json={"buyer": "alex"})
    assert buy.status_code == 200
    b = buy.get_json()
    assert b["status"] == "purchased"
    assert b["confirmation"]["item_id"] == 2
    assert b["confirmation"]["buyer"] == "alex"
    assert b["confirmation"]["amount"] == items[2]["buy_now"]
    assert b["confirmation"]["confirmation_code"].startswith("BUY-")

    # Once sold, trying to bid should fail with "Bidding closed"
    bid_after = app_client.post("/bidding/item/2/bid", json={"bidder": "sam", "amount": 100})
    assert bid_after.status_code == 400
    assert bid_after.get_json()["error"] == "Bidding closed"

    # And trying to buy again should be blocked
    buy_again = app_client.post("/bidding/item/2/buy", json={"buyer": "lisa"})
    assert buy_again.status_code == 400
    assert buy_again.get_json()["error"] == "Item not available"
