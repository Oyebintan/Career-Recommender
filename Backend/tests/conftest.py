"""
Shared pytest fixtures for the Backend test suite.

Run from the Backend/ directory:
    pytest
"""
import atexit
import os
import sys
import tempfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Config reads these env vars at import time, so they must be set before
# `app`/`config` are imported anywhere (including by other test modules).
_db_fd, _db_path = tempfile.mkstemp(suffix=".sqlite")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ["FLASK_DEBUG"] = "False"


@atexit.register
def _cleanup_db_file():
    try:
        os.close(_db_fd)
        os.unlink(_db_path)
    except OSError:
        pass


import pytest  # noqa: E402

from app import app as flask_app  # noqa: E402
from extensions import db as _db  # noqa: E402

flask_app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)


@pytest.fixture(autouse=True)
def _clean_database():
    """Give every test a fresh, empty schema."""
    with flask_app.app_context():
        _db.drop_all()
        _db.create_all()
    yield


@pytest.fixture()
def app():
    return flask_app


@pytest.fixture()
def app_context():
    with flask_app.app_context():
        yield flask_app


@pytest.fixture()
def client():
    return flask_app.test_client()


@pytest.fixture()
def registered_user(client):
    """Registers and logs in a user, returns (client, email, password)."""
    email, password = "pytest-user@example.com", "password123"
    client.post("/register", data={
        "name": "Pytest User",
        "email": email,
        "password": password,
        "confirm_password": password,
    })
    return client, email, password
