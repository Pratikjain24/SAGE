# SAGE-Live Production Docker Image
# Multi-stage build for minimal final image size.
#
# Build:
#   docker build -f docker/Dockerfile -t sage-live:latest .
#
# Run:
#   docker run -p 8000:8000 --env-file .env sage-live:latest

# ---------------------------------------------------------------------------
# Stage 1: Builder — install Poetry and export requirements
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME=/opt/poetry

# System dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

WORKDIR /build

# Copy only dependency files first for Docker layer caching
COPY pyproject.toml poetry.lock* ./

# Export to requirements.txt (no dev deps)
RUN poetry export -f requirements.txt --without dev --output requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: Runtime — minimal production image
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

LABEL maintainer="SAGE-Live Team <sage@example.com>" \
      description="Self-Refreshing, Cryptographically Attested AI Safety Benchmark System" \
      version="0.1.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    API_WORKERS=4 \
    LOG_LEVEL=INFO

# Runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN groupadd --gid 1001 sagegroup \
    && useradd --uid 1001 --gid sagegroup --shell /bin/bash --create-home sagelive

WORKDIR /app

# Install Python dependencies from the exported requirements
COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY --chown=sagelive:sagegroup sage_live/ ./sage_live/
COPY --chown=sagelive:sagegroup configs/ ./configs/
COPY --chown=sagelive:sagegroup pyproject.toml ./

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data \
    && chown -R sagelive:sagegroup /app/logs /app/data

# Switch to non-root user
USER sagelive

# Health check — calls the /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${API_PORT}/health || exit 1

EXPOSE ${API_PORT}

# Use exec form to handle signals correctly
CMD ["sh", "-c", \
    "uvicorn sage_live.api:app \
     --host ${API_HOST} \
     --port ${API_PORT} \
     --workers ${API_WORKERS} \
     --log-level ${LOG_LEVEL,,} \
     --proxy-headers \
     --forwarded-allow-ips='*'"]
