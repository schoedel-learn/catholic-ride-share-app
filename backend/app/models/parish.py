"""Parish model."""

from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Parish(Base):
    """Parish model."""

    __tablename__ = "parishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    diocese_id = Column(Integer, ForeignKey("dioceses.id"), nullable=True)

    # Relationships
    diocese = relationship("Diocese", back_populates="parishes")

    # Address
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)

    # Location (using PostGIS)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)

    # Contact
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    website = Column(String, nullable=True)

    # Mass times stored as JSON
    # Example: [{"day": "Sunday", "time": "08:00", "language": "English"}, ...]
    # This will be handled in the schema layer

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
