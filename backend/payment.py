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

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "marketplace.db")


def get_db_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------
# POST /payment/validate
# ---------------------------------------------------------------------
@payment_bp.route("/validate", methods=["POST"])
def validate_payment():
    """
    Validate payment credentials
    ---
    tags:
      - Payment
    summary: Validate a user's payment method
    description: |
      Checks if provided card and CVV format are valid, and stores the payment method in the database.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [paymentMethodId, userId, cardNumber, cvv, expiryDate]
            properties:
              paymentMethodId:
                type: string
                example: "visa_1234"
              userId:
                type: integer
                example: 5
              cardNumber:
                type: string
                example: "4242 4242 4242 4242"
              cvv:
                type: string
                example: "123"
              expiryDate:
                type: string
                example: "12/27"
    responses:
      200:
        description: Payment method validated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                status: {type: string, example: success}
                data:
                  type: object
                  properties:
                    valid: {type: boolean, example: true}
                    paymentMethodId: {type: string, example: "visa_1234"}
      400:
        description: Invalid or missing payment credentials
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


# ---------------------------------------------------------------------
# POST /payment/purchase
# ---------------------------------------------------------------------
@payment_bp.route("/purchase", methods=["POST"])
def create_purchase():
    """
    Create a purchase transaction
    ---
    tags:
      - Payment
    summary: Record a new purchase after validation
    description: Creates a new transaction entry for a validated payment method.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [itemId, userId, paymentMethodId, amount]
            properties:
              itemId: {type: integer, example: 12}
              userId: {type: integer, example: 5}
              paymentMethodId: {type: string, example: "visa_1234"}
              amount: {type: number, example: 199.99}
    responses:
      201:
        description: Purchase successfully recorded
        content:
          application/json:
            schema:
              type: object
              properties:
                status: {type: string, example: success}
                data:
                  type: object
                  properties:
                    transactionId: {type: integer, example: 42}
                    itemId: {type: integer, example: 12}
                    status: {type: string, example: unshipped}
                    purchasedAt: {type: string, example: "2025-11-03T18:30:00"}
      400:
        description: Payment method not verified or missing fields
    """
    data = request.get_json() or {}

    if not all(k in data for k in ("itemId", "userId", "paymentMethodId", "amount")):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT verified FROM payments
        WHERE user_id = ? AND payment_method_id = ?
    """, (data["userId"], data["paymentMethodId"]))
    record = cur.fetchone()

    if not record or record["verified"] != 1:
        conn.close()
        return jsonify({"status": "error", "message": "Payment not verified"}), 400

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


# ---------------------------------------------------------------------
# GET /payment/history/<user_id>
# ---------------------------------------------------------------------
@payment_bp.route("/history/<int:user_id>", methods=["GET"])
def get_payment_history(user_id):
    """
    Get payment history
    ---
    tags:
      - Payment
    summary: Retrieve all past transactions for a specific user
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
        description: The user's ID
    responses:
      200:
        description: List of transactions retrieved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                status: {type: string, example: success}
                transactions:
                  type: array
                  items:
                    type: object
                    properties:
                      transaction_id: {type: integer, example: 44}
                      item_id: {type: integer, example: 12}
                      amount: {type: number, example: 89.99}
                      status: {type: string, example: shipped}
                      purchased_at: {type: string, example: "2025-11-02T14:00:00"}
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT transaction_id, item_id, amount, status, purchased_at
        FROM transactions WHERE buyer_id = ?
    """, (user_id,))
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()

    return jsonify({"status": "success", "transactions": rows}), 200


# ---------------------------------------------------------------------
# PUT /payment/refund/<transaction_id>
# ---------------------------------------------------------------------
@payment_bp.route("/refund/<int:transaction_id>", methods=["PUT"])
def refund_transaction(transaction_id):
    """
    Refund a transaction
    ---
    tags:
      - Payment
    summary: Mark a transaction as refunded
    parameters:
      - name: transaction_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Transaction successfully refunded
        content:
          application/json:
            schema:
              type: object
              properties:
                status: {type: string, example: success}
                data:
                  type: object
                  properties:
                    transactionId: {type: integer, example: 88}
                    status: {type: string, example: refunded}
                    refundedAt: {type: string, example: "2025-11-03T19:00:00"}
      404:
        description: Transaction not found
    """
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
