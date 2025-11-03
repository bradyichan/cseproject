"""
Module: payment.py
Description: Implements payment credential validation, purchase confirmation,
and payment history management for the Marketplace API.
Author: Team 22 - CSE 2102
Date: 2025-11-03
"""

from datetime import datetime
from flask import Blueprint, jsonify, request
import sqlite3
import os

# Blueprint
payment_bp = Blueprint("payment", __name__, url_prefix="/payment")

# Database path (same as in database.py or main.py)
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "marketplace.db")


def get_db_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@payment_bp.route("/validate", methods=["POST"])
def validate_payment():
    """
    Validate payment credentials.
    ---
    tags:
      - Payment
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              paymentMethodId: {type: string}
              userId: {type: integer}
              cardNumber: {type: string}
              cvv: {type: string}
              expiryDate: {type: string}
    responses:
      200:
        description: Payment method validated successfully.
      400:
        description: Invalid payment credentials.
    """
    data = request.get_json() or {}

    required = ["paymentMethodId", "userId", "cardNumber", "cvv", "expiryDate"]
    if not all(k in data for k in required):
        return jsonify({
            "status": "error",
            "error": {"code": "MISSING_FIELDS", "message": "Missing required fields"}
        }), 400

    card = data.get("cardNumber", "").replace(" ", "")
    cvv = data.get("cvv", "")

    if len(card) not in (15, 16) or not cvv.isdigit() or len(cvv) not in (3, 4):
        return jsonify({
            "status": "error",
            "error": {"code": "INVALID_PAYMENT_METHOD", "message": "Payment credentials are invalid"}
        }), 400

    # Optional: insert or update payment method for user
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO payments (user_id, payment_method_id, card_last4, expiry_date, verified)
        VALUES (?, ?, ?, ?, ?)
    """, (data["userId"], data["paymentMethodId"], card[-4:], data["expiryDate"], 1))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "valid": True,
            "paymentMethodId": data["paymentMethodId"]
        }
    }), 200


@payment_bp.route("/purchase", methods=["POST"])
def create_purchase():
    """
    Record a new purchase transaction once payment is validated.
    ---
    tags:
      - Payment
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              itemId: {type: integer}
              userId: {type: integer}
              paymentMethodId: {type: string}
              amount: {type: number}
    responses:
      201:
        description: Purchase created successfully.
      400:
        description: Invalid or unverified payment.
    """
    data = request.get_json() or {}

    if not all(k in data for k in ("itemId", "userId", "paymentMethodId", "amount")):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Verify the payment method
    cur.execute("""
        SELECT verified FROM payments
        WHERE user_id = ? AND payment_method_id = ?
    """, (data["userId"], data["paymentMethodId"]))
    record = cur.fetchone()

    if not record or record["verified"] != 1:
        conn.close()
        return jsonify({"status": "error", "message": "Payment not verified"}), 400

    # Create new transaction
    cur.execute("""
        INSERT INTO transactions (item_id, buyer_id, amount, status, purchased_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["itemId"], data["userId"], data["amount"], "unshipped",
        datetime.now().isoformat()
    ))
    conn.commit()
    transaction_id = cur.lastrowid
    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "transactionId": transaction_id,
            "itemId": data["itemId"],
            "status": "unshipped",
            "purchasedAt": datetime.now().isoformat()
        }
    }), 201


@payment_bp.route("/history/<int:user_id>", methods=["GET"])
def get_payment_history(user_id):
    """Retrieve all transactions for a specific user."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT transaction_id, item_id, amount, status, purchased_at
        FROM transactions WHERE buyer_id = ?
    """, (user_id,))
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()

    return jsonify({"status": "success", "transactions": rows}), 200


@payment_bp.route("/refund/<int:transaction_id>", methods=["PUT"])
def refund_transaction(transaction_id):
    """Handle refund requests for transactions."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM transactions WHERE transaction_id = ?
    """, (transaction_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "Transaction not found"}), 404

    cur.execute("""
        UPDATE transactions SET status = ? WHERE transaction_id = ?
    """, ("refunded", transaction_id))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "data": {
            "transactionId": transaction_id,
            "status": "refunded",
            "refundedAt": datetime.now().isoformat()
        }
    }), 200
