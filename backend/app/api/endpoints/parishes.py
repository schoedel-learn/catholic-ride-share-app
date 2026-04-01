"""Parish endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.parish import Parish
from app.schemas.parish import ParishResponse

router = APIRouter()


@router.get("/", response_model=list[ParishResponse])
def list_parishes(
    db: Session = Depends(get_db), 
    q: Optional[str] = None,
    diocese_id: Optional[int] = None
):
    """List all parishes, optionally filtered by name and diocese_id."""
    query = db.query(Parish).order_by(Parish.name.asc())
    if q:
        query = query.filter(Parish.name.ilike(f"%{q}%"))
    if diocese_id is not None:
        query = query.filter(Parish.diocese_id == diocese_id)
    return query.all()


@router.get("/{parish_id}", response_model=ParishResponse)
def get_parish(parish_id: int, db: Session = Depends(get_db)):
    """Get parish by ID."""
    parish = db.query(Parish).filter(Parish.id == parish_id).first()
    if not parish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parish not found")
    return parish
