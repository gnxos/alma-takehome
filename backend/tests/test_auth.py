from app import config
from tests.test_leads import _create_lead


def test_login_success_sets_cookie_and_returns_email(client):
    # `client` is already logged in by the autouse fixture; log out first so
    # this test observes a clean login from scratch.
    client.post("/logout")

    response = client.post(
        "/login",
        json={"email": config.ATTORNEY_EMAIL, "password": config.ATTORNEY_PASSWORD},
    )
    assert response.status_code == 200
    assert response.json() == {"email": config.ATTORNEY_EMAIL}
    assert config.AUTH_COOKIE_NAME in response.cookies


def test_login_wrong_password_returns_401(client):
    response = client.post(
        "/login", json={"email": config.ATTORNEY_EMAIL, "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_login_unknown_email_returns_401(client):
    response = client.post(
        "/login",
        json={"email": "not-the-attorney@example.com", "password": config.ATTORNEY_PASSWORD},
    )
    assert response.status_code == 401


def test_login_email_is_case_insensitive(client):
    response = client.post(
        "/login",
        json={"email": config.ATTORNEY_EMAIL.upper(), "password": config.ATTORNEY_PASSWORD},
    )
    assert response.status_code == 200


def test_logout_clears_cookie(client):
    response = client.post("/logout")
    assert response.status_code == 200
    set_cookie = response.headers.get("set-cookie", "")
    assert config.AUTH_COOKIE_NAME in set_cookie
    # A cleared cookie is sent back with an empty value and an expiry in the past.
    assert f'{config.AUTH_COOKIE_NAME}=""' in set_cookie or f"{config.AUTH_COOKIE_NAME}=" in set_cookie


def test_me_returns_current_attorney_when_authenticated(client):
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json() == {"email": config.ATTORNEY_EMAIL}


def test_me_returns_401_without_cookie(client):
    client.cookies.clear()
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_returns_401_after_logout(client):
    client.post("/logout")
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_returns_401_with_tampered_token(client):
    client.cookies.set(config.AUTH_COOKIE_NAME, "this.is.not-a-valid-jwt")
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_leads_list_requires_authentication(client):
    client.cookies.clear()
    response = client.get("/api/leads")
    assert response.status_code == 401


def test_leads_get_requires_authentication(client):
    client.cookies.clear()
    response = client.get("/api/leads/some-id")
    assert response.status_code == 401


def test_leads_update_requires_authentication(client):
    client.cookies.clear()
    response = client.patch("/api/leads/some-id", json={"status": "REACHED_OUT"})
    assert response.status_code == 401


def test_leads_resume_requires_authentication(client):
    client.cookies.clear()
    response = client.get("/api/leads/some-id/resume")
    assert response.status_code == 401


def test_lead_creation_remains_public(client):
    client.cookies.clear()
    response = _create_lead(client)
    assert response.status_code == 201
