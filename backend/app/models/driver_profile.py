"""Driver profile model."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class DriverProfile(Base):
    """Driver profile model."""

    __tablename__ = "driver_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Vehicle information
    vehicle_make = Column(String, nullable=True)
    vehicle_model = Column(String, nullable=True)
    vehicle_year = Column(Integer, nullable=True)
    vehicle_color = Column(String, nullable=True)
    license_plate = Column(String, nullable=True)
    vehicle_capacity = Column(Integer, default=4, nullable=False)

    # Verification
    insurance_verified = Column(Boolean, default=False, nullable=False)
    background_check_status = Column(String, default="pending", nullable=False)
    
    # Safe Environment / Admin Vetting
    training_completed_date = Column(DateTime, nullable=True)
    training_expiration_date = Column(DateTime, nullable=True)
    admin_notes = Column(String, nullable=True)

    # Status
    is_available = Column(Boolean, default=False, nullable=False)

    # Stats
    total_rides = Column(Integer, default=0, nullable=False)
    average_rating = Column(Float, default=0.0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="driver_profile")
