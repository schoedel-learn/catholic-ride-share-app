"""Admin endpoint tests."""

from fastapi import status

from app.db.session import SessionLocal
from app.models.driver_profile import DriverProfile
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_verified_user(
    client, email: str, role: str = "rider", password: str = "StrongPass123!"
) -> int:
    """Register and verify a user; return their DB id."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "phone": None,
            "password": password,
            "first_name": "Test",
            "last_name": "User",
            "role": role,
        },
    )
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    user.is_verified = True
    db.commit()
    user_id = user.id
    db.close()
    return user_id


def _login_token(client, email: str, password: str = "StrongPass123!") -> str:
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == status.HTTP_200_OK
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_driver_profile(user_id: int, status: str = "pending") -> None:
    db = SessionLocal()
    profile = DriverProfile(user_id=user_id, background_check_status=status)
    db.add(profile)
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# GET /admin/drivers
# ---------------------------------------------------------------------------


def test_admin_get_all_drivers(client):
    admin_id = _create_verified_user(client, "admin@example.com", role="admin")
    driver_id = _create_verified_user(client, "d1@example.com", role="driver")
    _create_driver_profile(driver_id)

    token = _login_token(client, "admin@example.com")
    resp = client.get("/api/v1/admin/drivers", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) >= 1


def test_non_admin_cannot_list_drivers(client):
    _create_verified_user(client, "rider_admin_test@example.com", role="rider")
    token = _login_token(client, "rider_admin_test@example.com")
    resp = client.get("/api/v1/admin/drivers", headers=_auth(token))
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_unauthenticated_cannot_list_drivers(client):
    resp = client.get("/api/v1/admin/drivers")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# PUT /admin/drivers/{user_id}/verify
# ---------------------------------------------------------------------------


def test_admin_verify_driver_approves(client):
    _create_verified_user(client, "verifyadmin@example.com", role="admin")
    driver_id = _create_verified_user(client, "dverify@example.com", role="driver")
    _create_driver_profile(driver_id, status="pending")

    token = _login_token(client, "verifyadmin@example.com")
    resp = client.put(
        f"/api/v1/admin/drivers/{driver_id}/verify",
        json={"background_check_status": "approved"},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["background_check_status"] == "approved"


def test_admin_verify_driver_not_found(client):
    _create_verified_user(client, "notfoundadmin@example.com", role="admin")
    token = _login_token(client, "notfoundadmin@example.com")
    resp = client.put(
        "/api/v1/admin/drivers/99999/verify",
        json={"background_check_status": "approved"},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_admin_update_training_notes(client):
    _create_verified_user(client, "trainingadmin@example.com", role="admin")
    driver_id = _create_verified_user(client, "dtraining@example.com", role="driver")
    _create_driver_profile(driver_id)

    token = _login_token(client, "trainingadmin@example.com")
    resp = client.put(
        f"/api/v1/admin/drivers/{driver_id}/verify",
        json={"admin_notes": "Completed safe environment training"},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["admin_notes"] == "Completed safe environment training"


# ---------------------------------------------------------------------------
# GET /admin/parish/stats
# ---------------------------------------------------------------------------


def test_admin_parish_stats(client):
    _create_verified_user(client, "statsadmin@example.com", role="admin")
    token = _login_token(client, "statsadmin@example.com")

    resp = client.get("/api/v1/admin/parish/stats", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert "total_drivers" in data
    assert "verified_drivers" in data
    assert "pending_drivers" in data
    assert "total_ride_requests" in data
    assert "completed_rides" in data


# ---------------------------------------------------------------------------
# GET /admin/parish/rides
# ---------------------------------------------------------------------------


def test_admin_parish_rides(client):
    _create_verified_user(client, "ridesadmin@example.com", role="admin")
    token = _login_token(client, "ridesadmin@example.com")

    resp = client.get("/api/v1/admin/parish/rides", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.json(), list)


# ---------------------------------------------------------------------------
# Coordinator — cannot change background_check_status
# ---------------------------------------------------------------------------


def test_coordinator_cannot_change_background_check_status(client):
    _create_verified_user(client, "coord@example.com", role="coordinator")
    driver_id = _create_verified_user(client, "dcoord@example.com", role="driver")
    _create_driver_profile(driver_id)

    # Assign coordinator to a parish so the query works.
    db = SessionLocal()
    coord = db.query(User).filter(User.email == "coord@example.com").first()
    driver_user = db.query(User).filter(User.id == driver_id).first()
    coord.parish_id = 1
    driver_user.parish_id = 1
    db.commit()
    db.close()

    token = _login_token(client, "coord@example.com")
    resp = client.put(
        f"/api/v1/admin/drivers/{driver_id}/verify",
        json={"background_check_status": "approved"},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert "background check status" in resp.json()["detail"].lower()
