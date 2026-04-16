"""Tests for admin endpoints: driver verification, approval/rejection, stats."""

from fastapi import status

from app.db.session import SessionLocal
from app.models.driver_profile import DriverProfile
from app.models.user import User

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _register(
    client,
    *,
    email: str,
    phone: str,
    password: str,
    role: str = "rider",
) -> None:
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


def _verify(email: str) -> None:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    user.is_verified = True
    db.commit()
    db.close()


def _make_admin(email: str) -> None:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    user.role = "admin"
    db.commit()
    db.close()


def _make_coordinator(email: str) -> None:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    user.role = "coordinator"
    db.commit()
    db.close()


def _ensure_driver_profile(email: str) -> None:
    """Create a pending driver profile for the user if one doesn't exist."""
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    profile = db.query(DriverProfile).filter(DriverProfile.user_id == user.id).first()
    if not profile:
        profile = DriverProfile(user_id=user.id)
        db.add(profile)
        db.commit()
    db.close()


def _get_user_id(email: str) -> int:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    uid = user.id
    db.close()
    return uid


def _login(client, email: str, password: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# Tests: approve/reject driver
# ---------------------------------------------------------------------------


def test_admin_can_approve_driver(client):
    """Admin can set a driver's background_check_status to 'approved'."""
    password = "StrongPass123!"

    admin_email = "admin_approve@example.com"
    _register(client, email=admin_email, phone="+15552220001", password=password, role="rider")
    _verify(admin_email)
    _make_admin(admin_email)

    driver_email = "drv_toapprove@example.com"
    _register(client, email=driver_email, phone="+15552220002", password=password, role="driver")
    _verify(driver_email)
    _ensure_driver_profile(driver_email)
    driver_user_id = _get_user_id(driver_email)

    admin_token = _login(client, admin_email, password)
    resp = client.post(
        f"/api/v1/admin/drivers/{driver_user_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    assert resp.json()["background_check_status"] == "approved"


def test_admin_can_reject_driver_with_reason(client):
    """Admin can reject a driver and store a reason in admin_notes."""
    password = "StrongPass123!"

    admin_email = "admin_reject@example.com"
    _register(client, email=admin_email, phone="+15552220003", password=password, role="rider")
    _verify(admin_email)
    _make_admin(admin_email)

    driver_email = "drv_toreject@example.com"
    _register(client, email=driver_email, phone="+15552220004", password=password, role="driver")
    _verify(driver_email)
    _ensure_driver_profile(driver_email)
    driver_user_id = _get_user_id(driver_email)

    admin_token = _login(client, admin_email, password)
    resp = client.post(
        f"/api/v1/admin/drivers/{driver_user_id}/reject",
        json={"reason": "Background check failed"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    data = resp.json()
    assert data["background_check_status"] == "rejected"
    assert data["admin_notes"] == "Background check failed"


def test_coordinator_cannot_approve_driver(client):
    """Coordinators are not allowed to approve drivers — only global admins can."""
    password = "StrongPass123!"

    coord_email = "coord_noapprove@example.com"
    _register(client, email=coord_email, phone="+15552220005", password=password, role="rider")
    _verify(coord_email)
    _make_coordinator(coord_email)

    driver_email = "drv_coord_test@example.com"
    _register(client, email=driver_email, phone="+15552220006", password=password, role="driver")
    _verify(driver_email)
    _ensure_driver_profile(driver_email)
    driver_user_id = _get_user_id(driver_email)

    coord_token = _login(client, coord_email, password)
    resp = client.post(
        f"/api/v1/admin/drivers/{driver_user_id}/approve",
        headers={"Authorization": f"Bearer {coord_token}"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_regular_user_cannot_access_admin_endpoints(client):
    """A normal rider should receive 403 when hitting admin endpoints."""
    password = "StrongPass123!"

    rider_email = "rider_noadmin@example.com"
    _register(client, email=rider_email, phone="+15552220007", password=password, role="rider")
    _verify(rider_email)
    rider_token = _login(client, rider_email, password)

    resp = client.get(
        "/api/v1/admin/drivers",
        headers={"Authorization": f"Bearer {rider_token}"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_approve_nonexistent_driver_returns_404(client):
    """Approving a user who has no driver profile returns 404."""
    password = "StrongPass123!"

    admin_email = "admin_404@example.com"
    _register(client, email=admin_email, phone="+15552220008", password=password, role="rider")
    _verify(admin_email)
    _make_admin(admin_email)
    admin_token = _login(client, admin_email, password)

    resp = client.post(
        "/api/v1/admin/drivers/999999/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Tests: driver training update (existing PUT verify endpoint)
# ---------------------------------------------------------------------------


def test_admin_can_update_driver_training(client):
    """Admin can update training dates via PUT /admin/drivers/{id}/verify."""
    password = "StrongPass123!"

    admin_email = "admin_training@example.com"
    _register(client, email=admin_email, phone="+15552220009", password=password, role="rider")
    _verify(admin_email)
    _make_admin(admin_email)

    driver_email = "drv_training@example.com"
    _register(client, email=driver_email, phone="+15552220010", password=password, role="driver")
    _verify(driver_email)
    _ensure_driver_profile(driver_email)
    driver_user_id = _get_user_id(driver_email)

    admin_token = _login(client, admin_email, password)
    resp = client.put(
        f"/api/v1/admin/drivers/{driver_user_id}/verify",
        json={
            "training_completed_date": "2026-01-15T00:00:00",
            "training_expiration_date": "2028-01-15T00:00:00",
            "admin_notes": "Completed Safe Environment training",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    data = resp.json()
    assert data["admin_notes"] == "Completed Safe Environment training"


def test_coordinator_cannot_change_background_check_status(client):
    """Coordinators can update training dates but not background_check_status."""
    password = "StrongPass123!"

    coord_email = "coord_bgcheck@example.com"
    _register(client, email=coord_email, phone="+15552220011", password=password, role="rider")
    _verify(coord_email)
    _make_coordinator(coord_email)

    driver_email = "drv_bgcheck@example.com"
    _register(client, email=driver_email, phone="+15552220012", password=password, role="driver")
    _verify(driver_email)
    _ensure_driver_profile(driver_email)
    driver_user_id = _get_user_id(driver_email)

    coord_token = _login(client, coord_email, password)
    resp = client.put(
        f"/api/v1/admin/drivers/{driver_user_id}/verify",
        json={"background_check_status": "approved"},
        headers={"Authorization": f"Bearer {coord_token}"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Tests: stats and ride listing
# ---------------------------------------------------------------------------


def test_admin_can_see_parish_stats(client):
    """GET /admin/parish/stats returns a stats dict for admins."""
    password = "StrongPass123!"

    admin_email = "admin_stats@example.com"
    _register(client, email=admin_email, phone="+15552220013", password=password, role="rider")
    _verify(admin_email)
    _make_admin(admin_email)
    admin_token = _login(client, admin_email, password)

    resp = client.get(
        "/api/v1/admin/parish/stats",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    data = resp.json()
    assert "total_drivers" in data
    assert "verified_drivers" in data
    assert "total_ride_requests" in data
