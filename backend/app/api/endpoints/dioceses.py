"""Diocese endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.diocese import Diocese
from app.schemas.diocese import DioceseResponse

router = APIRouter()


@router.get("/", response_model=list[DioceseResponse])
def list_dioceses(db: Session = Depends(get_db)):
    """List all dioceses."""
    return db.query(Diocese).order_by(Diocese.name.asc()).all()
