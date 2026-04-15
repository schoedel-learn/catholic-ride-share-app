"""User endpoint tests."""

from fastapi import status

from app.db.session import SessionLocal
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _register_and_verify(client, email: str, role: str = "rider") -> str:
    """Register a user, verify their email, and return an auth token."""
    client.post(
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

    # Manually verify the user in DB.
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
        data={"username": email, "password": "StrongPass123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == status.HTTP_200_OK
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# GET /users/me
# ---------------------------------------------------------------------------


def test_get_current_user_profile(client):
    token = _register_and_verify(client, "me@example.com")
    resp = client.get("/api/v1/users/me", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["email"] == "me@example.com"
    assert data["first_name"] == "Test"
    assert data["is_verified"] is True


def test_get_current_user_requires_auth(client):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# PUT /users/me
# ---------------------------------------------------------------------------


def test_update_user_profile(client):
    token = _register_and_verify(client, "update@example.com")
    resp = client.put(
        "/api/v1/users/me",
        json={"first_name": "Updated", "last_name": "Name"},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"


def test_update_user_profile_partial(client):
    token = _register_and_verify(client, "partial@example.com")
    resp = client.put(
        "/api/v1/users/me",
        json={"first_name": "OnlyFirst"},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["first_name"] == "OnlyFirst"
    assert resp.json()["last_name"] == "User"  # unchanged


# ---------------------------------------------------------------------------
# GET /users/{user_id}
# ---------------------------------------------------------------------------


def test_get_user_by_id(client):
    token = _register_and_verify(client, "requester@example.com")

    # Register a second user to look up.
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "target@example.com",
            "phone": None,
            "password": "StrongPass123!",
            "first_name": "Target",
            "last_name": "Person",
            "role": "rider",
        },
    )
    db = SessionLocal()
    target = db.query(User).filter(User.email == "target@example.com").first()
    assert target is not None
    target_id = target.id
    db.close()

    resp = client.get(f"/api/v1/users/{target_id}", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["email"] == "target@example.com"


def test_get_user_by_id_not_found(client):
    token = _register_and_verify(client, "finder@example.com")
    resp = client.get("/api/v1/users/99999", headers=_auth(token))
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "User not found"


# ---------------------------------------------------------------------------
# PUT /users/me/location
# ---------------------------------------------------------------------------


def test_update_user_location(client):
    token = _register_and_verify(client, "location@example.com")
    resp = client.put(
        "/api/v1/users/me/location",
        json={"latitude": 37.7749, "longitude": -122.4194},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_200_OK


def test_update_user_location_requires_auth(client):
    resp = client.put(
        "/api/v1/users/me/location",
        json={"latitude": 37.7749, "longitude": -122.4194},
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# POST /users/me/photo
# ---------------------------------------------------------------------------


def test_upload_photo_without_s3_returns_503(client, monkeypatch):
    """When AWS S3 is not configured, the endpoint should return 503."""
    from app.core import config as config_module

    monkeypatch.setattr(config_module.settings, "AWS_S3_BUCKET", "")
    token = _register_and_verify(client, "photo@example.com")

    import io

    fake_file = io.BytesIO(b"not an image")
    resp = client.post(
        "/api/v1/users/me/photo",
        files={"file": ("test.jpg", fake_file, "image/jpeg")},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_upload_photo_invalid_content_type_returns_400(client, monkeypatch):
    from app.core import config as config_module

    monkeypatch.setattr(config_module.settings, "AWS_S3_BUCKET", "test-bucket")
    token = _register_and_verify(client, "phototype@example.com")

    import io

    fake_file = io.BytesIO(b"not an image")
    resp = client.post(
        "/api/v1/users/me/photo",
        files={"file": ("test.pdf", fake_file, "application/pdf")},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid image format" in resp.json()["detail"]


def test_upload_photo_valid_image(client, monkeypatch):
    """A valid JPEG is processed and the URL is stored on the user."""
    from app.core import config as config_module

    monkeypatch.setattr(config_module.settings, "AWS_S3_BUCKET", "test-bucket")

    # Mock out the S3 upload to avoid real AWS calls.
    monkeypatch.setattr(
        "app.api.endpoints.users.upload_file_obj",
        lambda *args, **kwargs: "https://test-bucket.s3.amazonaws.com/profile-photos/test.jpg",
    )

    token = _register_and_verify(client, "photovalid@example.com")

    # Create a minimal valid JPEG using Pillow.
    import io

    from PIL import Image

    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    resp = client.post(
        "/api/v1/users/me/photo",
        files={"file": ("photo.jpg", buf, "image/jpeg")},
        headers=_auth(token),
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["profile_photo_url"] is not None


# ---------------------------------------------------------------------------
# DELETE /users/me/photo
# ---------------------------------------------------------------------------


def test_delete_photo_when_none_set(client):
    """Deleting a photo when none is set should succeed gracefully."""
    token = _register_and_verify(client, "nophoto@example.com")
    resp = client.delete("/api/v1/users/me/photo", headers=_auth(token))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["profile_photo_url"] is None


def test_delete_photo_clears_url(client, monkeypatch):
    """After deletion the photo URL must be None."""
    from app.core import config as config_module

    monkeypatch.setattr(config_module.settings, "AWS_S3_BUCKET", "test-bucket")
    monkeypatch.setattr(
        "app.api.endpoints.users.upload_file_obj",
        lambda *args, **kwargs: "https://test-bucket.s3.amazonaws.com/profile-photos/x.jpg",
    )
    monkeypatch.setattr("app.api.endpoints.users.delete_file", lambda *args, **kwargs: None)

    token = _register_and_verify(client, "deleteafter@example.com")

    import io

    from PIL import Image

    img = Image.new("RGB", (100, 100))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    client.post(
        "/api/v1/users/me/photo",
        files={"file": ("photo.jpg", buf, "image/jpeg")},
        headers=_auth(token),
    )

    del_resp = client.delete("/api/v1/users/me/photo", headers=_auth(token))
    assert del_resp.status_code == status.HTTP_200_OK
    assert del_resp.json()["profile_photo_url"] is None
