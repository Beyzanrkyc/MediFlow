"""
Database engine/session setup (PostgreSQL via SQLAlchemy).

Reads DATABASE_URL from the environment, e.g.:
    DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mediflow
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/mediflow",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables that don't exist yet. Safe to call on every startup."""
    # Import models here (not at module top) so they register on Base.metadata
    # before create_all runs, without creating circular imports.
    from app.models import patient, appointment, hospital, triage_session  # noqa: F401

    Base.metadata.create_all(bind=engine)
