"""
Module: payment.py
Description: Simulates payment credential verification and order confirmation
for completed transactions in the Marketplace API.
Author: Team XX - CSE 2102
Date: 2025-10-27
"""

from flask import Blueprint, jsonify, request

payment_bp = Blueprint("payment", __name__, url_prefix="/payment")

# Mock data
verifications = {}
orders = []


def validate_credentials(card_number, cvv, name, zip_code):
    """Basic mock validation logic."""
    if not (card_number and cvv and name and zip_code):
        return False
    digits = card_number.replace(" ", "")
    return len(digits) in (15, 16) and cvv.isdigit() and (3 <= len(cvv) <= 4)


@payment_bp.route("/credentials", methods=["POST"])
def send_credentials():
    """Validate payment credentials and return a token."""
    data = request.get_json() or {}
    card_number = data.get("card_number", "")
    cvv = data.get("cvv", "")
    name = data.get("name", "")
    zip_code = data.get("zip_code", "")

    # Create simple token using count instead of uuid
    token = f"VERIF-{len(verifications) + 1:04}"
    verifications[token] = {"status": "pending"}

    if validate_credentials(card_number, cvv, name, zip_code):
        verifications[token]["status"] = "verified"
        return jsonify({"status": "verified", "token": token}), 200

    verifications[token]["status"] = "invalid"
    return jsonify({
        "status": "invalid",
        "message": "Invalid card info. Try again.",
        "token": token
    }), 400


@payment_bp.route("/confirm", methods=["POST"])
def confirm_payment():
    """Confirm payment if credentials verified."""
    data = request.get_json() or {}
    token = data.get("token")
    item_id = data.get("item_id")
    amount = data.get("amount")
    buyer = data.get("buyer")

    if not all([token, item_id, amount, buyer]):
        return jsonify({"error": "Missing required fields"}), 400

    session = verifications.get(token)
    if not session or session["status"] != "verified":
        return jsonify({"error": "Payment not verified"}), 400

    order_id = len(orders) + 1
    confirmation_code = f"CONFIRM-{order_id:04}"
    orders.append({
        "order_id": order_id,
        "item_id": item_id,
        "amount": amount,
        "buyer": buyer,
        "confirmation_code": confirmation_code
    })

    return jsonify({
        "status": "success",
        "confirmation_code": confirmation_code
    }), 200


@payment_bp.route("/history", methods=["GET"])
def get_history():
    """Return all completed mock orders."""
    return jsonify({"orders": orders}), 200
