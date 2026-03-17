import pytest


REGISTER_URL = "/auth/register"
LOGIN_URL    = "/auth/login"
ACCOUNT_URL  = "/auth/account"


# ── Register ──────────────────────────────────────────────────────────────────

class TestRegister:
    def test_success(self, client):
        resp = client.post(REGISTER_URL, json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "password_hash" not in data

    def test_missing_username(self, client):
        resp = client.post(REGISTER_URL, json={"email": "a@example.com", "password": "password123"})
        assert resp.status_code == 422

    def test_missing_email(self, client):
        resp = client.post(REGISTER_URL, json={"username": "user", "password": "password123"})
        assert resp.status_code == 422

    def test_missing_password(self, client):
        resp = client.post(REGISTER_URL, json={"username": "user", "email": "a@example.com"})
        assert resp.status_code == 422

    def test_empty_body(self, client):
        resp = client.post(REGISTER_URL, json={})
        assert resp.status_code == 422

    def test_invalid_email(self, client):
        resp = client.post(REGISTER_URL, json={"username": "user", "email": "not-an-email", "password": "password123"})
        assert resp.status_code == 422

    def test_password_too_short(self, client):
        resp = client.post(REGISTER_URL, json={"username": "user", "email": "a@example.com", "password": "short"})
        assert resp.status_code == 422
        errors = resp.get_json()["errors"]
        assert any(e["field"] == "password" for e in errors)

    def test_username_too_long(self, client):
        resp = client.post(REGISTER_URL, json={"username": "u" * 31, "email": "a@example.com", "password": "password123"})
        assert resp.status_code == 422
        errors = resp.get_json()["errors"]
        assert any(e["field"] == "username" for e in errors)

    def test_duplicate_email(self, client, existing_user):
        resp = client.post(REGISTER_URL, json={
            "username": "differentuser",
            "email": existing_user["email"],
            "password": "password123",
        })
        assert resp.status_code == 409
        assert "email" in resp.get_json()["error"]

    def test_duplicate_username(self, client, existing_user):
        resp = client.post(REGISTER_URL, json={
            "username": existing_user["username"],
            "email": "different@example.com",
            "password": "password123",
        })
        assert resp.status_code == 409
        assert "username" in resp.get_json()["error"]

    def test_email_normalized_to_lowercase(self, client):
        resp = client.post(REGISTER_URL, json={
            "username": "caseuser",
            "email": "UPPER@EXAMPLE.COM",
            "password": "password123",
        })
        assert resp.status_code == 201
        assert resp.get_json()["email"] == "upper@example.com"


# ── Login ─────────────────────────────────────────────────────────────────────

class TestLogin:
    def test_success(self, client, existing_user):
        resp = client.post(LOGIN_URL, json={
            "email": existing_user["email"],
            "password": existing_user["password"],
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "access_token" in data
        assert data["user"]["email"] == existing_user["email"]

    def test_wrong_password(self, client, existing_user):
        resp = client.post(LOGIN_URL, json={"email": existing_user["email"], "password": "wrongpassword"})
        assert resp.status_code == 401

    def test_wrong_email(self, client):
        resp = client.post(LOGIN_URL, json={"email": "nobody@example.com", "password": "password123"})
        assert resp.status_code == 401

    def test_missing_email(self, client):
        resp = client.post(LOGIN_URL, json={"password": "password123"})
        assert resp.status_code == 422

    def test_missing_password(self, client):
        resp = client.post(LOGIN_URL, json={"email": "a@example.com"})
        assert resp.status_code == 422

    def test_empty_body(self, client):
        resp = client.post(LOGIN_URL, json={})
        assert resp.status_code == 422

    def test_disabled_account(self, client, app, existing_user):
        from app.extensions import db
        from app.models.user import User
        with app.app_context():
            user = User.query.filter_by(email=existing_user["email"]).first()
            user.is_active = False
            db.session.commit()

        resp = client.post(LOGIN_URL, json={"email": existing_user["email"], "password": existing_user["password"]})
        assert resp.status_code == 403


# ── Edit account ──────────────────────────────────────────────────────────────

class TestEditAccount:
    def test_update_username(self, client, existing_user, auth_headers):
        resp = client.patch(ACCOUNT_URL, json={"username": "updatedname"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["username"] == "updatedname"

    def test_update_email(self, client, existing_user, auth_headers):
        resp = client.patch(ACCOUNT_URL, json={"email": "updated@example.com"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["email"] == "updated@example.com"

    def test_update_password(self, client, existing_user, auth_headers):
        resp = client.patch(ACCOUNT_URL, json={"password": "newpassword123"}, headers=auth_headers)
        assert resp.status_code == 200
        # verify new password works
        login_resp = client.post(LOGIN_URL, json={"email": existing_user["email"], "password": "newpassword123"})
        assert login_resp.status_code == 200

    def test_update_bio(self, client, existing_user, auth_headers):
        resp = client.patch(ACCOUNT_URL, json={"bio": "My trading bio"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["bio"] == "My trading bio"

    def test_update_avatar_url(self, client, existing_user, auth_headers):
        resp = client.patch(ACCOUNT_URL, json={"avatar_url": "https://example.com/avatar.png"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["avatar_url"] == "https://example.com/avatar.png"

    def test_update_multiple_fields(self, client, existing_user, auth_headers):
        resp = client.patch(ACCOUNT_URL, json={"username": "multiupdate", "bio": "Updated bio"}, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["username"] == "multiupdate"
        assert data["bio"] == "Updated bio"

    def test_no_auth(self, client):
        resp = client.patch(ACCOUNT_URL, json={"username": "hacker"})
        assert resp.status_code == 401

    def test_duplicate_username(self, client, app, existing_user, auth_headers):
        from app.extensions import db
        from app.models.user import User
        with app.app_context():
            other = User(username="takenuser", email="other@example.com", password_hash="x")
            db.session.add(other)
            db.session.commit()

        resp = client.patch(ACCOUNT_URL, json={"username": "takenuser"}, headers=auth_headers)
        assert resp.status_code == 409

    def test_duplicate_email(self, client, app, existing_user, auth_headers):
        from app.extensions import db
        from app.models.user import User
        with app.app_context():
            other = User(username="otheruser", email="taken@example.com", password_hash="x")
            db.session.add(other)
            db.session.commit()

        resp = client.patch(ACCOUNT_URL, json={"email": "taken@example.com"}, headers=auth_headers)
        assert resp.status_code == 409

    def test_password_too_short(self, client, existing_user, auth_headers):
        resp = client.patch(ACCOUNT_URL, json={"password": "short"}, headers=auth_headers)
        assert resp.status_code == 422

    def test_username_too_long(self, client, existing_user, auth_headers):
        resp = client.patch(ACCOUNT_URL, json={"username": "u" * 31}, headers=auth_headers)
        assert resp.status_code == 422

    def test_bio_too_long(self, client, existing_user, auth_headers):
        resp = client.patch(ACCOUNT_URL, json={"bio": "x" * 161}, headers=auth_headers)
        assert resp.status_code == 422

    def test_empty_body_is_noop(self, client, existing_user, auth_headers):
        resp = client.patch(ACCOUNT_URL, json={}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["username"] == existing_user["username"]
