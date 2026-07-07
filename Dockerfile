# ============================================================
# Stage 1: Build Stage
# ============================================================
# Use the official Python 3.12 slim image to keep the final
# image small (~150MB vs ~1GB for the full image).
# This matters for ACR storage costs and pipeline speed.

FROM python:3.12-slim

# Metadata labels — useful for image inspection and ACR management
LABEL maintainer="team-devops"
LABEL project="url-shortener"
LABEL description="FastAPI URL Shortener for DevOps Certification Project"

# Set the working directory inside the container.
# All subsequent commands run relative to /app.
WORKDIR /app

# Copy requirements first (before the rest of the code).
# Docker caches each layer, so if requirements.txt hasn't changed,
# Docker will reuse the cached pip install layer — this makes
# rebuilds much faster during development.
COPY requirements.txt .

# Install Python dependencies.
# --no-cache-dir prevents pip from storing download cache (saves ~50MB).
# --no-compile skips .pyc generation during install (done at runtime).
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code.
# This layer changes frequently, but the pip install layer above
# is cached, so rebuilds are fast.
COPY . .

# Document which port the application uses.
# This doesn't actually publish the port — it's documentation for
# anyone running the container (they still need -p 8000:8000).
EXPOSE 8000

# Run the FastAPI application using uvicorn.
# --host 0.0.0.0 makes the server listen on all interfaces
# (required inside Docker, otherwise it only listens on localhost
# which is not accessible from outside the container).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
