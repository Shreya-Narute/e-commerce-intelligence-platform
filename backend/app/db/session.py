import time
from typing import Generator, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings


def _normalize_db_url(url: str) -> str:
    """
    Normalize the DATABASE_URL to use psycopg2 driver explicitly.
    SQLAlchemy 2.1+ defaults to psycopg (psycopg3) for 'postgresql://',
    so we force psycopg2 to avoid the optional dependency.
    """
    if url.startswith("postgresql://") or url.startswith("postgresql+psycopg://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        url = url.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
    return url


# Engine configuration with connection pooling and pre-ping
_db_url = _normalize_db_url(settings.DATABASE_URL)
connect_args = {}
if _db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    _db_url,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> Tuple[bool, float, str]:
    """
    Executes a heartbeat query against the configured database.
    Returns: (is_connected: bool, latency_ms: float, message: str)
    """
    start_time = time.perf_counter()
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return True, latency_ms, "Database connection operational"
    except Exception as exc:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return False, latency_ms, f"Database connection failed: {str(exc)}"
