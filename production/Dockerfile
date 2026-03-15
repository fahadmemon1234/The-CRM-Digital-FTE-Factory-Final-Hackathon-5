# TechCorp Customer Success AI Agent - Production Dockerfile
#
# Multi-stage build for optimized production image.
#
# INCUBATION MAPPING:
# -------------------
# Incubation: Local Python script execution
# Production: Containerized deployment with optimized image
#
# Usage:
#   docker build -t techcorp/fte:latest .
#   docker run -p 8000:8000 techcorp/fte:latest
#
# Author: AI Engineering Team
# Version: 1.0.0 (Production)

# ============================================================================
# BASE IMAGE
# ============================================================================

FROM python:3.11-slim

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

# Set Python environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# ============================================================================
# SYSTEM DEPENDENCIES
# ============================================================================

# Install system packages required for dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Required for asyncpg (PostgreSQL driver)
    libpq-dev \
    # Required for cryptography
    libffi-dev \
    # Required for some Python packages
    gcc \
    # Useful utilities
    curl \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# PYTHON DEPENDENCIES
# ============================================================================

# Copy requirements first for better caching
COPY production/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# APPLICATION CODE
# ============================================================================

# Copy application code
COPY production /app/production
COPY context /app/context

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# ============================================================================
# EXPOSE PORT
# ============================================================================

EXPOSE 8000

# ============================================================================
# HEALTH CHECK
# ============================================================================

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ============================================================================
# ENTRYPOINT
# ============================================================================

CMD ["uvicorn", "production.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
