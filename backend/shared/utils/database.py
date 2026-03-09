"""
Shared Database Utilities
Database connection helpers for cross-service communication
"""
import os
from typing import Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool


# Django database settings
DJANGO_DB_HOST = os.environ.get("DJANGO_DB_HOST", "localhost")
DJANGO_DB_PORT = os.environ.get("DJANGO_DB_PORT", "5432")
DJANGO_DB_NAME = os.environ.get("DJANGO_DB_NAME", "RealEstate")
DJANGO_DB_USER = os.environ.get("DJANGO_DB_USER", "postgres")
DJANGO_DB_PASSWORD = os.environ.get("DJANGO_DB_PASSWORD", "12345")

# Build Django database URL
DJANGO_DATABASE_URL = f"postgresql://{DJANGO_DB_USER}:{DJANGO_DB_PASSWORD}@{DJANGO_DB_HOST}:{DJANGO_DB_PORT}/{DJANGO_DB_NAME}"


class DatabaseManager:
    """Database connection manager for external services"""

    _engine = None
    _session_factory = None

    @classmethod
    def get_engine(cls):
        """Get or create SQLAlchemy engine"""
        if cls._engine is None:
            cls._engine = create_engine(
                DJANGO_DATABASE_URL,
                poolclass=NullPool,  # Use NullPool for async/FastAPI services
                echo=os.environ.get("SQL_ECHO", "false").lower() == "true"
            )
        return cls._engine

    @classmethod
    def get_session_factory(cls):
        """Get or create session factory"""
        if cls._session_factory is None:
            cls._session_factory = sessionmaker(
                bind=cls.get_engine(),
                expire_on_commit=False
            )
        return cls._session_factory

    @classmethod
    @contextmanager
    def get_session(cls) -> Session:
        """Context manager for database sessions"""
        session_factory = cls.get_session_factory()
        session = session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @classmethod
    def get_metadata(cls) -> MetaData:
        """Get database metadata"""
        return MetaData(bind=cls.get_engine())


def get_db_session() -> Session:
    """Dependency for FastAPI to get database session"""
    with DatabaseManager.get_session() as session:
        yield session
