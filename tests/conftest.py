import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.config import TestConfig
from app.extensions import db as _db
from app.models.user import User


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function", autouse=True)
def clean_db(app):
    """Wipe all rows between tests without dropping tables."""
    yield
    with app.app_context():
        _db.session.query(User).delete()
        _db.session.commit()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def existing_user(app):
    """Creates and returns a persisted user for tests that need one."""
    with app.app_context():
        user = User(
            username="existinguser",
            email="existing@example.com",
            password_hash=generate_password_hash("password123"),
        )
        _db.session.add(user)
        _db.session.commit()
        return {"email": "existing@example.com", "password": "password123", "username": "existinguser"}


@pytest.fixture()
def auth_headers(client, existing_user):
    """Returns Authorization headers for an authenticated request."""
    resp = client.post("/auth/login", json={
        "email": existing_user["email"],
        "password": existing_user["password"],
    })
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
