"""Schemas for ride requests and rides."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.ride import RideStatus
from app.models.ride_request import DestinationType, RideRequestStatus
from app.schemas.donation import DonationIntentResponse


class Location(BaseModel):
    """Latitude/longitude pair."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class RideRequestCreate(BaseModel):
    """Payload to create a ride request."""

    pickup: Location
    dropoff: Location
    destination_type: DestinationType
    requested_datetime: datetime
    parish_id: Optional[int] = None
    notes: Optional[str] = None
    passenger_count: int = Field(default=1, ge=1, le=6)


class RideRequestResponse(BaseModel):
    """Ride request response payload."""

    id: int
    ride_id: Optional[int] = None
    rider_id: int
    destination_type: DestinationType
    parish_id: Optional[int]
    requested_datetime: datetime
    notes: Optional[str]
    passenger_count: int
    status: RideRequestStatus
    created_at: datetime
    updated_at: datetime
    pickup: Location
    dropoff: Location

    class Config:
        from_attributes = True


class RideAcceptResponse(BaseModel):
    """Response returned when a driver accepts a ride request."""

    id: int
    ride_request_id: int
    driver_id: int
    rider_id: int
    status: RideStatus
    accepted_at: datetime
    pickup: Location
    dropoff: Location
    auto_donation_intent: Optional[DonationIntentResponse] = None

    class Config:
        from_attributes = True


class RideStatusUpdate(BaseModel):
    """Payload for updating an in-flight ride status."""

    status: RideStatus
