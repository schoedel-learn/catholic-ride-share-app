"""Donation preferences and ride review endpoint tests.

All Stripe calls are mocked so no real payment infrastructure is required.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi import status

from app.db.session import SessionLocal
from app.models.ride import Ride, RideStatus
from app.models.ride_request import RideRequest, RideRequestStatus
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_verified_user(
    client, email: str, role: str = "rider", password: str = "StrongPass123!"
) -> int:
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


def _create_completed_ride(rider_id: int, driver_id: int) -> int:
    """Directly insert a completed ride and its request; return the ride id."""
    db = SessionLocal()
    ride_request = RideRequest(
        rider_id=rider_id,
        destination_type="mass",
        requested_datetime=datetime.utcnow() + timedelta(hours=1),
        status=RideRequestStatus.COMPLETED,
        pickup_location="POINT(-122.4194 37.7749)",
        destination_location="POINT(-122.4094 37.7849)",
    )
    db.add(ride_request)
    db.flush()

    ride = Ride(
        ride_request_id=ride_request.id,
        driver_id=driver_id,
        rider_id=rider_id,
        status=RideStatus.COMPLETED,
        accepted_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)
    ride_id = ride.id
    db.close()
    return ride_id


def _create_pending_ride(rider_id: int, driver_id: int) -> int:
    """Insert an accepted (non-completed) ride; return the ride id."""
    db = SessionLocal()
    ride_request = RideRequest(
        rider_id=rider_id,
        destination_type="mass",
        requested_datetime=datetime.utcnow() + timedelta(hours=2),
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
        status=RideStatus.ACCEPTED,
        accepted_at=datetime.utcnow(),
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)
    ride_id = ride.id
    db.close()
    return ride_id


# ---------------------------------------------------------------------------
# GET /users/me/donation-preferences
# ---------------------------------------------------------------------------


def test_get_donation_preferences_defaults(client):
    rider_id = _create_verified_user(client, "prefdefault@example.com")
    token = _login_token(client, "prefdefault@example.com")

    resp = client.get("/api/v1/users/me/donation-preferences", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["auto_donation_enabled"] is False
    assert data["auto_donation_type"] in ("fixed", "distance_based")


# ---------------------------------------------------------------------------
# PUT /users/me/donation-preferences
# ---------------------------------------------------------------------------


def test_update_donation_preferences_fixed(client):
    _create_verified_user(client, "preffixed@example.com")
    token = _login_token(client, "preffixed@example.com")

    resp = client.put(
        "/api/v1/users/me/donation-preferences",
        json={
            "auto_donation_enabled": True,
            "auto_donation_type": "fixed",
            "auto_donation_amount": 10.00,
        },
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["auto_donation_enabled"] is True
    assert data["auto_donation_type"] == "fixed"
    assert data["auto_donation_amount"] == pytest.approx(10.00)


def test_update_donation_preferences_distance_based(client):
    _create_verified_user(client, "prefdist@example.com")
    token = _login_token(client, "prefdist@example.com")

    resp = client.put(
        "/api/v1/users/me/donation-preferences",
        json={
            "auto_donation_enabled": True,
            "auto_donation_type": "distance_based",
            "auto_donation_multiplier": 0.75,
        },
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["auto_donation_type"] == "distance_based"
    assert data["auto_donation_multiplier"] == pytest.approx(0.75)


def test_update_fixed_preferences_without_amount_returns_400(client):
    _create_verified_user(client, "prefnoamt@example.com")
    token = _login_token(client, "prefnoamt@example.com")

    resp = client.put(
        "/api/v1/users/me/donation-preferences",
        json={
            "auto_donation_enabled": True,
            "auto_donation_type": "fixed",
            # auto_donation_amount intentionally omitted
        },
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "auto_donation_amount" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# GET /users/me/donations
# ---------------------------------------------------------------------------


def test_list_donations_empty(client):
    _create_verified_user(client, "nodonations@example.com")
    token = _login_token(client, "nodonations@example.com")

    resp = client.get("/api/v1/users/me/donations", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == []


# ---------------------------------------------------------------------------
# POST /rides/{ride_id}/donate
# ---------------------------------------------------------------------------


def test_donate_ride_not_found(client):
    _create_verified_user(client, "donate404@example.com")
    token = _login_token(client, "donate404@example.com")

    resp = client.post(
        "/api/v1/rides/99999/donate",
        json={"donation_amount": 5.00},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_donate_not_your_ride(client):
    rider_id = _create_verified_user(client, "riderdonateother@example.com")
    driver_id = _create_verified_user(client, "driverdonateother@example.com", role="driver")
    ride_id = _create_completed_ride(rider_id, driver_id)

    # A different user tries to donate
    other_id = _create_verified_user(client, "otherdonor@example.com")
    token = _login_token(client, "otherdonor@example.com")

    resp = client.post(
        f"/api/v1/rides/{ride_id}/donate",
        json={"donation_amount": 5.00},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_donate_ride_not_completed(client):
    rider_id = _create_verified_user(client, "riderinprogress@example.com")
    driver_id = _create_verified_user(client, "driverinprogress@example.com", role="driver")
    ride_id = _create_pending_ride(rider_id, driver_id)

    token = _login_token(client, "riderinprogress@example.com")
    resp = client.post(
        f"/api/v1/rides/{ride_id}/donate",
        json={"donation_amount": 5.00},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "completion" in resp.json()["detail"].lower()


def test_donate_stripe_not_configured_returns_503(client, monkeypatch):
    from app.services import payment as payment_module

    monkeypatch.setattr(
        payment_module.PaymentService,
        "__init__",
        lambda self: (_ for _ in ()).throw(payment_module.StripeNotConfiguredError("not configured")),
    )

    rider_id = _create_verified_user(client, "riderstripe503@example.com")
    driver_id = _create_verified_user(client, "driverstripe503@example.com", role="driver")
    ride_id = _create_completed_ride(rider_id, driver_id)

    token = _login_token(client, "riderstripe503@example.com")
    resp = client.post(
        f"/api/v1/rides/{ride_id}/donate",
        json={"donation_amount": 5.00},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


# ---------------------------------------------------------------------------
# POST /rides/{ride_id}/review
# ---------------------------------------------------------------------------


def test_submit_review_without_donation(client):
    rider_id = _create_verified_user(client, "reviewer@example.com")
    driver_id = _create_verified_user(client, "driverreview@example.com", role="driver")
    ride_id = _create_completed_ride(rider_id, driver_id)

    token = _login_token(client, "reviewer@example.com")
    resp = client.post(
        f"/api/v1/rides/{ride_id}/review",
        json={"rating": 5, "comment": "Great ride!"},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["rating"] == 5
    assert data["comment"] == "Great ride!"
    assert data["donation"] is None
    assert data["donation_intent"] is None


def test_submit_duplicate_review_returns_400(client):
    rider_id = _create_verified_user(client, "dupreviewer@example.com")
    driver_id = _create_verified_user(client, "dupdriverrev@example.com", role="driver")
    ride_id = _create_completed_ride(rider_id, driver_id)

    token = _login_token(client, "dupreviewer@example.com")

    client.post(
        f"/api/v1/rides/{ride_id}/review",
        json={"rating": 4, "comment": "Good."},
        headers=_auth(token),
    )

    resp = client.post(
        f"/api/v1/rides/{ride_id}/review",
        json={"rating": 3, "comment": "Changed my mind."},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "already submitted" in resp.json()["detail"]


def test_submit_review_wrong_ride_returns_403(client):
    rider_id = _create_verified_user(client, "reviewwrong@example.com")
    driver_id = _create_verified_user(client, "driverreviewwrong@example.com", role="driver")
    ride_id = _create_completed_ride(rider_id, driver_id)

    other_id = _create_verified_user(client, "otherreviewwrong@example.com")
    token = _login_token(client, "otherreviewwrong@example.com")

    resp = client.post(
        f"/api/v1/rides/{ride_id}/review",
        json={"rating": 5},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_submit_review_ride_not_completed_returns_400(client):
    rider_id = _create_verified_user(client, "reviewnotdone@example.com")
    driver_id = _create_verified_user(client, "driverreviewnotdone@example.com", role="driver")
    ride_id = _create_pending_ride(rider_id, driver_id)

    token = _login_token(client, "reviewnotdone@example.com")
    resp = client.post(
        f"/api/v1/rides/{ride_id}/review",
        json={"rating": 5},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_submit_review_ride_not_found_returns_404(client):
    _create_verified_user(client, "reviewnotfound@example.com")
    token = _login_token(client, "reviewnotfound@example.com")

    resp = client.post(
        "/api/v1/rides/99999/review",
        json={"rating": 5},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# GET /rides/{ride_id}/donation-intent
# ---------------------------------------------------------------------------


def test_get_donation_intent_not_found(client):
    rider_id = _create_verified_user(client, "intentnotfound@example.com")
    driver_id = _create_verified_user(client, "driverintent@example.com", role="driver")
    ride_id = _create_completed_ride(rider_id, driver_id)

    token = _login_token(client, "intentnotfound@example.com")
    resp = client.get(f"/api/v1/rides/{ride_id}/donation-intent", headers=_auth(token))
    assert resp.status_code == status.HTTP_404_NOT_FOUND
