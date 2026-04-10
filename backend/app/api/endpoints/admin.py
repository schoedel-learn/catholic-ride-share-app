"""Admin endpoints.

Permission model:
  - ADMIN: Full global access — all drivers, all parishes, can approve/deny drivers.
  - COORDINATOR: Parish-scoped — sees drivers in their assigned parishes (supports
    parish clusters via coordinator_parishes table), can update training dates and
    notes, but CANNOT change background_check_status.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_admin_user
from app.db.session import get_db
from app.models.driver_profile import DriverProfile
from app.models.user import User, UserRole
from app.schemas.driver_profile import DriverProfileResponse, DriverTrainingUpdate

router = APIRouter()


def _is_global_admin(user: User) -> bool:
    return user.role == UserRole.ADMIN


def _coordinator_parish_ids(user: User) -> list[int]:
    """Get the list of parish IDs this coordinator manages (supports clusters)."""
    ids = [p.id for p in user.coordinated_parishes]
    # Fallback: include user's own parish_id if they have one
    if user.parish_id and user.parish_id not in ids:
        ids.append(user.parish_id)
    return ids


@router.get("/drivers", response_model=List[DriverProfileResponse])
def get_all_drivers(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100,
):
    """Get driver profiles visible to the current admin/coordinator.

    - Admins see all drivers.
    - Coordinators see only drivers from their assigned parishes.
    """
    query = db.query(DriverProfile)

    if not _is_global_admin(current_admin):
        parish_ids = _coordinator_parish_ids(current_admin)
        if not parish_ids:
            return []
        query = query.join(User, User.id == DriverProfile.user_id).filter(
            User.parish_id.in_(parish_ids)
        )

    drivers = query.offset(skip).limit(limit).all()
    return drivers


@router.put("/drivers/{user_id}/verify", response_model=DriverProfileResponse)
def verify_driver(
    user_id: int,
    training_data: DriverTrainingUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """Update a driver's training status or background check.

    Permission rules:
    - Admins can update ALL fields including background_check_status.
    - Coordinators can update training dates and notes for drivers in
      their assigned parishes, but CANNOT change background_check_status.
    """
    driver = db.query(DriverProfile).filter(DriverProfile.user_id == user_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found for this user",
        )

    # Coordinator parish scoping
    if not _is_global_admin(current_admin):
        driver_user = db.query(User).filter(User.id == user_id).first()
        parish_ids = _coordinator_parish_ids(current_admin)
        if not driver_user or driver_user.parish_id not in parish_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage drivers within your assigned parishes",
            )

    update_data = training_data.model_dump(exclude_unset=True)

    # Coordinators cannot change background check status — only admins
    if not _is_global_admin(current_admin) and "background_check_status" in update_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change background check status."
            " Contact your diocesan admin.",
        )

    for field, value in update_data.items():
        setattr(driver, field, value)

    db.commit()
    db.refresh(driver)
    return driver


@router.get("/parish/rides")
def get_parish_rides(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 50,
):
    """Get ride requests for the coordinator's assigned parishes.

    Admins see all ride requests; coordinators see only their parishes'.
    """
    from app.models.ride_request import RideRequest

    query = db.query(RideRequest)

    if not _is_global_admin(current_admin):
        parish_ids = _coordinator_parish_ids(current_admin)
        if not parish_ids:
            return []
        query = query.filter(RideRequest.parish_id.in_(parish_ids))

    rides = query.order_by(RideRequest.created_at.desc()).offset(skip).limit(limit).all()
    return rides


@router.get("/parish/stats")
def get_parish_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    """Quick summary stats for the coordinator's parishes (or global for admins)."""
    from app.models.ride import Ride, RideStatus
    from app.models.ride_request import RideRequest

    driver_query = db.query(DriverProfile)
    ride_query = db.query(RideRequest)

    if not _is_global_admin(current_admin):
        parish_ids = _coordinator_parish_ids(current_admin)
        if not parish_ids:
            return {
                "total_drivers": 0,
                "verified_drivers": 0,
                "pending_drivers": 0,
                "total_ride_requests": 0,
                "completed_rides": 0,
            }
        driver_query = driver_query.join(User, User.id == DriverProfile.user_id).filter(
            User.parish_id.in_(parish_ids)
        )
        ride_query = ride_query.filter(RideRequest.parish_id.in_(parish_ids))

    total_drivers = driver_query.count()
    verified_drivers = driver_query.filter(
        DriverProfile.background_check_status == "approved"
    ).count()
    pending_drivers = total_drivers - verified_drivers
    total_ride_requests = ride_query.count()
    completed_rides = db.query(Ride).filter(Ride.status == RideStatus.COMPLETED).count()

    return {
        "total_drivers": total_drivers,
        "verified_drivers": verified_drivers,
        "pending_drivers": pending_drivers,
        "total_ride_requests": total_ride_requests,
        "completed_rides": completed_rides,
    }
