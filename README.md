# URL Shortener — DevOps Certification Project

A simple FastAPI URL shortener service built for a DevOps certification project. The application is intentionally kept simple because the focus is on **containerization**, **CI/CD pipelines**, and **image security scanning**.

## Endpoints

| Method | Endpoint        | Description                              |
|--------|-----------------|------------------------------------------|
| GET    | `/health`       | Service health check (used by CI pipeline) |
| POST   | `/shorten`      | Create a shortened URL                   |
| GET    | `/{code}`       | Redirect to the original URL             |
| GET    | `/stats/{code}` | View click statistics for a short URL    |

## Project Structure

```
url-shortener/
├── app/
│   ├── __init__.py      # Package init
│   ├── main.py          # FastAPI application and endpoints
│   ├── database.py      # SQLAlchemy database configuration
│   ├── models.py        # ORM model (URL table)
│   ├── schemas.py       # Pydantic request/response schemas
│   └── utils.py         # Short code generation utility
├── tests/
│   ├── __init__.py      # Package init
│   └── test_api.py      # Pytest test suite (8 tests)
├── requirements.txt     # Pinned Python dependencies
├── Dockerfile           # Container build instructions
├── .dockerignore        # Files excluded from Docker build
└── README.md            # This file
```

## Local Development Setup

### Prerequisites
- Python 3.12+
- Docker

### 1. Create Virtual Environment

```bash
cd url-shortener
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
uvicorn app.main:app --reload
```

Visit the interactive API docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Run Tests

```bash
pytest tests/ -v
```

## Docker

### Build the Image

```bash
docker build -t url-shortener:latest .
```

### Run the Container

```bash
docker run -d -p 8000:8000 --name url-app url-shortener:latest
```

### Verify the Container

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Stop and Remove the Container

```bash
docker stop url-app
docker rm url-app
```

## Container-Based Test

After building the image, you can run a container-based health check:

```bash
# Start the container
docker run -d -p 8000:8000 --name url-app url-shortener:latest

# Wait for startup
sleep 3

# Test the health endpoint
curl -f http://localhost:8000/health

# Cleanup
docker stop url-app
docker rm url-app
```

If `curl -f` exits with a non-zero code, the container is not healthy.

## API Usage Examples

### Create a Short URL

```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
```

Response:
```json
{
  "short_code": "aB3xY7",
  "short_url": "http://localhost:8000/aB3xY7"
}
```

### Redirect

```bash
curl -L http://localhost:8000/aB3xY7
```

### View Statistics

```bash
curl http://localhost:8000/stats/aB3xY7
```

Response:
```json
{
  "short_code": "aB3xY7",
  "original_url": "https://www.google.com",
  "clicks": 1,
  "created_at": "2026-07-07T12:00:00"
}
```

## For Team Members

### Person 2 (Azure + ACR)
The Docker image built from this project can be pushed to ACR:
```bash
docker tag url-shortener:latest <acr-name>.azurecr.io/url-shortener:1.0.0
docker push <acr-name>.azurecr.io/url-shortener:1.0.0
```

### Person 3 (CI Pipeline)
- Tests: `pytest tests/ -v` (8 tests, all should pass)
- Health check: `curl -f http://localhost:8000/health`
- The `/health` endpoint returns a simple JSON object for easy CI validation
