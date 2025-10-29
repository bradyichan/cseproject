"""Pytest suite for backend.main.

Covers:
- Root endpoint response and CORS header.
- Blueprint registration.
- Presence of routes under expected API prefixes.
- Basic non-5xx sanity checks for each base API path.
"""

from typing import Iterator

import pytest
from backend.main import app


@pytest.fixture(scope="module")
def app_client() -> Iterator:
    """Provide a Flask test client for the application."""
    with app.test_client() as client:
        yield client


def test_root_ok(app_client) -> None:
    """Root (/) should return 200 and expected JSON structure."""
    resp = app_client.get("/")
    assert resp.status_code == 200

    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get("message") == "Marketplace API is running"
    assert "endpoints" in data
    assert isinstance(data["endpoints"], list)
    assert "/messages" in data["endpoints"] or "/messaging" in data["endpoints"]


def test_cors_header_present_on_root(app_client) -> None:
    """Flask-CORS should attach an Access-Control-Allow-Origin header."""
    resp = app_client.get("/")
    assert "Access-Control-Allow-Origin" in resp.headers


def test_blueprints_registered() -> None:
    """All expected blueprints should be registered on the Flask app."""
    expected = {"users", "items", "search", "bidding", "payment", "messaging"}
    registered = set(app.blueprints.keys())
    missing = expected - registered
    assert not missing, f"Missing blueprints: {missing}"


def test_api_prefixes_exist_in_url_map() -> None:
    """Each API prefix should have at least one registered route."""
    prefixes = ["/users", "/items", "/search", "/bidding", "/payment", "/messaging"]
    url_rules = [rule.rule for rule in app.url_map.iter_rules()]

    missing = []
    for prefix in prefixes:
        if not any(rule == prefix or rule.startswith(prefix + "/") for rule in url_rules):
            missing.append(prefix)

    if "/messaging" in missing and any(
        rule == "/messages" or rule.startswith("/messages/") for rule in url_rules
    ):
        missing.remove("/messaging")

    assert not missing, f"No routes found under prefixes: {missing}"


@pytest.mark.parametrize(
    "path",
    ["/users", "/items", "/search", "/bidding", "/payment", "/messaging", "/messages"],
)
def test_each_api_path_not_server_error(app_client, path: str) -> None:
    """Base paths should not return a 5xx error; 2xx/3xx/4xx are acceptable."""
    resp = app_client.get(path)
    assert resp.status_code < 500, f"{path} returned {resp.status_code}"
