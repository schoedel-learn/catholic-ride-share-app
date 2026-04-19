"""Ride message model.

Stores per-ride chat messages exchanged between a rider and their assigned
driver.  Only the two participants (and admins) are permitted to read or
send messages for a given ride.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class RideMessage(Base):
    """A single chat message attached to an in-progress ride."""

    __tablename__ = "ride_messages"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(
        Integer, ForeignKey("rides.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Soft-delete / moderation flag.
    is_deleted = Column(String(1), default="N", nullable=False)

    ride = relationship("Ride", back_populates="messages")
    sender = relationship("User")
