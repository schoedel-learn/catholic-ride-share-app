"""Driver endpoint tests."""

from fastapi import status

from app.db.session import SessionLocal
from app.models.driver_profile import DriverProfile
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _register_and_verify(
    client, email: str, role: str = "driver", password: str = "StrongPass123!"
) -> str:
    """Register, verify, and log in a user; return the access token."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "phone": None,
            "password": password,
            "first_name": "Test",
            "last_name": "Driver",
            "role": role,
        },
    )
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        user.is_verified = True
        db.commit()
    finally:
        db.close()

    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == status.HTTP_200_OK
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# GET /drivers/available  (public endpoint message)
# ---------------------------------------------------------------------------


def test_get_available_drivers_returns_message(client):
    token = _register_and_verify(client, "available_check@example.com")
    resp = client.get("/api/v1/drivers/available", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    assert "Available drivers endpoint" in resp.json()["message"]


# ---------------------------------------------------------------------------
# GET /drivers/me
# ---------------------------------------------------------------------------


def test_get_my_driver_profile_not_found(client):
    """Driver role with no profile yet should return 404."""
    token = _register_and_verify(client, "noprofile@example.com", role="driver")
    resp = client.get("/api/v1/drivers/me", headers=_auth(token))
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert "Driver profile not found" in resp.json()["detail"]


def test_get_my_driver_profile_rider_returns_403(client):
    """Users with rider role cannot access the driver profile endpoint."""
    token = _register_and_verify(client, "riderme@example.com", role="rider")
    resp = client.get("/api/v1/drivers/me", headers=_auth(token))
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_get_my_driver_profile_unverified_returns_403(client):
    """Unverified users should not be able to access driver endpoints."""
    email = "unverifieddriver@example.com"
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "phone": None,
            "password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "Driver",
            "role": "driver",
        },
    )
    # Do NOT verify — log in while unverified.
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "StrongPass123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == status.HTTP_200_OK
    token = resp.json()["access_token"]

    resp = client.get("/api/v1/drivers/me", headers=_auth(token))
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_get_my_driver_profile_with_profile_present(client):
    """After creating a profile, GET /drivers/me should return it."""
    token = _register_and_verify(client, "withprofile@example.com", role="driver")

    # Create profile via availability toggle (auto-creates profile).
    client.put(
        "/api/v1/drivers/me/availability",
        json={"is_available": True},
        headers=_auth(token),
    )

    resp = client.get("/api/v1/drivers/me", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["is_available"] is True


# ---------------------------------------------------------------------------
# PUT /drivers/me/availability
# ---------------------------------------------------------------------------


def test_update_driver_availability_creates_profile(client):
    """First availability toggle implicitly creates the driver profile."""
    token = _register_and_verify(client, "newavail@example.com", role="driver")
    resp = client.put(
        "/api/v1/drivers/me/availability",
        json={"is_available": True},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["is_available"] is True


def test_update_driver_availability_toggles(client):
    """Availability can be toggled on and off."""
    token = _register_and_verify(client, "toggle@example.com", role="driver")

    client.put(
        "/api/v1/drivers/me/availability",
        json={"is_available": True},
        headers=_auth(token),
    )

    resp = client.put(
        "/api/v1/drivers/me/availability",
        json={"is_available": False},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["is_available"] is False


def test_update_driver_availability_rider_returns_403(client):
    """Riders cannot update driver availability."""
    token = _register_and_verify(client, "rideravail@example.com", role="rider")
    resp = client.put(
        "/api/v1/drivers/me/availability",
        json={"is_available": True},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_update_driver_availability_requires_auth(client):
    resp = client.put("/api/v1/drivers/me/availability", json={"is_available": True})
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# POST /drivers/profile  (stub endpoint)
# ---------------------------------------------------------------------------


def test_create_driver_profile_stub(client):
    token = _register_and_verify(client, "createprofile@example.com", role="driver")
    resp = client.post("/api/v1/drivers/profile", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    assert "Create driver profile endpoint" in resp.json()["message"]
