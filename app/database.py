"""
Database configuration for the URL Shortener.

Uses SQLAlchemy with SQLite. The database file is stored at ./urls.db
relative to where the application is run from. In Docker, this will
be inside /app/urls.db.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./urls.db"

# check_same_thread=False is required for SQLite with FastAPI because
# FastAPI handles requests in multiple threads, but SQLite by default
# only allows access from the thread that created the connection.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session per request.
    Ensures the session is properly closed after the request completes,
    even if an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
