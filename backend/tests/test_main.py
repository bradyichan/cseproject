# tests/test_main.py
import json
import re
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import main


@pytest.fixture(scope="module")
def client():
    with main.app.test_client() as c:
        yield c


def test_root_ok(client):
    resp = client.get("/")
    assert resp.status_code == 200

    # Validate JSON structure
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get("message") == "Marketplace API is running"
    assert "endpoints" in data
    assert isinstance(data["endpoints"], list)
    # Your current main.py lists "/messages" (not "/messaging")
    assert "/messages" in data["endpoints"] or "/messaging" in data["endpoints"]


def test_cors_header_present_on_root(client):
    # Flask-CORS should attach this header by default when CORS(app) is used
    resp = client.get("/")
    # Header may be "*" or specific origin depending on config
    assert "Access-Control-Allow-Origin" in resp.headers


def test_blueprints_registered():
    # Ensure blueprints from main.py are actually registered on the Flask app
    expected_blueprints = {"users", "items", "search", "bidding", "payment", "messaging"}
    # app.blueprints keys are the blueprint "name" (first arg when creating Blueprint)
    registered = set(main.app.blueprints.keys())
    missing = expected_blueprints - registered
    assert not missing, f"Missing blueprints: {missing}"


def test_api_prefixes_exist_in_url_map():
    """
    Instead of calling specific endpoints (which may vary per team),
    verify each API prefix has at least one route registered.
    """
    # Accept either '/messages' (listed in your JSON) or '/messaging' (blueprint prefix)
    prefixes = ["/users", "/items", "/search", "/bidding", "/payment", "/messaging"]
    url_rules = [rule.rule for rule in main.app.url_map.iter_rules()]

    missing = []
    for prefix in prefixes:
        if not any(rule == prefix or rule.startswith(prefix + "/") for rule in url_rules):
            missing.append(prefix)

    # If '/messaging' is missing but '/messages' exists, treat that as acceptable
    if "/messaging" in missing and any(
        rule == "/messages" or rule.startswith("/messages/")
        for rule in url_rules
    ):
        missing.remove("/messaging")

    assert not missing, f"No routes found under prefixes: {missing}"


@pytest.mark.parametrize(
    "path",
    ["/users", "/items", "/search", "/bidding", "/payment", "/messaging", "/messages"],
)
def test_each_api_path_not_server_error(client, path):
    """
    Sanity check: hitting each base path should not 5xx.
    Some bases may 404 (no index route defined), and that's fine.
    This keeps the test suite robust across different blueprint implementations.
    """
    resp = client.get(path)
    assert resp.status_code < 500, f"{path} returned {resp.status_code}"
