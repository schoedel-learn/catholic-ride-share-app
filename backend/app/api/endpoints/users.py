"""User endpoints."""

from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from geoalchemy2 import WKTElement
from PIL import Image, ImageOps
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_active_user
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserLocationUpdate, UserResponse, UserUpdate
from app.services.storage import delete_file, generate_profile_photo_key, upload_file_obj

router = APIRouter()

MAX_PROFILE_PHOTO_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    update_data = user_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/me/photo", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Upload or replace the current user's profile photo."""
    if not settings.AWS_S3_BUCKET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="File storage is not configured",
        )

    if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Allowed: JPEG, PNG, WebP",
        )

    # Read into memory to check size and process image
    contents = await file.read()
    if len(contents) > MAX_PROFILE_PHOTO_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large (max 5MB)",
        )

    try:
        image = Image.open(BytesIO(contents))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file",
        )

    # Normalize and resize to 500x500 thumbnail
    image = image.convert("RGB")
    image = ImageOps.fit(image, (500, 500))

    output = BytesIO()
    image.save(output, format="JPEG", quality=85)
    output.seek(0)

    key = generate_profile_photo_key(current_user.id, file.filename or "profile.jpg")
    url = upload_file_obj(
        output,
        bucket=settings.AWS_S3_BUCKET,
        key=key,
        content_type="image/jpeg",
    )

    # Optionally delete previous photo
    if current_user.profile_photo_url:
        try:
            # Expecting URLs like https://bucket.s3.region.amazonaws.com/key
            parts = current_user.profile_photo_url.split(".amazonaws.com/", 1)
            if len(parts) == 2:
                old_key = parts[1]
                delete_file(settings.AWS_S3_BUCKET, old_key)
        except Exception:
            # Best-effort cleanup; ignore failures
            pass

    current_user.profile_photo_url = url
    db.commit()
    db.refresh(current_user)

    return current_user


@router.delete("/me/photo", response_model=UserResponse)
def delete_profile_photo(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove the current user's profile photo."""
    if current_user.profile_photo_url and settings.AWS_S3_BUCKET:
        try:
            parts = current_user.profile_photo_url.split(".amazonaws.com/", 1)
            if len(parts) == 2:
                key = parts[1]
                delete_file(settings.AWS_S3_BUCKET, key)
        except Exception:
            # Ignore deletion errors
            pass

    current_user.profile_photo_url = None
    db.commit()
    db.refresh(current_user)

    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/me/location", response_model=UserResponse)
def update_user_location(
    location: UserLocationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Update the current user's last known location.

    This is typically called by the mobile or web client when the user
    explicitly shares their location (e.g., before requesting or offering a
    ride). Location is stored as a PostGIS POINT(longitude, latitude).
    """
    point_wkt = f"POINT({location.longitude} {location.latitude})"
    current_user.last_known_location = WKTElement(point_wkt, srid=4326)
    current_user.last_location_updated_at = datetime.utcnow()

    db.commit()
    db.refresh(current_user)

    return current_user
