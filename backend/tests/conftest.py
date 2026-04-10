import os
from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient
from geoalchemy2 import Geography
from sqlalchemy.ext.compiler import compiles

# Provide minimal defaults so Settings can initialize during tests without external services.
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.db.session import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402

# Import models so metadata is aware for table creation.
from app.models import driver_profile, parish, ride, ride_request, user  # noqa: F401, E402

# Check if we're using SQLite (for local dev) or PostgreSQL (for CI)
_is_sqlite = "sqlite" in os.environ.get("DATABASE_URL", "sqlite")


# SQLite does not support PostGIS types; compile Geography to TEXT for tests.
@compiles(Geography, "sqlite")
def compile_geography_sqlite(element, compiler, **kwargs):
    return "TEXT"


# Disable spatial indexes for SQLite test runs to avoid missing functions.
if _is_sqlite:
    Geography.spatial_index = False


class _FakePipeline:
    def __init__(self, store: Dict[str, Any]):
        self.store = store
        self._incr_key: str | None = None
        self._count: int | None = None

    def incr(self, key: str):
        self._incr_key = key
        current = int(self.store.get(key, 0)) + 1
        self._count = current
        self.store[key] = current
        return self

    def expire(self, key: str, _seconds: int):
        # TTL not enforced in this in-memory fake.
        return self

    def execute(self) -> List[Any]:
        return [self._count or 0, True]


class FakeRedis:
    """Minimal Redis stub for rate limits and email codes."""

    def __init__(self):
        self.store: Dict[str, Any] = {}

    def pipeline(self):
        return _FakePipeline(self.store)

    def setex(self, key: str, _ttl: int, value: Any):
        self.store[key] = value

    def get(self, key: str):
        return self.store.get(key)

    def delete(self, key: str):
        self.store.pop(key, None)

    def incr(self, key: str):
        current = int(self.store.get(key, 0)) + 1
        self.store[key] = current
        return current

    def expire(self, key: str, _seconds: int):
        return True


@pytest.fixture(autouse=True)
def _db_setup():
    """Ensure a clean schema for each test session."""
    from sqlalchemy import String

    # Replace PostGIS types with simple strings for SQLite test DB only.
    if _is_sqlite:
        for table in Base.metadata.tables.values():
            for column in table.c:
                if isinstance(column.type, Geography):
                    column.type = String()
                    column.type.spatial_index = False

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    SessionLocal().close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    """Patch Redis client used in rate limiting and email flows."""
    client = FakeRedis()
    from app.core import redis as redis_module
    from app.services import rate_limit

    try:
        redis_module.get_redis_client.cache_clear()
    except AttributeError:
        # get_redis_client may not be cache-wrapped in some test configurations.
        pass

    monkeypatch.setattr(redis_module, "get_redis_client", lambda: client)
    monkeypatch.setattr(rate_limit, "get_redis_client", lambda: client)
    monkeypatch.setattr("app.services.auth_email._get_redis", lambda: client)
    return client


@pytest.fixture(autouse=True)
def patch_point_for_sqlite(monkeypatch):
    """Avoid WKTElement binding issues on SQLite by using plain strings."""
    if _is_sqlite:
        from app.api.endpoints import rides as rides_api

        monkeypatch.setattr(
            rides_api, "_to_point", lambda longitude, latitude: f"POINT({longitude} {latitude})"
        )


@pytest.fixture(autouse=True)
def mock_email(monkeypatch):
    """Avoid real SMTP by no-op send_email."""
    monkeypatch.setattr("app.services.email.send_email", lambda *args, **kwargs: None)


@pytest.fixture
def client():
    return TestClient(app)
