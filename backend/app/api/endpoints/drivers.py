"""Driver endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_active_user, get_current_verified_user
from app.db.session import get_db
from app.models.driver_profile import DriverProfile
from app.models.user import User
from app.schemas.driver_profile import DriverAvailabilityUpdate, DriverProfileResponse

router = APIRouter()


@router.get("/available")
def get_available_drivers(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Get available drivers nearby."""
    # TODO: Implement driver discovery
    return {"message": "Available drivers endpoint - to be implemented"}


@router.get("/me", response_model=DriverProfileResponse)
def get_my_driver_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    """Get the current driver's profile."""
    if current_user.role not in ["driver", "both", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized as a driver")

    driver = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found. Toggle availability to create one.",
        )
    return driver


@router.put("/me/availability", response_model=DriverProfileResponse)
def update_driver_availability(
    data: DriverAvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    """Update current driver's availability status."""
    if current_user.role not in ["driver", "both", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized as a driver")

    driver = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
    if not driver:
        # Create profile implicitly for MVP if missing
        driver = DriverProfile(user_id=current_user.id, is_available=data.is_available)
        db.add(driver)
        db.commit()
        db.refresh(driver)
        return driver

    driver.is_available = data.is_available
    db.commit()
    db.refresh(driver)
    return driver


@router.post("/profile")
def create_driver_profile(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Create driver profile."""
    # TODO: Implement driver profile creation
    return {"message": "Create driver profile endpoint - to be implemented"}
