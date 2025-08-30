# ============================================================================
# AgriConnect API - Production Dockerfile
# Multi-stage build for optimal production deployment
# ============================================================================

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libgdal-dev \
    gdal-bin \
    libgeos-dev \
    libproj-dev \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt requirements-production.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt -r requirements-production.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=agriconnect.production_settings \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    libgdal28 \
    libgeos-c1v5 \
    libproj22 \
    libjpeg62-turbo \
    libpng16-16 \
    libfreetype6 \
    libxml2 \
    libxslt1.1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app user
RUN groupadd -r agriconnect && useradd -r -g agriconnect agriconnect

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set work directory
WORKDIR /app

# Copy application code
COPY --chown=agriconnect:agriconnect . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R agriconnect:agriconnect /app

# Switch to non-root user
USER agriconnect

# Collect static files
RUN python manage.py collectstatic --noinput --settings=agriconnect.production_settings

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Expose port
EXPOSE 8000

# Production command
CMD ["gunicorn", "--config", "gunicorn.conf.py", "agriconnect.wsgi:application"]
