import os
import pytest
from backend.main import app
from backend.db.database import init_db

@pytest.fixture(scope="session")
def app_client():
    # Always use in-memory DB for tests
    os.environ["TEST_DB_PATH"] = ":memory:"

    with app.app_context():
        init_db()
        client = app.test_client()
        yield client
