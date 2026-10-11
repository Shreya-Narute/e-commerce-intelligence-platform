import os
import sys
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ── Point to SQLite BEFORE any app module is imported ─────────────────────
os.environ.setdefault(
    "DATABASE_URL", "sqlite:///./test_ecommerce.db"
)

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.auth_service import AuthService

# In-memory SQLite for complete test isolation
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ---------------------------------------------------------------------------
# SQLite compatibility shim: PostgreSQL's to_char(timestamp, text) is used by
# several analytics services (e.g. sales_service.get_monthly_revenue with the
# 'YYYY-MM' format). The in-memory SQLite test DB has no native to_char, so we
# register a small Python equivalent on each connection. This is a TEST-ONLY
# helper; it does not touch production code or the real database.
# ---------------------------------------------------------------------------
def _sqlite_to_char(value, fmt):
    """Minimal PostgreSQL to_char for the format codes used in this codebase."""
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        s = str(value)
        dt = None
        for parse_fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(s, parse_fmt)
                break
            except ValueError:
                continue
        if dt is None:
            try:
                dt = datetime.fromisoformat(s)
            except ValueError:
                return None
    out = fmt
    # Replace longer tokens first to avoid partial collisions.
    out = out.replace("HH24", dt.strftime("%H"))
    out = out.replace("YYYY", dt.strftime("%Y"))
    out = out.replace("MM", dt.strftime("%m"))
    out = out.replace("DD", dt.strftime("%d"))
    out = out.replace("MI", dt.strftime("%M"))
    out = out.replace("SS", dt.strftime("%S"))
    return out


@event.listens_for(test_engine, "connect")
def _register_to_char(dbapi_conn, connection_record):
    dbapi_conn.create_function("to_char", 2, _sqlite_to_char)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    with TestingSessionLocal() as db:
        AuthService.seed_initial_admin(db)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()
