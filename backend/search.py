"""
Module: search.py
Description: Implements item search, filtering, and suggestion endpoints
to simulate query results for the Marketplace API.
Author: Team XX - CSE 2102
Date: 2025-10-27
"""

from flask import Blueprint, jsonify, request

search_bp = Blueprint("search", __name__, url_prefix="/search")

# Mock listings data
listings = [
    {"id": 1, "title": "Gaming Laptop", "category": "Electronics", "price": 750},
    {"id": 2, "title": "Vintage Lamp", "category": "Home Decor", "price": 40},
    {"id": 3, "title": "Mountain Bike", "category": "Sports", "price": 300},
    {"id": 4, "title": "Leather Jacket", "category": "Clothing", "price": 100},
    {"id": 5, "title": "Wireless Earbuds", "category": "Electronics", "price": 60}
]


@search_bp.route("/", methods=["GET"])
def search_items():
    """Handle search queries with optional filters and sorting."""
    query = request.args.get("q", "").lower()
    category = request.args.get("category", "").lower()
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    sort_by = request.args.get("sort", "relevance")  # "price_asc", "price_desc", "relevance"

    # Filter listings
    results = []
    for item in listings:
        # Keyword search
        if query and query not in item["title"].lower():
            continue
        # Category filter
        if category and category not in item["category"].lower():
            continue
        # Price range filter
        if min_price and item["price"] < min_price:
            continue
        if max_price and item["price"] > max_price:
            continue

        results.append(item)

    # Sorting
    if sort_by == "price_asc":
        results.sort(key=lambda x: x["price"])
    elif sort_by == "price_desc":
        results.sort(key=lambda x: x["price"], reverse=True)
    # "relevance" leaves results as-is (since mock data isn’t scored)

    if not results:
        return jsonify({"message": "No results found", "results": []}), 404

    return jsonify({"count": len(results), "results": results}), 200


@search_bp.route("/suggestions", methods=["GET"])
def get_suggestions():
    """Return basic keyword suggestions for refinement."""
    query = request.args.get("q", "").lower()
    suggestions = []

    if not query:
        suggestions = ["laptop", "headphones", "jacket", "lamp"]
    else:
        for item in listings:
            title = item["title"].lower()
            if query in title and title not in suggestions:
                suggestions.append(title)

    return jsonify({"query": query, "suggestions": suggestions}), 200


@search_bp.route("/item/<int:item_id>", methods=["GET"])
def get_item_details(item_id):
    """Return details for a single listing (view after search)."""
    for item in listings:
        if item["id"] == item_id:
            return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 404
