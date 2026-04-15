"""Extended authentication endpoint tests."""

from fastapi import status

from app.db.session import SessionLocal
from app.models.user import User
from app.services import auth_email


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _register(client, email: str = "user@example.com", role: str = "rider"):
    return client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "phone": None,
            "password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "User",
            "role": role,
        },
    )


def _login(client, email: str = "user@example.com", password: str = "StrongPass123!"):
    return client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def _set_inactive(email: str) -> None:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    user.is_active = False
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Login edge cases
# ---------------------------------------------------------------------------


def test_login_wrong_password_returns_401(client):
    _register(client)
    resp = _login(client, password="WrongPassword!")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email" in resp.json()["detail"]


def test_login_nonexistent_user_returns_401(client):
    resp = _login(client, email="nobody@example.com")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_inactive_user_returns_400(client):
    email = "inactive@example.com"
    _register(client, email=email)
    _set_inactive(email)
    resp = _login(client, email=email)
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["detail"] == "Inactive user"


# ---------------------------------------------------------------------------
# Email verification flow
# ---------------------------------------------------------------------------


def test_verify_email_success(client, fake_redis):
    email = "verify@example.com"
    _register(client, email=email)

    # Manually place the verification code into FakeRedis.
    code = "123456"
    fake_redis.setex(f"email_verification:{email}", 3600, code)

    resp = client.post(
        "/api/v1/auth/verify-email", json={"email": email, "code": code}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["message"] == "Email successfully verified"

    # User should now be verified in the database.
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    assert user is not None and user.is_verified is True


def test_verify_email_wrong_code_returns_400(client, fake_redis):
    email = "wrongcode@example.com"
    _register(client, email=email)

    fake_redis.setex(f"email_verification:{email}", 3600, "999999")

    resp = client.post(
        "/api/v1/auth/verify-email", json={"email": email, "code": "000000"}
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["detail"] == "Invalid email or code"


def test_verify_email_nonexistent_user_returns_400(client):
    resp = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "ghost@example.com", "code": "000000"},
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_verify_email_already_verified(client, fake_redis):
    email = "alreadyverified@example.com"
    _register(client, email=email)

    # Verify once
    code = "112233"
    fake_redis.setex(f"email_verification:{email}", 3600, code)
    client.post("/api/v1/auth/verify-email", json={"email": email, "code": code})

    # Attempt to verify again (code has been deleted from Redis, user is verified)
    resp = client.post(
        "/api/v1/auth/verify-email", json={"email": email, "code": "000000"}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["message"] == "Email already verified"


# ---------------------------------------------------------------------------
# Resend verification
# ---------------------------------------------------------------------------


def test_resend_verification_existing_unverified_user(client):
    email = "resend@example.com"
    _register(client, email=email)

    resp = client.post(
        "/api/v1/auth/resend-verification", json={"email": email}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert "If an account exists" in resp.json()["message"]


def test_resend_verification_nonexistent_email(client):
    resp = client.post(
        "/api/v1/auth/resend-verification", json={"email": "ghost@example.com"}
    )
    # Must return generic message — does not reveal whether account exists.
    assert resp.status_code == status.HTTP_200_OK
    assert "If an account exists" in resp.json()["message"]


def test_resend_verification_already_verified_user(client, fake_redis):
    email = "alreadyv2@example.com"
    _register(client, email=email)

    code = "445566"
    fake_redis.setex(f"email_verification:{email}", 3600, code)
    client.post("/api/v1/auth/verify-email", json={"email": email, "code": code})

    resp = client.post(
        "/api/v1/auth/resend-verification", json={"email": email}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["message"] == "Email already verified"


# ---------------------------------------------------------------------------
# Forgot password — user enumeration prevention
# ---------------------------------------------------------------------------


def test_forgot_password_nonexistent_email_returns_generic_message(client):
    resp = client.post(
        "/api/v1/auth/forgot-password", json={"email": "nobody@example.com"}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert "If an account exists" in resp.json()["message"]


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------


def test_rate_limit_registration(client, fake_redis):
    """After exceeding the limit the endpoint must return 429."""
    email_base = "ratelimitreg"
    # Force the rate limit key past the threshold (limit=5).
    rl_key = f"ratelimit:register:{email_base}0@example.com"
    fake_redis.store[rl_key] = 5  # already at limit

    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"{email_base}0@example.com",
            "phone": None,
            "password": "StrongPass123!",
            "first_name": "Rate",
            "last_name": "Limited",
            "role": "rider",
        },
    )
    assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_rate_limit_login(client, fake_redis):
    """After exceeding the login limit the endpoint must return 429."""
    email = "ratelimitlogin@example.com"
    _register(client, email=email)

    rl_key = f"ratelimit:login:{email}"
    fake_redis.store[rl_key] = 10  # already at limit

    resp = _login(client, email=email)
    assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
