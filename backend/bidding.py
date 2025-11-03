"""
Module: bidding.py
Description: Handles bidding and buy-now functionality for auction items,
including bid placement, status checks, and bid history.
Author: Team XX - CSE 2102
Date: 2025-10-27
"""
from datetime import datetime
from flask import Blueprint, jsonify, request

bidding_bp = Blueprint("bidding", __name__, url_prefix="/bidding")

# Mock data
items = {
    1: {"name": "Gaming Laptop", "current_bid": 500, "buy_now": 800,
        "highest_bidder": None, "status": "open"},
    2: {"name": "Headphones", "current_bid": 40, "buy_now": 60,
        "highest_bidder": None, "status": "open"}
}

bids = []  # store all bids

@bidding_bp.route("/items", methods=["GET"])
def get_all_items():
    """Display all auction items (display_item_details)."""
    return jsonify({"items": items}), 200


@bidding_bp.route("/item/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Return details of a specific item."""
    if item_id not in items:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(items[item_id]), 200


@bidding_bp.route("/item/<int:item_id>/bid", methods=["POST"])
def place_bid(item_id):
    """Place a bid on an item."""
    data = request.get_json() or {}
    bidder = data.get("bidder")
    amount = data.get("amount")

    if not all([bidder, amount]):
        return jsonify({"error": "Missing bidder or amount"}), 400

    if item_id not in items:
        return jsonify({"error": "Item not found"}), 404

    item = items[item_id]
    if item["status"] != "open":
        return jsonify({"error": "Bidding closed"}), 400

    if amount <= item["current_bid"]:
        return jsonify({"status": "failed", "message": "Bid too low"}), 400

    # Record bid
    item["current_bid"] = amount
    item["highest_bidder"] = bidder
    bids.append({
        "item_id": item_id,
        "bidder": bidder,
        "amount": amount,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return jsonify({
        "status": "success",
        "message": "Bid placed successfully",
        "item_id": item_id,
        "new_highest_bid": amount
    }), 200


@bidding_bp.route("/item/<int:item_id>/status", methods=["GET"])
def get_bid_status(item_id):
    """Check the current bid status of an item."""
    if item_id not in items:
        return jsonify({"error": "Item not found"}), 404

    item = items[item_id]
    return jsonify({
        "item_id": item_id,
        "current_bid": item["current_bid"],
        "highest_bidder": item["highest_bidder"],
        "status": item["status"]
    }), 200


@bidding_bp.route("/item/<int:item_id>/buy", methods=["POST"])
def buy_now(item_id):
    """Simulate 'buy now' (goes to payment step)."""
    data = request.get_json() or {}
    buyer = data.get("buyer")

    if item_id not in items:
        return jsonify({"error": "Item not found"}), 404
    item = items[item_id]

    if item["status"] != "open":
        return jsonify({"error": "Item not available"}), 400

    item["status"] = "sold"
    confirmation = {
        "item_id": item_id,
        "buyer": buyer,
        "amount": item["buy_now"],
        "confirmation_code": f"BUY-{item_id:04}"
    }

    return jsonify({
        "status": "purchased",
        "confirmation": confirmation
    }), 200


@bidding_bp.route("/history/<string:username>", methods=["GET"])
def user_bid_history(username):
    """Return all bids placed by a given user."""
    user_bids = [b for b in bids if b["bidder"] == username]
    return jsonify({"username": username, "bids": user_bids}), 200
