"""Coordinator-parish assignment model.

Supports parish clusters where one coordinator manages multiple parishes.
"""

from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.session import Base

# Many-to-many: a coordinator can be assigned to multiple parishes,
# and a parish can have multiple coordinators.
coordinator_parishes = Table(
    "coordinator_parishes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("parish_id", Integer, ForeignKey("parishes.id"), primary_key=True),
)
