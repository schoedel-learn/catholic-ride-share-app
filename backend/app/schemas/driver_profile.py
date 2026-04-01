"""Driver profile schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DriverProfileBase(BaseModel):
    """Base driver profile schema."""

    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[int] = None
    vehicle_color: Optional[str] = None
    license_plate: Optional[str] = None
    vehicle_capacity: int = 4


class DriverProfileCreate(DriverProfileBase):
    """Driver profile creation schema."""

    pass


class DriverProfileUpdate(DriverProfileBase):
    """Driver profile update schema."""

    pass


class DriverAvailabilityUpdate(BaseModel):
    """Driver availability toggle schema."""
    is_available: bool

class DriverTrainingUpdate(BaseModel):
    """Driver training status update schema for admins."""

    background_check_status: Optional[str] = None
    training_completed_date: Optional[datetime] = None
    training_expiration_date: Optional[datetime] = None
    admin_notes: Optional[str] = None


class DriverProfileResponse(DriverProfileBase):
    """Driver profile response schema."""

    id: int
    user_id: int
    insurance_verified: bool
    background_check_status: str
    training_completed_date: Optional[datetime] = None
    training_expiration_date: Optional[datetime] = None
    admin_notes: Optional[str] = None
    is_available: bool
    total_rides: int
    average_rating: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
