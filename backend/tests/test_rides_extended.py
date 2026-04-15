"""Additional ride endpoint edge-case tests."""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import status

from app.db.session import SessionLocal
from app.models.driver_profile import DriverProfile
from app.models.ride import Ride, RideStatus
from app.models.ride_request import RideRequest, RideRequestStatus
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _register_and_verify(
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


def _create_approved_driver(client, email: str) -> tuple[int, str]:
    """Create a driver with an approved profile; return (user_id, token)."""
    user_id = _register_and_verify(client, email, role="driver")
    db = SessionLocal()
    profile = DriverProfile(user_id=user_id, background_check_status="approved")
    db.add(profile)
    db.commit()
    db.close()
    return user_id, _login_token(client, email)


def _create_ride_directly(rider_id: int, driver_id: int, ride_status: str) -> tuple[int, int]:
    """Insert a ride and ride_request directly; return (ride_id, ride_request_id)."""
    db = SessionLocal()
    ride_request = RideRequest(
        rider_id=rider_id,
        destination_type="mass",
        requested_datetime=datetime.utcnow() + timedelta(hours=1),
        status=RideRequestStatus.ACCEPTED,
        pickup_location="POINT(-122.4194 37.7749)",
        destination_location="POINT(-122.4094 37.7849)",
    )
    db.add(ride_request)
    db.flush()

    ride = Ride(
        ride_request_id=ride_request.id,
        driver_id=driver_id,
        rider_id=rider_id,
        status=ride_status,
        accepted_at=datetime.utcnow(),
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)
    ride_id = ride.id
    rr_id = ride_request.id
    db.close()
    return ride_id, rr_id


# ---------------------------------------------------------------------------
# Unverified users cannot access ride endpoints
# ---------------------------------------------------------------------------


def test_unverified_user_cannot_create_ride_request(client):
    email = "unverifiedrider@example.com"
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "phone": None,
            "password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "Rider",
            "role": "rider",
        },
    )
    token = _login_token(client, email)

    resp = client.post(
        "/api/v1/rides/",
        json={
            "pickup": {"latitude": 37.77, "longitude": -122.41},
            "dropoff": {"latitude": 37.78, "longitude": -122.40},
            "destination_type": "mass",
            "requested_datetime": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        },
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Riders cannot access driver-only endpoints
# ---------------------------------------------------------------------------


def test_rider_cannot_view_open_rides(client):
    rider_id = _register_and_verify(client, "rideropens@example.com", role="rider")
    token = _login_token(client, "rideropens@example.com")
    resp = client.get("/api/v1/rides/open", headers=_auth(token))
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_rider_cannot_view_assigned_rides(client):
    rider_id = _register_and_verify(client, "riderassigned@example.com", role="rider")
    token = _login_token(client, "riderassigned@example.com")
    resp = client.get("/api/v1/rides/assigned", headers=_auth(token))
    assert resp.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Non-approved drivers cannot accept rides
# ---------------------------------------------------------------------------


def test_unverified_driver_cannot_accept_ride(client):
    rider_id = _register_and_verify(client, "ridernoapprove@example.com", role="rider")
    driver_id = _register_and_verify(client, "drivernoapprove@example.com", role="driver")
    # Driver has a profile but NOT approved
    db = SessionLocal()
    profile = DriverProfile(user_id=driver_id, background_check_status="pending")
    db.add(profile)
    db.commit()
    db.close()

    # Create a ride request directly in the DB.
    db = SessionLocal()
    rr = RideRequest(
        rider_id=rider_id,
        destination_type="mass",
        requested_datetime=datetime.utcnow() + timedelta(hours=2),
        status=RideRequestStatus.PENDING,
        pickup_location="POINT(-122.4194 37.7749)",
        destination_location="POINT(-122.4094 37.7849)",
    )
    db.add(rr)
    db.commit()
    rr_id = rr.id
    db.close()

    driver_token = _login_token(client, "drivernoapprove@example.com")
    resp = client.post(f"/api/v1/rides/{rr_id}/accept", headers=_auth(driver_token))
    assert resp.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Status update edge cases
# ---------------------------------------------------------------------------


def test_update_ride_status_ride_not_found(client):
    _, driver_token = _create_approved_driver(client, "drivernotfound@example.com")
    resp = client.patch(
        "/api/v1/rides/99999/status",
        json={"status": "in_progress"},
        headers=_auth(driver_token),
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_update_ride_status_not_your_ride(client):
    rider_id = _register_and_verify(client, "ridernotyours@example.com", role="rider")
    driver1_id, driver1_token = _create_approved_driver(client, "driver1notyours@example.com")
    driver2_id, driver2_token = _create_approved_driver(client, "driver2notyours@example.com")

    ride_id, _ = _create_ride_directly(rider_id, driver1_id, RideStatus.ACCEPTED)

    resp = client.patch(
        f"/api/v1/rides/{ride_id}/status",
        json={"status": "in_progress"},
        headers=_auth(driver2_token),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_cancel_ride(client):
    rider_id = _register_and_verify(client, "ridercancel@example.com", role="rider")
    driver_id, driver_token = _create_approved_driver(client, "drivercancel@example.com")

    ride_id, _ = _create_ride_directly(rider_id, driver_id, RideStatus.ACCEPTED)

    resp = client.patch(
        f"/api/v1/rides/{ride_id}/status",
        json={"status": "cancelled"},
        headers=_auth(driver_token),
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "cancelled"


def test_driver_enroute_status(client):
    rider_id = _register_and_verify(client, "riderenroute@example.com", role="rider")
    driver_id, driver_token = _create_approved_driver(client, "driverenroute@example.com")

    ride_id, _ = _create_ride_directly(rider_id, driver_id, RideStatus.ACCEPTED)

    resp = client.patch(
        f"/api/v1/rides/{ride_id}/status",
        json={"status": "driver_enroute"},
        headers=_auth(driver_token),
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "driver_enroute"


def test_arrived_status(client):
    rider_id = _register_and_verify(client, "riderarrived@example.com", role="rider")
    driver_id, driver_token = _create_approved_driver(client, "driverarrived@example.com")

    ride_id, _ = _create_ride_directly(rider_id, driver_id, RideStatus.DRIVER_ENROUTE)

    resp = client.patch(
        f"/api/v1/rides/{ride_id}/status",
        json={"status": "arrived"},
        headers=_auth(driver_token),
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "arrived"


# ---------------------------------------------------------------------------
# List /rides/mine returns empty list when no rides exist
# ---------------------------------------------------------------------------


def test_list_mine_empty(client):
    _register_and_verify(client, "minelist@example.com", role="rider")
    token = _login_token(client, "minelist@example.com")
    resp = client.get("/api/v1/rides/mine", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == []


# ---------------------------------------------------------------------------
# Accept ride — business rule checks
# ---------------------------------------------------------------------------


def test_driver_cannot_accept_own_ride_request(client):
    """A driver who is also a rider cannot accept their own request."""
    both_id, both_token = _create_approved_driver(client, "bothrole@example.com")

    # Change role to "both" so they can create a ride request too.
    db = SessionLocal()
    user = db.query(User).filter(User.id == both_id).first()
    assert user is not None
    user.role = "both"
    db.commit()
    db.close()

    # Create ride request as the "both" user.
    rr_resp = client.post(
        "/api/v1/rides/",
        json={
            "pickup": {"latitude": 37.77, "longitude": -122.41},
            "dropoff": {"latitude": 37.78, "longitude": -122.40},
            "destination_type": "mass",
            "requested_datetime": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        },
        headers=_auth(both_token),
    )
    assert rr_resp.status_code == status.HTTP_201_CREATED
    rr_id = rr_resp.json()["id"]

    # Try to accept own request.
    resp = client.post(f"/api/v1/rides/{rr_id}/accept", headers=_auth(both_token))
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "own ride request" in resp.json()["detail"]


def test_driver_cannot_accept_already_accepted_request(client):
    rider_id = _register_and_verify(client, "rideralreadyaccepted@example.com", role="rider")
    driver1_id, driver1_token = _create_approved_driver(
        client, "driver1alreadyaccepted@example.com"
    )
    driver2_id, driver2_token = _create_approved_driver(
        client, "driver2alreadyaccepted@example.com"
    )

    # Create a pending ride request in the DB.
    db = SessionLocal()
    rr = RideRequest(
        rider_id=rider_id,
        destination_type="mass",
        requested_datetime=datetime.utcnow() + timedelta(hours=1),
        status=RideRequestStatus.PENDING,
        pickup_location="POINT(-122.4194 37.7749)",
        destination_location="POINT(-122.4094 37.7849)",
    )
    db.add(rr)
    db.commit()
    rr_id = rr.id
    db.close()

    # Driver 1 accepts.
    resp1 = client.post(f"/api/v1/rides/{rr_id}/accept", headers=_auth(driver1_token))
    assert resp1.status_code == status.HTTP_201_CREATED

    # Driver 2 tries to accept the same request.
    resp2 = client.post(f"/api/v1/rides/{rr_id}/accept", headers=_auth(driver2_token))
    assert resp2.status_code == status.HTTP_400_BAD_REQUEST
