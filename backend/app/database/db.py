"""Database configuration and session management.

Provides SQLAlchemy engine, session factory, and base class
for declarative models with support for multiple database backends.
"""

from functools import lru_cache
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings


# Resolve database path
BASE_DIR = Path(__file__).resolve().parents[2]


@lru_cache
def get_database_url() -> str:
    """Get database URL from settings or use default SQLite."""
    settings = get_settings()
    if settings.database_url:
        return settings.database_url
    return f"sqlite:///{BASE_DIR / 'predictions.db'}"


# Create engine based on database URL
_database_url = get_database_url()

connect_args = {}
if _database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    _database_url,
    connect_args=connect_args,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,  # Enable connection health checks
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()


def get_db() -> Generator:
    """Dependency that provides a database session.

    Yields:
        SQLAlchemy session instance.

    Usage:
        def my_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables.

    Should be called on application startup.
    """
    # Import all models to register them with Base
    from app.models import library_item, prediction, question, section  # noqa: F401

    Base.metadata.create_all(bind=engine)