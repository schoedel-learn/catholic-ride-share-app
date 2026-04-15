from datetime import datetime, timedelta

from fastapi import status

from app.db.session import SessionLocal
from app.models.user import User


def _verify_user(email: str) -> None:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    user.is_verified = True
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

    # Create an approved driver profile so _ensure_verified_driver passes.
    from app.models.driver_profile import DriverProfile as DP

    db = SessionLocal()
    driver_user = db.query(User).filter(User.email == driver_email).first()
    assert driver_user is not None
    profile = DP(user_id=driver_user.id, background_check_status="approved")
    db.add(profile)
    db.commit()
    db.close()

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
        json={"status": "in_progress"},
        headers=driver_headers,
    )
    assert in_progress.status_code == status.HTTP_200_OK
    assert in_progress.json()["status"] == "in_progress"

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
