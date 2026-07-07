"""
SQLAlchemy ORM model for the URL table.

This defines the database schema — one table called 'urls' with columns
for the short code, original URL, click count, and creation timestamp.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base


class URL(Base):
    """Represents a shortened URL entry in the database."""

    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    original_url = Column(String, nullable=False)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
