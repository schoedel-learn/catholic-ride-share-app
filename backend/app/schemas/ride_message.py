"""Pydantic schemas for ride messages."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RideMessageCreate(BaseModel):
    """Payload to send a new message within a ride."""

    content: str = Field(..., min_length=1, max_length=1000)


class RideMessageResponse(BaseModel):
    """Single ride message returned by the API."""

    id: int
    ride_id: int
    sender_id: int | None
    content: str
    sent_at: datetime

    model_config = ConfigDict(from_attributes=True)
