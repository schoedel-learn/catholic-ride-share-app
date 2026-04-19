"""Celery tasks for ride-lifecycle and driver-verification notifications.

These tasks are invoked as background jobs from API endpoints so that
notification delivery does not block the HTTP response.

Current implementation logs the event and is a no-op stub for the actual
delivery mechanism.  Extend each task body once FCM / APNS tokens and
SMTP are wired up.
"""

from __future__ import annotations

import logging

from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="notifications.ride_requested")
def notify_ride_requested(rider_id: int, ride_request_id: int) -> None:
    """Notify nearby available drivers that a new ride request was created.

    Args:
        rider_id: ID of the rider who created the request.
        ride_request_id: ID of the new RideRequest.
    """
    logger.info(
        "notify_ride_requested rider_id=%s ride_request_id=%s",
        rider_id,
        ride_request_id,
    )
    # TODO: look up driver FCM tokens, send push notification.


@celery_app.task(name="notifications.ride_accepted")
def notify_ride_accepted(rider_id: int, ride_id: int, driver_name: str) -> None:
    """Notify the rider that a driver accepted their request.

    Args:
        rider_id: ID of the rider.
        ride_id: ID of the newly created Ride.
        driver_name: Display name of the accepting driver.
    """
    logger.info(
        "notify_ride_accepted rider_id=%s ride_id=%s driver=%s",
        rider_id,
        ride_id,
        driver_name,
    )
    # TODO: send push / email to rider.


@celery_app.task(name="notifications.ride_status_changed")
def notify_ride_status_changed(user_id: int, ride_id: int, new_status: str) -> None:
    """Notify a ride participant of a status change.

    Args:
        user_id: Recipient user ID (rider or driver).
        ride_id: ID of the affected Ride.
        new_status: The new RideStatus string value.
    """
    logger.info(
        "notify_ride_status_changed user_id=%s ride_id=%s status=%s",
        user_id,
        ride_id,
        new_status,
    )
    # TODO: send push / email based on status.


@celery_app.task(name="notifications.ride_cancelled")
def notify_ride_cancelled(user_id: int, ride_id: int, reason: str | None) -> None:
    """Notify a ride participant that the ride was cancelled.

    Args:
        user_id: Recipient user ID.
        ride_id: ID of the cancelled Ride.
        reason: Optional human-readable reason.
    """
    logger.info(
        "notify_ride_cancelled user_id=%s ride_id=%s reason=%s",
        user_id,
        ride_id,
        reason,
    )
    # TODO: send push / email.


@celery_app.task(name="notifications.driver_verification_updated")
def notify_driver_verification_updated(
    driver_user_id: int,
    new_status: str,
    reason: str | None = None,
) -> None:
    """Notify a driver that their verification status was changed by an admin.

    Args:
        driver_user_id: ID of the driver's User record.
        new_status: One of ``'approved'`` or ``'rejected'``.
        reason: Optional rejection reason.
    """
    logger.info(
        "notify_driver_verification_updated user_id=%s status=%s",
        driver_user_id,
        new_status,
    )
    # TODO: send push / email.
