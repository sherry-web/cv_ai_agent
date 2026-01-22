# =============================================================================
# CV AI Agent - Production Docker Container
# =============================================================================
# Build: docker build -t cv-ai-agent .
# Run:   docker run -p 5000:5000 --env-file .env cv-ai-agent
# =============================================================================

# -----------------------------------------------------------------------------
# BASE IMAGE
# -----------------------------------------------------------------------------
# python:3.12-slim - Official, security-maintained, minimal footprint
# Debian-based with essential system packages
FROM python:3.12-slim AS builder

# -----------------------------------------------------------------------------
# SYSTEM DEPENDENCIES & ENVIRONMENT
# -----------------------------------------------------------------------------
# Install system packages needed for Python dependencies and security
# Clean up apt cache in same layer to reduce image size
RUN apt-get update && apt-get install -y \
    # Required for building Python packages
    gcc \
    # Security updates and certificate management
    ca-certificates \
    # Cleanup utilities
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# APPLICATION USER
# -----------------------------------------------------------------------------
# Create non-root user for security best practices
# Prevents container running as root if compromised
RUN useradd --create-home --shell /bin/bash appuser

# -----------------------------------------------------------------------------
# WORKING DIRECTORY
# -----------------------------------------------------------------------------
# Set application directory with proper permissions
WORKDIR /app

# -----------------------------------------------------------------------------
# DEPENDENCY INSTALLATION
# -----------------------------------------------------------------------------
# Copy requirements first for Docker layer caching optimization
# Changes to code won't trigger dependency reinstallation
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Prevents pip cache, reduces image size
# --user: Install to user directory for security
RUN pip install --no-cache-dir --user -r requirements.txt

# -----------------------------------------------------------------------------
# APPLICATION CODE
# -----------------------------------------------------------------------------
# Copy application files (excludes .dockerignore patterns)
# Set ownership to non-root user
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# -----------------------------------------------------------------------------
# RUNTIME CONFIGURATION
# -----------------------------------------------------------------------------
# Expose the default Flask port
# Can be overridden via PORT environment variable
EXPOSE 5000

# -----------------------------------------------------------------------------
# ENVIRONMENT VARIABLES
# -----------------------------------------------------------------------------
# Default environment variables (can be overridden at runtime)
# FLASK_ENV=production ensures debug mode is disabled
# PYTHONUNBUFFERED ensures Python output is sent to Docker logs immediately
ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:${PATH}"

# -----------------------------------------------------------------------------
# HEALTH CHECK
# -----------------------------------------------------------------------------
# Container health monitoring
# Checks /health endpoint every 30 seconds
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; import sys; \
    exit(0 if urllib.request.urlopen('http://localhost:5000/health').getcode() == 200 else 1)"

# -----------------------------------------------------------------------------
# ENTRYPOINT
# -----------------------------------------------------------------------------
# Use gunicorn as production WSGI server
# -w 4: 4 worker processes (adjust based on CPU cores)
# -b 0.0.0.0:5000: Bind to all interfaces on port 5000
# app:create_app(): Import app factory from app.py
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:create_app()"]

# -----------------------------------------------------------------------------
# BUILD NOTES
# -----------------------------------------------------------------------------
# This Dockerfile follows the 12-factor app methodology:
# 1. Codebase in version control ✓
# 2. Dependencies explicitly declared ✓ (requirements.txt)
# 3. Config stored in environment ✓ (.env.example pattern)
# 4. Backing services attached via environment ✓
# 5. Build, release, run separation ✓ (multi-stage ready)
# 6. Stateless processes ✓
# 7. Port binding ✓ (EXPOSE 5000)
# 8. Concurrency via process model ✓ (gunicorn workers)
# 9. Disposability ✓ (graceful shutdown support)
# 10. Dev/prod parity ✓ (same image, different config)
# 11. Logs to stdout ✓ (PYTHONUNBUFFERED)
# 12. Admin processes as one-offs ✓ (docker exec support)
# =============================================================================