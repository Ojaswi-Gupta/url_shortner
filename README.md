# 🚀 Containerized Build Pipeline to Azure Container Registry

**DevOps Certification Project** — Containerize a FastAPI application and build a CI pipeline that automatically tests, builds, scans, and pushes Docker images to Azure Container Registry.

## 📋 Project Overview

An application currently runs only on a developer's laptop with no repeatable build process. This project containerizes it and builds a CI pipeline that:

```
Code Push → GitHub Actions → Tests Run → Docker Image Built → Container Tested → Vulnerability Scan → Push to ACR
```

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Developer   │────▶│  GitHub Actions   │────▶│  Azure Container    │
│  pushes code │     │  CI Pipeline      │     │  Registry (ACR)     │
└──────────────┘     │                   │     │                     │
                     │  1. Run pytest    │     │  Tagged images:     │
                     │  2. Build image   │     │  - v1.0.0           │
                     │  3. Test /health  │     │  - build-42         │
                     │  4. Trivy scan    │     │  - sha-a1b2c3d      │
                     │  5. Push to ACR   │     │                     │
                     └──────────────────┘     └─────────────────────┘
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Application | Python, FastAPI, SQLAlchemy, SQLite |
| Containerization | Docker |
| CI/CD Pipeline | GitHub Actions |
| Container Registry | Azure Container Registry (ACR) |
| Vulnerability Scanning | Trivy |

## 📂 Project Structure

```
url-shortener/
├── app/
│   ├── __init__.py          # Package init
│   ├── main.py              # FastAPI application and endpoints
│   ├── database.py          # SQLAlchemy database configuration
│   ├── models.py            # ORM model (URL table)
│   ├── schemas.py           # Pydantic request/response schemas
│   └── utils.py             # Short code generation utility
├── tests/
│   ├── __init__.py          # Package init
│   └── test_api.py          # Pytest test suite (8 tests)
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI pipeline
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container build instructions
├── .dockerignore            # Files excluded from Docker build
├── .gitignore               # Files excluded from Git
└── README.md                # This file
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check (used by CI pipeline) |
| `POST` | `/shorten` | Create a shortened URL |
| `GET` | `/{code}` | Redirect to the original URL |
| `GET` | `/stats/{code}` | View click statistics for a short URL |

### Example Usage

**Health Check:**
```bash
curl http://localhost:8000/health
# {"status": "healthy", "version": "1.0.0"}
```

**Create Short URL:**
```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
# {"short_code": "aB3xY7", "short_url": "http://localhost:8000/aB3xY7"}
```

**View Stats:**
```bash
curl http://localhost:8000/stats/aB3xY7
# {"short_code": "aB3xY7", "original_url": "https://www.google.com", "clicks": 5, "created_at": "..."}
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Docker

### Run Locally (without Docker)

```bash
# Clone the repo
git clone https://github.com/Ojaswi-Gupta/url_shortner.git
cd url_shortner

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload

# Visit: http://localhost:8000/docs
```

### Run with Docker

```bash
# Build the image
docker build -t url-shortener:latest .

# Run the container
docker run -d -p 8000:8000 --name url-app url-shortener:latest

# Verify
curl http://localhost:8000/health

# Stop
docker stop url-app && docker rm url-app
```

### Run Tests

```bash
pytest tests/ -v
```

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline runs automatically on every push to `main` and `develop`:

1. **Test** — Runs `pytest` to verify all 8 tests pass
2. **Build** — Builds the Docker image
3. **Container Test** — Starts the container and checks `/health`
4. **Scan** — Runs Trivy vulnerability scan (fails on CRITICAL findings)
5. **Push** — Tags and pushes the image to Azure Container Registry

### Image Tagging Strategy

Each image is tagged with:
- **Build number**: `url-shortener:build-42`
- **Commit SHA**: `url-shortener:sha-a1b2c3d`
- **Semantic version**: `url-shortener:1.0.0`

> **Why not `latest`?** The `latest` tag is mutable — it gets overwritten on every push, making production rollbacks unreliable. Immutable version tags (build number, SHA) let you roll back to any specific build.

## 🔒 Security

### Vulnerability Scanning

Trivy scans every Docker image before it is pushed to ACR. The pipeline is configured to:
- **CRITICAL vulnerabilities** → Pipeline fails (image is NOT pushed)
- **HIGH/MEDIUM/LOW** → Warning only (image is pushed with findings logged)

### Responsible Engineering Note

> If a critical vulnerability is found, the pipeline should **block automatically**, not just warn. A warning-only approach risks deploying known-vulnerable containers to production. Automated blocking enforces security as a gate, not a suggestion.

## 🧹 ACR Retention Policy

To prevent unbounded storage growth in Azure Container Registry:

- **Untagged manifests**: Automatically purge after 7 days
- **Development images** (`build-*`): Retain last 30 builds, delete older ones
- **Release images** (`v*.*.*`): Retain indefinitely
- Enforce via `az acr run --cmd "acr purge"` on a scheduled task

## 👥 Team

| Role | Responsibility |
|------|---------------|
| **Person 1** — Application + Docker | FastAPI app, Dockerfile, tests, container testing |
| **Person 2** — Azure + ACR | Resource group, ACR setup, authentication, retention policy |
| **Person 3** — CI Pipeline + Security | GitHub Actions, Trivy scanning, image tagging, end-to-end pipeline |

## 📦 Azure Services Used

- **Azure Container Registry (ACR)** — Stores versioned, tagged container images
- **GitHub Actions** — Builds, tests, scans, and pushes Docker images
- **Trivy** — Scans images for known vulnerabilities
