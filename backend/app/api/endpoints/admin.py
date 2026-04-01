"""Admin endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_admin_user
from app.db.session import get_db
from app.models.driver_profile import DriverProfile
from app.models.user import User
from app.schemas.driver_profile import DriverProfileResponse, DriverTrainingUpdate

router = APIRouter()


@router.get("/drivers", response_model=List[DriverProfileResponse])
def get_all_drivers(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100,
):
    """Get all driver profiles for admin view."""
    drivers = db.query(DriverProfile).offset(skip).limit(limit).all()
    return drivers


@router.put("/drivers/{user_id}/verify", response_model=DriverProfileResponse)
def verify_driver(
    user_id: int,
    training_data: DriverTrainingUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """Update a driver's background check and safe environment training status."""
    driver = db.query(DriverProfile).filter(DriverProfile.user_id == user_id).first()
    if not driver:
        # For MVP, assume they must have a driver profile already
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found for this user",
        )

    # Update fields that were provided
    update_data = training_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(driver, field, value)
        
    db.commit()
    db.refresh(driver)
    return driver
