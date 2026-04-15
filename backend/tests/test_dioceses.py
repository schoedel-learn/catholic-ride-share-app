"""Diocese endpoint tests."""

from fastapi import status

from app.db.session import SessionLocal
from app.models.diocese import Diocese


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_diocese(name: str, state: str = "IL") -> Diocese:
    db = SessionLocal()
    diocese = Diocese(name=name, state=state)
    db.add(diocese)
    db.commit()
    db.refresh(diocese)
    db.close()
    return diocese


# ---------------------------------------------------------------------------
# GET /dioceses/
# ---------------------------------------------------------------------------


def test_list_dioceses_empty(client):
    resp = client.get("/api/v1/dioceses/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == []


def test_list_dioceses_with_data(client):
    _create_diocese("Diocese of Springfield", state="IL")
    _create_diocese("Archdiocese of Chicago", state="IL")

    resp = client.get("/api/v1/dioceses/")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) == 2
    names = {d["name"] for d in data}
    assert "Diocese of Springfield" in names
    assert "Archdiocese of Chicago" in names


def test_list_dioceses_ordered_alphabetically(client):
    _create_diocese("Zeta Diocese", state="TX")
    _create_diocese("Alpha Diocese", state="TX")
    _create_diocese("Mu Diocese", state="TX")

    resp = client.get("/api/v1/dioceses/")
    assert resp.status_code == status.HTTP_200_OK
    names = [d["name"] for d in resp.json()]
    assert names == sorted(names)
