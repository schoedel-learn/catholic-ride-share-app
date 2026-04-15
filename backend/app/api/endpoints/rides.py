"""Ride endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from geoalchemy2 import WKTElement
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps.auth import get_current_verified_user
from app.db.session import get_db
from app.models.ride import Ride, RideStatus
from app.models.ride_request import RideRequest, RideRequestStatus
from app.models.user import User, UserRole
from app.models.driver_profile import DriverProfile
from app.services.websocket import manager, WebSocketAction
from app.schemas.donation import DonationIntentResponse
from app.schemas.ride import (
    RideAcceptResponse,
    RideCancelRequest,
    RideRequestCreate,
    RideRequestResponse,
    RideStatusUpdate,
)
from app.services.payment import PaymentService, StripeNotConfiguredError

router = APIRouter()

# Valid status transitions for a Ride.  Keys are the current status; values are
# the set of statuses the driver is permitted to transition to.
_VALID_TRANSITIONS: dict[RideStatus, set[RideStatus]] = {
    RideStatus.ACCEPTED: {RideStatus.DRIVER_ENROUTE, RideStatus.CANCELLED},
    RideStatus.DRIVER_ENROUTE: {RideStatus.ARRIVED, RideStatus.CANCELLED},
    RideStatus.ARRIVED: {RideStatus.PICKED_UP, RideStatus.CANCELLED},
    RideStatus.PICKED_UP: {RideStatus.IN_PROGRESS, RideStatus.CANCELLED},
    RideStatus.IN_PROGRESS: {RideStatus.COMPLETED},
    RideStatus.COMPLETED: set(),
    RideStatus.CANCELLED: set(),
}


def _to_point(longitude: float, latitude: float) -> WKTElement:
    """Convert lat/long to PostGIS-compatible POINT."""
    return WKTElement(f"POINT({longitude} {latitude})", srid=4326)

async def _notify_users(user_ids: list[int], message: dict):
    """Notify users via WebSocket."""
    await manager.broadcast_to_users(message, user_ids)


def _ensure_driver(current_user: User) -> None:
    if current_user.role not in {UserRole.DRIVER, UserRole.BOTH, UserRole.ADMIN}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver access required to view or accept rides",
        )


def _ensure_verified_driver(current_user: User, db: Session) -> None:
    """Ensure user is a driver AND has been approved by admin."""
    _ensure_driver(current_user)
    profile = db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
    if not profile or profile.background_check_status != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your driver account has not been verified by an administrator yet.",
        )


@router.get("/mine", response_model=list[RideRequestResponse])
def list_my_ride_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    """List ride requests created by the current user."""
    rows = (
        db.query(RideRequest, Ride.id.label("ride_id"))
        .outerjoin(Ride, Ride.ride_request_id == RideRequest.id)
        .filter(RideRequest.rider_id == current_user.id)
        .order_by(RideRequest.created_at.desc())
        .all()
    )
    results: list[RideRequest] = []
    for ride_request, ride_id in rows:
        setattr(ride_request, "ride_id", ride_id)
        results.append(ride_request)
    return results


@router.get("/open", response_model=list[RideRequestResponse])
def list_open_requests_for_drivers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    """List pending ride requests available for drivers to accept."""
    _ensure_verified_driver(current_user, db)

    return (
        db.query(RideRequest)
        .filter(
            RideRequest.status == RideRequestStatus.PENDING,
            RideRequest.rider_id != current_user.id,
        )
        .order_by(RideRequest.created_at.desc())
        .all()
    )


@router.post("/", response_model=RideRequestResponse, status_code=status.HTTP_201_CREATED)
def create_ride_request(
    payload: RideRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    """Create a new ride request."""
    ride_request = RideRequest(
        rider_id=current_user.id,
        destination_type=payload.destination_type,
        parish_id=payload.parish_id,
        pickup_location=_to_point(
            longitude=payload.pickup.longitude, latitude=payload.pickup.latitude
        ),
        destination_location=_to_point(
            longitude=payload.dropoff.longitude, latitude=payload.dropoff.latitude
        ),
        requested_datetime=payload.requested_datetime,
        notes=payload.notes,
        passenger_count=payload.passenger_count,
        status=RideRequestStatus.PENDING,
    )

    db.add(ride_request)
    db.commit()
    db.refresh(ride_request)

    # Find available drivers near pickup location using PostGIS ST_Distance and
    # notify them via WebSocket.  The query is silently skipped on databases
    # that do not support PostGIS (e.g. SQLite used in tests).
    try:
        available_drivers = (
            db.query(User.id)
            .join(DriverProfile, DriverProfile.user_id == User.id)
            .filter(
                User.role.in_([UserRole.DRIVER, UserRole.BOTH]),
                DriverProfile.is_available == True,
                DriverProfile.background_check_status == "approved",
                User.last_known_location.is_not(None)
            )
            .order_by(
                func.ST_Distance(
                    User.last_known_location,
                    _to_point(longitude=payload.pickup.longitude, latitude=payload.pickup.latitude)
                )
            )
            .limit(10)
            .all()
        )
    except Exception:
        available_drivers = []

    driver_ids = [row[0] for row in available_drivers]
    if driver_ids:
        msg = {
            "action": WebSocketAction.NEW_REQUEST,
            "data": {
                "ride_request_id": ride_request.id,
                "pickup": {"lat": payload.pickup.latitude, "lng": payload.pickup.longitude},
                "destination_type": payload.destination_type,
                "passenger_count": payload.passenger_count,
            }
        }
        background_tasks.add_task(_notify_users, driver_ids, msg)

    return ride_request


@router.post(
    "/{ride_request_id}/accept",
    response_model=RideAcceptResponse,
    status_code=status.HTTP_201_CREATED,
)
def accept_ride_request(
    ride_request_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    """Allow a driver to accept a pending ride request."""
    _ensure_verified_driver(current_user, db)

    ride_request = db.query(RideRequest).filter(RideRequest.id == ride_request_id).first()
    if not ride_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ride request not found")

    if ride_request.rider_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot accept your own ride request",
        )

    if ride_request.status != RideRequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ride request is no longer available",
        )

    existing_ride = db.query(Ride).filter(Ride.ride_request_id == ride_request.id).first()
    if existing_ride:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ride request already accepted",
        )

    ride = Ride(
        ride_request_id=ride_request.id,
        driver_id=current_user.id,
        rider_id=ride_request.rider_id,
        status=RideStatus.ACCEPTED,
        accepted_at=datetime.utcnow(),
    )

    ride_request.status = RideRequestStatus.ACCEPTED

    db.add(ride)
    db.commit()
    db.refresh(ride)

    # Notify rider that their ride was accepted
    msg = {
        "action": WebSocketAction.RIDE_ACCEPTED,
        "data": {
            "ride_id": ride.id,
            "driver_name": current_user.full_name,
        }
    }
    background_tasks.add_task(_notify_users, [ride_request.rider_id], msg)

    return ride


@router.post("/{ride_request_id}/cancel", response_model=RideRequestResponse)
def cancel_ride_request(
    ride_request_id: int,
    payload: Optional[RideCancelRequest] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    """Allow a rider to cancel a pending or accepted ride request.

    If the request has already been accepted, the associated Ride record is also
    cancelled and the driver is notified via WebSocket.
    """
    ride_request = db.query(RideRequest).filter(RideRequest.id == ride_request_id).first()
    if not ride_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ride request not found"
        )

    if ride_request.rider_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your ride request"
        )

    if ride_request.status not in {RideRequestStatus.PENDING, RideRequestStatus.ACCEPTED}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel a ride with status '{ride_request.status}'",
        )

    ride_request.status = RideRequestStatus.CANCELLED

    # Also cancel the associated Ride if it already exists.
    ride = db.query(Ride).filter(Ride.ride_request_id == ride_request.id).first()
    if ride and ride.status not in {RideStatus.COMPLETED, RideStatus.CANCELLED}:
        ride.status = RideStatus.CANCELLED
        ride.cancelled_at = datetime.utcnow()
        if payload and payload.reason:
            ride.cancel_reason = payload.reason
        msg = {
            "action": WebSocketAction.RIDE_UPDATED,
            "data": {"ride_id": ride.id, "status": ride.status},
        }
        background_tasks.add_task(_notify_users, [ride.driver_id], msg)

    db.commit()
    db.refresh(ride_request)
    return ride_request


@router.get("/assigned", response_model=list[RideAcceptResponse])
def list_assigned_rides(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    """List rides assigned to the current driver."""
    _ensure_driver(current_user)
    return (
        db.query(Ride)
        .filter(Ride.driver_id == current_user.id)
        .order_by(Ride.accepted_at.desc())
        .all()
    )


@router.patch(
    "/{ride_id}/status",
    response_model=RideAcceptResponse,
)
def update_ride_status(
    ride_id: int,
    payload: RideStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
):
    """Update the status of an accepted ride (driver only).

    Only valid state transitions are accepted; see ``_VALID_TRANSITIONS``.
    """
    _ensure_driver(current_user)

    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ride not found")

    if ride.driver_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your ride")

    current_status = RideStatus(ride.status)
    new_status = payload.status
    allowed = _VALID_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot transition ride from '{current_status}' to '{new_status}'. "
                f"Allowed transitions: {sorted(s.value for s in allowed) or 'none'}"
            ),
        )

    ride.status = new_status

    ride_request = db.query(RideRequest).filter(RideRequest.id == ride.ride_request_id).first()
    if ride_request:
        if new_status in {RideStatus.DRIVER_ENROUTE, RideStatus.ARRIVED, RideStatus.PICKED_UP}:
            ride_request.status = RideRequestStatus.ACCEPTED
        elif new_status == RideStatus.IN_PROGRESS:
            ride_request.status = RideRequestStatus.IN_PROGRESS
        elif new_status == RideStatus.COMPLETED:
            ride_request.status = RideRequestStatus.COMPLETED
        elif new_status == RideStatus.CANCELLED:
            ride_request.status = RideRequestStatus.CANCELLED

    if new_status == RideStatus.COMPLETED:
        ride.completed_at = datetime.utcnow()
        # Increment driver's total ride counter.
        driver_profile = (
            db.query(DriverProfile).filter(DriverProfile.user_id == current_user.id).first()
        )
        if driver_profile:
            driver_profile.total_rides = (driver_profile.total_rides or 0) + 1
    elif new_status == RideStatus.CANCELLED:
        ride.cancelled_at = datetime.utcnow()

    db.commit()
    db.refresh(ride)

    # Notify rider of status update
    msg = {
        "action": WebSocketAction.RIDE_UPDATED,
        "data": {
            "ride_id": ride.id,
            "status": ride.status,
        }
    }
    background_tasks.add_task(_notify_users, [ride.rider_id], msg)

    auto_donation_intent: DonationIntentResponse | None = None

    if new_status == RideStatus.COMPLETED:
        rider = db.query(User).filter(User.id == ride.rider_id).first()
        if rider and rider.auto_donation_enabled:
            amount_cents: int | None = None
            if rider.auto_donation_type == "fixed":
                amount_cents = rider.auto_donation_amount_cents or None
            else:
                try:
                    payment = PaymentService()
                    distance_miles = payment.get_ride_distance_miles(db, ride_id=ride.id) or 0.0
                    multiplier = rider.auto_donation_multiplier or 0.5  # USD per mile
                    amount = 5.0 + (distance_miles * multiplier)
                    amount_cents = max(100, min(100_000, int(round(amount * 100))))
                    intent = payment.create_donation_payment_intent(
                        db,
                        amount_cents=amount_cents,
                        donor=rider,
                        ride_id=ride.id,
                        driver_id=ride.driver_id,
                    )
                    auto_donation_intent = DonationIntentResponse(
                        payment_intent_id=intent.payment_intent_id,
                        client_secret=intent.client_secret,
                        amount=intent.amount_cents / 100.0,
                        currency="USD",
                    )
                except StripeNotConfiguredError:
                    auto_donation_intent = None
                except Exception:
                    # Don't block ride completion if donations fail.
                    auto_donation_intent = None

            if amount_cents and rider.auto_donation_type == "fixed":
                try:
                    payment = PaymentService()
                    intent = payment.create_donation_payment_intent(
                        db,
                        amount_cents=amount_cents,
                        donor=rider,
                        ride_id=ride.id,
                        driver_id=ride.driver_id,
                    )
                    auto_donation_intent = DonationIntentResponse(
                        payment_intent_id=intent.payment_intent_id,
                        client_secret=intent.client_secret,
                        amount=intent.amount_cents / 100.0,
                        currency="USD",
                    )
                except StripeNotConfiguredError:
                    auto_donation_intent = None
                except Exception:
                    auto_donation_intent = None

    return RideAcceptResponse.model_validate(
        {
            "id": ride.id,
            "ride_request_id": ride.ride_request_id,
            "driver_id": ride.driver_id,
            "rider_id": ride.rider_id,
            "status": ride.status,
            "accepted_at": ride.accepted_at,
            "pickup": ride.pickup,
            "dropoff": ride.dropoff,
            "auto_donation_intent": auto_donation_intent,
        }
    )

