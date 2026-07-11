"""
Test suite for the URL Shortener API.

Uses FastAPI's TestClient (backed by httpx) to test all endpoints
without needing to start a real server. Each test function gets a
fresh in-memory SQLite database to prevent test pollution.

These tests will be run by:
1. You — locally during development
2. Person 3 — inside the GitHub Actions CI pipeline
3. Person 3 — inside the Docker container as a container-based test
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


# ---------------------------------------------------------------------------
# Test Database Setup
# ---------------------------------------------------------------------------
# Use an in-memory SQLite database for tests so they run fast and don't
# interfere with the real database. StaticPool ensures the same connection
# is reused across the session (required for in-memory SQLite).

SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


def override_get_db():
    """Provide a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the database dependency so the app uses the test database
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """
    Create tables before each test and drop them after.
    This ensures every test starts with a clean database.
    """
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


# Create the test client
client = TestClient(app)


# ---------------------------------------------------------------------------
# Test: Health Check
# ---------------------------------------------------------------------------

def test_health_returns_200():
    """GET /health should return 200 with status and version."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.1"


# ---------------------------------------------------------------------------
# Test: Create Short URL
# ---------------------------------------------------------------------------

def test_shorten_creates_short_url():
    """POST /shorten should create a short URL and return the code."""
    response = client.post("/shorten", json={"url": "https://www.google.com"})
    assert response.status_code == 201

    data = response.json()
    assert "short_code" in data
    assert "short_url" in data
    assert len(data["short_code"]) == 6
    assert data["short_code"] in data["short_url"]


def test_shorten_rejects_invalid_url():
    """POST /shorten should reject an invalid URL with 422."""
    response = client.post("/shorten", json={"url": "not-a-valid-url"})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Test: Redirect
# ---------------------------------------------------------------------------

def test_redirect_to_original_url():
    """GET /{code} should redirect to the original URL."""
    # First, create a short URL
    create_response = client.post(
        "/shorten", json={"url": "https://www.example.com"}
    )
    code = create_response.json()["short_code"]

    # Then, follow the redirect
    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://www.example.com/"


def test_redirect_increments_click_count():
    """Each visit to GET /{code} should increment the click counter."""
    # Create a short URL
    create_response = client.post(
        "/shorten", json={"url": "https://www.example.com"}
    )
    code = create_response.json()["short_code"]

    # Visit it 3 times
    for _ in range(3):
        client.get(f"/{code}", follow_redirects=False)

    # Check stats
    stats_response = client.get(f"/stats/{code}")
    assert stats_response.json()["clicks"] == 3


# ---------------------------------------------------------------------------
# Test: Statistics
# ---------------------------------------------------------------------------

def test_stats_returns_url_info():
    """GET /stats/{code} should return URL info and click count."""
    # Create a short URL
    create_response = client.post(
        "/shorten", json={"url": "https://www.github.com"}
    )
    code = create_response.json()["short_code"]

    # Get stats
    response = client.get(f"/stats/{code}")
    assert response.status_code == 200

    data = response.json()
    assert data["short_code"] == code
    assert data["original_url"] == "https://www.github.com/"
    assert data["clicks"] == 0
    assert "created_at" in data


# ---------------------------------------------------------------------------
# Test: Not Found
# ---------------------------------------------------------------------------

def test_redirect_invalid_code_returns_404():
    """GET /{code} with a non-existent code should return 404."""
    response = client.get("/nonexistent", follow_redirects=False)
    assert response.status_code == 404


def test_stats_invalid_code_returns_404():
    """GET /stats/{code} with a non-existent code should return 404."""
    response = client.get("/stats/nonexistent")
    assert response.status_code == 404
