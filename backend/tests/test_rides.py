from datetime import datetime, timedelta

from fastapi import status

from app.db.session import SessionLocal
from app.models.driver_profile import DriverProfile
from app.models.user import User


def _verify_user(email: str) -> None:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    user.is_verified = True
    db.commit()
    db.close()


def _approve_driver(email: str) -> None:
    """Create (or update) an approved driver profile for the given user e-mail."""
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


def test_rider_creates_and_driver_accepts_ride(client):
    rider_email = "rider@example.com"
    driver_email = "driver@example.com"
    password = "StrongPass123!"

    rider_payload = {
        "email": rider_email,
        "phone": "+15550000001",
        "password": password,
        "first_name": "Rider",
        "last_name": "One",
        "role": "rider",
    }
    driver_payload = {
        "email": driver_email,
        "phone": "+15550000002",
        "password": password,
        "first_name": "Driver",
        "last_name": "One",
        "role": "driver",
    }

    rider_resp = client.post("/api/v1/auth/register", json=rider_payload)
    driver_resp = client.post("/api/v1/auth/register", json=driver_payload)
    assert rider_resp.status_code == status.HTTP_201_CREATED
    assert driver_resp.status_code == status.HTTP_201_CREATED

    _verify_user(rider_email)
    _verify_user(driver_email)
    _approve_driver(driver_email)

    rider_token = _login(client, rider_email, password)
    driver_token = _login(client, driver_email, password)

    rider_headers = {"Authorization": f"Bearer {rider_token}"}
    driver_headers = {"Authorization": f"Bearer {driver_token}"}

    ride_request_payload = {
        "pickup": {"latitude": 37.7749, "longitude": -122.4194},
        "dropoff": {"latitude": 37.7849, "longitude": -122.4094},
        "destination_type": "mass",
        "requested_datetime": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        "notes": "Need a ride to the vigil Mass.",
        "passenger_count": 2,
    }

    create_resp = client.post("/api/v1/rides/", json=ride_request_payload, headers=rider_headers)
    assert create_resp.status_code == status.HTTP_201_CREATED, create_resp.text
    ride_request = create_resp.json()
    ride_request_id = ride_request["id"]
    assert ride_request["status"] == "pending"

    open_resp = client.get("/api/v1/rides/open", headers=driver_headers)
    assert open_resp.status_code == status.HTTP_200_OK
    open_ids = [r["id"] for r in open_resp.json()]
    assert ride_request_id in open_ids

    accept_resp = client.post(f"/api/v1/rides/{ride_request_id}/accept", headers=driver_headers)
    assert accept_resp.status_code == status.HTTP_201_CREATED, accept_resp.text
    ride = accept_resp.json()
    ride_id = ride["id"]
    assert ride["status"] == "accepted"

    assigned = client.get("/api/v1/rides/assigned", headers=driver_headers)
    assert assigned.status_code == status.HTTP_200_OK
    assigned_ids = [r["id"] for r in assigned.json()]
    assert ride_id in assigned_ids

    in_progress = client.patch(
        f"/api/v1/rides/{ride_id}/status",
        json={"status": "driver_enroute"},
        headers=driver_headers,
    )
    assert in_progress.status_code == status.HTTP_200_OK, in_progress.text
    assert in_progress.json()["status"] == "driver_enroute"

    arrived = client.patch(
        f"/api/v1/rides/{ride_id}/status",
        json={"status": "arrived"},
        headers=driver_headers,
    )
    assert arrived.status_code == status.HTTP_200_OK, arrived.text
    assert arrived.json()["status"] == "arrived"

    picked_up = client.patch(
        f"/api/v1/rides/{ride_id}/status",
        json={"status": "picked_up"},
        headers=driver_headers,
    )
    assert picked_up.status_code == status.HTTP_200_OK, picked_up.text
    assert picked_up.json()["status"] == "picked_up"

    in_progress2 = client.patch(
        f"/api/v1/rides/{ride_id}/status",
        json={"status": "in_progress"},
        headers=driver_headers,
    )
    assert in_progress2.status_code == status.HTTP_200_OK, in_progress2.text
    assert in_progress2.json()["status"] == "in_progress"

    completed = client.patch(
        f"/api/v1/rides/{ride_id}/status",
        json={"status": "completed"},
        headers=driver_headers,
    )
    assert completed.status_code == status.HTTP_200_OK
    assert completed.json()["status"] == "completed"

    rider_rides = client.get("/api/v1/rides/mine", headers=rider_headers)
    assert rider_rides.status_code == status.HTTP_200_OK
    mine = rider_rides.json()
    assert mine[0]["status"] == "completed"


def test_rider_can_cancel_pending_request(client):
    """Rider cancels a pending ride request before a driver accepts it."""
    rider_email = "cancel_rider@example.com"
    password = "StrongPass123!"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": rider_email,
            "phone": "+15550000010",
            "password": password,
            "first_name": "Cancel",
            "last_name": "Rider",
            "role": "rider",
        },
    )
    _verify_user(rider_email)
    token = _login(client, rider_email, password)
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        "/api/v1/rides/",
        json={
            "pickup": {"latitude": 37.7749, "longitude": -122.4194},
            "dropoff": {"latitude": 37.7849, "longitude": -122.4094},
            "destination_type": "mass",
            "requested_datetime": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        },
        headers=headers,
    )
    assert create_resp.status_code == status.HTTP_201_CREATED
    ride_request_id = create_resp.json()["id"]

    cancel_resp = client.post(
        f"/api/v1/rides/{ride_request_id}/cancel",
        json={"reason": "Change of plans"},
        headers=headers,
    )
    assert cancel_resp.status_code == status.HTTP_200_OK, cancel_resp.text
    assert cancel_resp.json()["status"] == "cancelled"


def test_invalid_status_transition_rejected(client):
    """Attempting an illegal status transition returns HTTP 400."""
    rider_email = "bad_trans_rider@example.com"
    driver_email = "bad_trans_driver@example.com"
    password = "StrongPass123!"

    for payload in [
        {
            "email": rider_email,
            "phone": "+15550000020",
            "password": password,
            "first_name": "Bad",
            "last_name": "Rider",
            "role": "rider",
        },
        {
            "email": driver_email,
            "phone": "+15550000021",
            "password": password,
            "first_name": "Bad",
            "last_name": "Driver",
            "role": "driver",
        },
    ]:
        client.post("/api/v1/auth/register", json=payload)

    _verify_user(rider_email)
    _verify_user(driver_email)
    _approve_driver(driver_email)

    rider_token = _login(client, rider_email, password)
    driver_token = _login(client, driver_email, password)

    create_resp = client.post(
        "/api/v1/rides/",
        json={
            "pickup": {"latitude": 37.7749, "longitude": -122.4194},
            "dropoff": {"latitude": 37.7849, "longitude": -122.4094},
            "destination_type": "confession",
            "requested_datetime": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        },
        headers={"Authorization": f"Bearer {rider_token}"},
    )
    assert create_resp.status_code == status.HTTP_201_CREATED
    ride_request_id = create_resp.json()["id"]

    accept_resp = client.post(
        f"/api/v1/rides/{ride_request_id}/accept",
        headers={"Authorization": f"Bearer {driver_token}"},
    )
    assert accept_resp.status_code == status.HTTP_201_CREATED
    ride_id = accept_resp.json()["id"]

    # Attempt to jump directly from "accepted" to "completed" — not allowed.
    bad_resp = client.patch(
        f"/api/v1/rides/{ride_id}/status",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {driver_token}"},
    )
    assert bad_resp.status_code == status.HTTP_400_BAD_REQUEST

