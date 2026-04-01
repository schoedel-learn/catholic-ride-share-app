from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DioceseBase(BaseModel):
    name: str
    state: str


class DioceseCreate(DioceseBase):
    pass


class DioceseResponse(DioceseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
