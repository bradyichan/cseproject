import sys, os

# --- ensure Python can find backend and db modules ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # for db/

import pytest
from backend.main import app


@pytest.fixture(scope="module")
def client():
    """Flask test client for the main app."""
    with app.test_client() as client:
        yield client


def test_home_status_ok(client):
    """Root endpoint should return 200 and a valid message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "Marketplace API is running" in data["message"]
    assert isinstance(data["endpoints"], list)
    expected = {"/users", "/items", "/search", "/bidding", "/payment", "/messages"}
    assert expected.issubset(set(data["endpoints"]))


def test_blueprints_registered():
    """Ensure all expected blueprints are registered on the Flask app."""
    blueprints = set(app.blueprints.keys())
    expected = {"users", "items", "search", "bidding", "payment", "messaging"}
    assert expected.issubset(blueprints)


def test_swagger_and_cors_present():
    """Check Swagger and CORS are initialized properly."""
    # Swagger adds /apidocs route
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    assert any("/apidocs" in r for r in routes)

    # CORS should add access-control headers
    with app.test_client() as client:
        resp = client.get("/")
        assert "Access-Control-Allow-Origin" in resp.headers
