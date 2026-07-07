"""
Pydantic schemas for request/response validation.

These define the shape of data going in and out of the API.
FastAPI uses these for automatic request validation and
OpenAPI documentation generation.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, HttpUrl


class URLCreate(BaseModel):
    """Request body for creating a shortened URL."""
    url: HttpUrl  # Validates that the input is a proper HTTP/HTTPS URL


class URLResponse(BaseModel):
    """Response after successfully creating a shortened URL."""
    short_code: str
    short_url: str


class URLStats(BaseModel):
    """Response for the stats endpoint — shows usage data for a short URL."""
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    original_url: str
    clicks: int
    created_at: datetime


class HealthResponse(BaseModel):
    """Response for the health check endpoint."""
    status: str
    version: str
