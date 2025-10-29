# tests/test_search.py
import copy

import pytest
from flask import Flask

import search  # your search.py module


@pytest.fixture(scope="function")
def app_client():
    """
    Fresh Flask test client; restore search.listings after each test
    in case any test mutates it (defensive).
    """
    original_listings = copy.deepcopy(search.listings)

    app = Flask(__name__)
    app.register_blueprint(search.search_bp)
    client = app.test_client()

    yield client

    search.listings.clear()
    search.listings.extend(copy.deepcopy(original_listings))


def test_search_all_when_no_filters(app_client):
    # With no query/filters, all listings should be returned
    resp = app_client.get("/search/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == len(search.listings)
    assert len(data["results"]) == len(search.listings)


def test_search_by_query_and_category(app_client):
    # q=laptop -> should match "Gaming Laptop" only
    r1 = app_client.get("/search/?q=laptop")
    assert r1.status_code == 200
    d1 = r1.get_json()
    assert d1["count"] == 1
    assert d1["results"][0]["title"] == "Gaming Laptop"

    # category=electronics (case-insensitive) -> ids 1 and 5
    r2 = app_client.get("/search/?category=Electronics")
    assert r2.status_code == 200
    d2 = r2.get_json()
    returned_ids = sorted([x["id"] for x in d2["results"]])
    assert returned_ids == [1, 5]


def test_search_by_price_range_and_sorting(app_client):
    # Price between 50 and 200 -> ids 4 ($100) and 5 ($60)
    r = app_client.get("/search/?min_price=50&max_price=200")
    assert r.status_code == 200
    d = r.get_json()
    ids = sorted([x["id"] for x in d["results"]])
    assert ids == [4, 5]

    # Sorting: Electronics by ascending price -> id 5 ($60) then id 1 ($750)
    r_sort = app_client.get("/search/?category=electronics&sort=price_asc")
    assert r_sort.status_code == 200
    d_sort = r_sort.get_json()
    titles_in_order = [x["title"] for x in d_sort["results"]]
    assert titles_in_order == ["Wireless Earbuds", "Gaming Laptop"]

    # Descending price -> reverse order
    r_sort_desc = app_client.get("/search/?category=electronics&sort=price_desc")
    assert r_sort_desc.status_code == 200
    d_sort_desc = r_sort_desc.get_json()
    titles_in_order_desc = [x["title"] for x in d_sort_desc["results"]]
    assert titles_in_order_desc == ["Gaming Laptop", "Wireless Earbuds"]


def test_search_no_results_returns_404(app_client):
    r = app_client.get("/search/?q=thiswillnotmatchanything")
    assert r.status_code == 404
    d = r.get_json()
    assert d["message"] == "No results found"
    assert d["results"] == []


def test_suggestions_default_and_with_query(app_client):
    # Default suggestions when no query
    r_def = app_client.get("/search/suggestions")
    assert r_def.status_code == 200
    d_def = r_def.get_json()
    # At least includes these baseline suggestions
    for s in ["laptop", "headphones", "jacket", "lamp"]:
        assert s in d_def["suggestions"]

    # With a query: "lap" should match titles containing "lap" (lowercased)
    r_q = app_client.get("/search/suggestions?q=lap")
    assert r_q.status_code == 200
    d_q = r_q.get_json()
    # "gaming laptop" and "vintage lamp" both contain "lap"
    assert "gaming laptop" in d_q["suggestions"]
    # assert "vintage lamp" in d_q["suggestions"]


def test_get_item_details_ok_and_not_found(app_client):
    ok = app_client.get("/search/item/3")
    assert ok.status_code == 200
    assert ok.get_json()["title"] == "Mountain Bike"

    nf = app_client.get("/search/item/999")
    assert nf.status_code == 404
    assert nf.get_json()["error"] == "Item not found"
