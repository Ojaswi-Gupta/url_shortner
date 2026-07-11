"""
URL Shortener — FastAPI Application

A simple URL shortener service built for a DevOps certification project.
The application is intentionally kept simple because the focus of the
project is containerization, CI/CD pipelines, and image security scanning,
not application complexity.

Endpoints:
    GET  /health        → Service health check (used by CI pipeline)
    POST /shorten       → Create a shortened URL
    GET  /{code}        → Redirect to the original URL
    GET  /stats/{code}  → View click statistics for a short URL
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import engine, get_db, Base
from app.models import URL
from app.schemas import URLCreate, URLResponse, URLStats, HealthResponse
from app.utils import generate_short_code

# Application version — used in /health and for image tagging
APP_VERSION = "1.0.1"

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener",
    description="A simple URL shortener service for DevOps pipeline demonstration.",
    version=APP_VERSION,
)


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Health check endpoint.

    Returns the service status and version. This endpoint is critical
    for the CI/CD pipeline — GitHub Actions will start the container
    and hit this endpoint to verify the application is running correctly
    before pushing the image to Azure Container Registry.
    """
    return HealthResponse(status="healthy", version=APP_VERSION)


# ---------------------------------------------------------------------------
# Create Short URL
# ---------------------------------------------------------------------------

@app.post("/shorten", response_model=URLResponse, status_code=201, tags=["URLs"])
def create_short_url(payload: URLCreate, request: Request, db: Session = Depends(get_db)):
    """
    Create a shortened URL.

    Takes a long URL, generates a unique 6-character code, stores the
    mapping in SQLite, and returns the short URL.

    If a generated code collides with an existing one (extremely unlikely
    with 62^6 possibilities), the function retries up to 10 times.
    """
    # Convert the Pydantic HttpUrl to a plain string for storage
    original_url = str(payload.url)

    # Generate a unique short code (retry on collision)
    for _ in range(10):
        code = generate_short_code()
        existing = db.query(URL).filter(URL.short_code == code).first()
        if not existing:
            break
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate a unique short code. Please try again.",
        )

    # Create and save the URL record
    url_entry = URL(short_code=code, original_url=original_url)
    db.add(url_entry)
    db.commit()
    db.refresh(url_entry)

    # Build the full short URL using the current request's base URL
    base_url = str(request.base_url).rstrip("/")
    short_url = f"{base_url}/{code}"

    return URLResponse(short_code=code, short_url=short_url)


# ---------------------------------------------------------------------------
# Redirect
# ---------------------------------------------------------------------------

@app.get(
    "/{code}",
    response_class=RedirectResponse,
    status_code=307,
    tags=["URLs"],
)
def redirect_to_url(code: str, db: Session = Depends(get_db)):
    """
    Redirect to the original URL.

    Looks up the short code in the database. If found, increments the
    click counter and returns a 307 Temporary Redirect to the original URL.
    If not found, returns 404.

    Uses 307 (Temporary Redirect) instead of 301 (Permanent) so browsers
    don't cache the redirect — this ensures every visit is counted.
    """
    url_entry = db.query(URL).filter(URL.short_code == code).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Increment click count
    url_entry.clicks += 1
    db.commit()

    return RedirectResponse(url=url_entry.original_url, status_code=307)


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

@app.get("/stats/{code}", response_model=URLStats, tags=["URLs"])
def get_url_stats(code: str, db: Session = Depends(get_db)):
    """
    Get click statistics for a shortened URL.

    Returns the original URL, total click count, and creation timestamp.
    """
    url_entry = db.query(URL).filter(URL.short_code == code).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return URLStats(
        short_code=url_entry.short_code,
        original_url=url_entry.original_url,
        clicks=url_entry.clicks,
        created_at=url_entry.created_at,
    )