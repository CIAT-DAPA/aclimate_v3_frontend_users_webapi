# syntax=docker/dockerfile:1
# ============================================================================
# ACLIMATE v3 — Frontend Users WebAPI Dockerfile
# Stack: Python + FastAPI + Uvicorn
# Port: 3004 (configurable via PORT env var)
# ============================================================================

FROM python:3.11-slim

# Build-time environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=3004

# System dependencies
# git: required to install dependencies from git+https:// URLs
# build-essential (libc6-dev, gcc, make) + python3-dev + libpq-dev:
#   required to compile psycopg2 from source (needs Python.h and stdlib.h)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        libpq-dev \
        build-essential \
        python3-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create non-root user
RUN useradd -l -u 10001 appuser

# Layer 1: Install Python dependencies (cacheable)
COPY src/requirements.txt /app/src/requirements.txt
RUN pip install --no-cache-dir -r /app/src/requirements.txt

# Layer 2: Copy application source code
COPY src/ /app/src

# Cleanup build-time system packages
RUN apt-get remove -y git build-essential python3-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/src

EXPOSE 3004

# Health check (liveness endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=5 \
  CMD curl -fsS http://127.0.0.1:${PORT}/health || exit 1

# Drop privileges
USER appuser

# Start command (shell form resolves ${PORT} at runtime)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --proxy-headers"]