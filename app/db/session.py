from typing import Generator
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

# Sanitize DATABASE_URL (strip any accidental surrounding quotes or whitespace from dashboard inputs)
raw_db_url = settings.DATABASE_URL.strip().strip("\"'").strip()
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
if raw_db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

try:
    engine = create_engine(
        raw_db_url,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.DEBUG
    )
except Exception as e:
    logger.error(f"Error creating primary database engine with URL {raw_db_url[:20]}...: {e}")
    # Fallback to local SQLite if remote PostgreSQL URL is completely malformed
    engine = create_engine("sqlite:///./vajranet_fallback.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
