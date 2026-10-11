from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Handle database URL normalization and engine arguments
db_url = str(settings.DATABASE_URL).strip().strip("'\"")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
    "echo": settings.DEBUG,
}

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # Supabase PostgreSQL requires SSL; ensure sslmode=require
    if "sslmode" not in db_url:
        delimiter = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{delimiter}sslmode=require"
    # Auto-recycle connections every 5 minutes to avoid stale Supabase pooler drops
    engine_kwargs["pool_recycle"] = 300
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(
    db_url,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
