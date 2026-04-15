"""Driver endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from geoalchemy2 import WKTElement
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_active_user, get_current_verified_user
from app.db.session import get_db
from app.models.driver_profile import DriverProfile
from app.models.user import User, UserRole
from app.schemas.driver_profile import (
    AvailableDriverResponse,
    DriverAvailabilityUpdate,
    DriverProfileCreate,
    DriverProfileResponse,
    DriverProfileUpdate,
)

router = APIRouter()

_DRIVER_ROLES = {UserRole.DRIVER, UserRole.BOTH, UserRole.ADMIN}


def _require_driver_role(user: User) -> None:
    """Raise 403 if the user is not registered as a driver."""
    if user.role not in _DRIVER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized as a driver",
        )


def _to_point(longitude: float, latitude: float) -> WKTElement:
    """Convert lat/long to PostGIS-compatible POINT."""
    return WKTElement(f"POINT({longitude} {latitude})", srid=4326)


# ---------------------------------------------------------------------------
# Driver profile management
# ---------------------------------------------------------------------------


@router.post("/profile", response_model=DriverProfileResponse, status_code=status.HTTP_200_OK)
def upsert_driver_profile(
    data: DriverProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    """Create or update the current driver's profile (vehicle details).

    Idempotent: creates the profile on first call, updates it on subsequent calls.
    Requires the user to have a driver-capable role.
    """
    _require_driver_role(current_user)

    driver = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
    if not driver:
        driver = DriverProfile(user_id=current_user.id)
        db.add(driver)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)

    db.commit()
    db.refresh(driver)
    return driver


@router.put("/me", response_model=DriverProfileResponse)
def update_driver_profile(
    data: DriverProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    """Update vehicle details on an existing driver profile."""
    _require_driver_role(current_user)

    driver = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found. Use POST /drivers/profile to create one.",
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)

    db.commit()
    db.refresh(driver)
    return driver


@router.get("/me", response_model=DriverProfileResponse)
def get_my_driver_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    """Get the current driver's full profile (private)."""
    _require_driver_role(current_user)

    driver = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found. Use POST /drivers/profile to create one.",
        )
    return driver


@router.put("/me/availability", response_model=DriverProfileResponse)
def update_driver_availability(
    data: DriverAvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    """Toggle current driver's availability.

    Creates a blank profile on first use so drivers can signal availability
    before completing the full vehicle form.
    """
    _require_driver_role(current_user)

    driver = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
    if not driver:
        driver = DriverProfile(user_id=current_user.id, is_available=data.is_available)
        db.add(driver)
        db.commit()
        db.refresh(driver)
        return driver

    driver.is_available = data.is_available
    db.commit()
    db.refresh(driver)
    return driver


# ---------------------------------------------------------------------------
# Driver discovery
# ---------------------------------------------------------------------------


@router.get("/available", response_model=list[AvailableDriverResponse])
def get_available_drivers(
    latitude: Optional[float] = Query(default=None, ge=-90, le=90),
    longitude: Optional[float] = Query(default=None, ge=-180, le=180),
    radius_miles: float = Query(default=50.0, ge=1.0, le=500.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List currently available, admin-approved drivers.

    Optional query parameters:
    - **latitude** / **longitude**: when both provided, only drivers within
      ``radius_miles`` are returned and results are ordered nearest-first.
    - **radius_miles**: search radius (default 50 miles).  Ignored when
      lat/lon are not supplied.
    """
    query = (
        db.query(DriverProfile)
        .join(User, User.id == DriverProfile.user_id)
        .filter(
            DriverProfile.is_available.is_(True),
            DriverProfile.background_check_status == "approved",
            User.role.in_([UserRole.DRIVER, UserRole.BOTH, UserRole.ADMIN]),
        )
    )

    if latitude is not None and longitude is not None:
        try:
            point = _to_point(longitude=longitude, latitude=latitude)
            radius_meters = radius_miles * 1609.34
            query = query.filter(
                User.last_known_location.is_not(None),
                func.ST_DWithin(User.last_known_location, point, radius_meters),
            ).order_by(func.ST_Distance(User.last_known_location, point))
        except Exception:
            # PostGIS unavailable (e.g. SQLite in tests): fall back to unordered list.
            pass

    return query.limit(50).all()

