"""Tests for driver profile management and driver discovery."""

from fastapi import status

from app.db.session import SessionLocal
from app.models.driver_profile import DriverProfile
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _register_and_verify(client, *, email: str, phone: str, password: str, role: str) -> None:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "phone": phone,
            "password": password,
            "first_name": "Test",
            "last_name": "User",
            "role": role,
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.text

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    user.is_verified = True
    db.commit()
    db.close()


def _approve_driver_db(email: str) -> None:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    profile = db.query(DriverProfile).filter(DriverProfile.user_id == user.id).first()
    if not profile:
        profile = DriverProfile(user_id=user.id, background_check_status="approved")
        db.add(profile)
    else:
        profile.background_check_status = "approved"
    db.commit()
    db.close()


def _login(client, email: str, password: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# Tests: driver profile upsert
# ---------------------------------------------------------------------------


def test_driver_can_create_and_update_profile(client):
    """POST /drivers/profile creates a profile; calling it again updates it."""
    email = "dp_create@example.com"
    password = "StrongPass123!"
    _register_and_verify(client, email=email, phone="+15551110001", password=password, role="driver")
    token = _login(client, email, password)
    headers = {"Authorization": f"Bearer {token}"}

    # First call: create
    resp = client.post(
        "/api/v1/drivers/profile",
        json={
            "vehicle_make": "Toyota",
            "vehicle_model": "Camry",
            "vehicle_year": 2020,
            "vehicle_color": "Silver",
            "license_plate": "ABC123",
            "vehicle_capacity": 4,
        },
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    data = resp.json()
    assert data["vehicle_make"] == "Toyota"
    assert data["vehicle_model"] == "Camry"
    assert data["vehicle_year"] == 2020
    assert data["background_check_status"] == "pending"

    # Second call (upsert): update model only
    resp2 = client.post(
        "/api/v1/drivers/profile",
        json={"vehicle_model": "Corolla"},
        headers=headers,
    )
    assert resp2.status_code == status.HTTP_200_OK, resp2.text
    data2 = resp2.json()
    assert data2["vehicle_model"] == "Corolla"
    assert data2["vehicle_make"] == "Toyota"  # unchanged


def test_non_driver_cannot_create_profile(client):
    """A rider role should be refused when calling POST /drivers/profile."""
    email = "rider_no_dp@example.com"
    password = "StrongPass123!"
    _register_and_verify(
        client, email=email, phone="+15551110002", password=password, role="rider"
    )
    token = _login(client, email, password)

    resp = client.post(
        "/api/v1/drivers/profile",
        json={"vehicle_make": "Ford"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_driver_put_me_updates_profile(client):
    """PUT /drivers/me updates vehicle details on an existing profile."""
    email = "dp_put@example.com"
    password = "StrongPass123!"
    _register_and_verify(
        client, email=email, phone="+15551110003", password=password, role="driver"
    )
    token = _login(client, email, password)
    headers = {"Authorization": f"Bearer {token}"}

    # Create profile first
    client.post(
        "/api/v1/drivers/profile",
        json={"vehicle_make": "Honda", "vehicle_capacity": 5},
        headers=headers,
    )

    # Update via PUT /me
    resp = client.put(
        "/api/v1/drivers/me",
        json={"vehicle_capacity": 7},
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    assert resp.json()["vehicle_capacity"] == 7
    assert resp.json()["vehicle_make"] == "Honda"  # unchanged


def test_put_me_404_when_no_profile(client):
    """PUT /drivers/me returns 404 if the driver hasn't created a profile yet."""
    email = "dp_no_profile@example.com"
    password = "StrongPass123!"
    _register_and_verify(
        client, email=email, phone="+15551110004", password=password, role="driver"
    )
    token = _login(client, email, password)

    resp = client.put(
        "/api/v1/drivers/me",
        json={"vehicle_capacity": 3},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Tests: availability toggle
# ---------------------------------------------------------------------------


def test_driver_availability_toggle(client):
    """PUT /drivers/me/availability creates a profile on first use and toggles it."""
    email = "dp_avail@example.com"
    password = "StrongPass123!"
    _register_and_verify(
        client, email=email, phone="+15551110005", password=password, role="driver"
    )
    token = _login(client, email, password)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.put(
        "/api/v1/drivers/me/availability",
        json={"is_available": True},
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    assert resp.json()["is_available"] is True

    resp2 = client.put(
        "/api/v1/drivers/me/availability",
        json={"is_available": False},
        headers=headers,
    )
    assert resp2.status_code == status.HTTP_200_OK
    assert resp2.json()["is_available"] is False


# ---------------------------------------------------------------------------
# Tests: driver discovery
# ---------------------------------------------------------------------------


def test_get_available_drivers_empty_initially(client):
    """GET /drivers/available returns an empty list when no approved drivers exist."""
    email = "rider_discovery@example.com"
    password = "StrongPass123!"
    _register_and_verify(
        client, email=email, phone="+15551110006", password=password, role="rider"
    )
    token = _login(client, email, password)

    resp = client.get(
        "/api/v1/drivers/available",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    assert resp.json() == []


def test_get_available_drivers_shows_approved_only(client):
    """Only approved, available drivers appear in /drivers/available."""
    password = "StrongPass123!"

    # Approved available driver
    approved_email = "driver_approved@example.com"
    _register_and_verify(
        client, email=approved_email, phone="+15551110007", password=password, role="driver"
    )
    _approve_driver_db(approved_email)
    approved_token = _login(client, approved_email, password)
    client.put(
        "/api/v1/drivers/me/availability",
        json={"is_available": True},
        headers={"Authorization": f"Bearer {approved_token}"},
    )

    # Pending driver (not approved)
    pending_email = "driver_pending@example.com"
    _register_and_verify(
        client, email=pending_email, phone="+15551110008", password=password, role="driver"
    )
    pending_token = _login(client, pending_email, password)
    client.put(
        "/api/v1/drivers/me/availability",
        json={"is_available": True},
        headers={"Authorization": f"Bearer {pending_token}"},
    )

    # Rider making the discovery request
    rider_email = "rider_seeker@example.com"
    _register_and_verify(
        client, email=rider_email, phone="+15551110009", password=password, role="rider"
    )
    rider_token = _login(client, rider_email, password)

    resp = client.get(
        "/api/v1/drivers/available",
        headers={"Authorization": f"Bearer {rider_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    drivers = resp.json()
    assert len(drivers) == 1
    # Should not expose license_plate in the public response
    assert "license_plate" not in drivers[0]
    assert "vehicle_capacity" in drivers[0]


def test_get_my_driver_profile(client):
    """GET /drivers/me returns the current driver's full profile."""
    email = "dp_getme@example.com"
    password = "StrongPass123!"
    _register_and_verify(
        client, email=email, phone="+15551110010", password=password, role="driver"
    )
    token = _login(client, email, password)
    headers = {"Authorization": f"Bearer {token}"}

    # Create profile first
    client.post(
        "/api/v1/drivers/profile",
        json={"vehicle_make": "Chevy", "vehicle_year": 2019},
        headers=headers,
    )

    resp = client.get("/api/v1/drivers/me", headers=headers)
    assert resp.status_code == status.HTTP_200_OK, resp.text
    data = resp.json()
    assert data["vehicle_make"] == "Chevy"
    # Full profile includes the license_plate field (even if None)
    assert "license_plate" in data
