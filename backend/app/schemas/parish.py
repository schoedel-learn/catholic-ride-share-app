"""Parish response schema."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ParishResponse(BaseModel):
    """Represents a parish for browse/detail views."""

    id: int
    name: str
    diocese_id: Optional[int] = None
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
