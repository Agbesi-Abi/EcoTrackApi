# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.production.txt ./

# Install Python dependencies (use production requirements)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.production.txt

# Copy application code
# Copy application code
COPY . .

# Create necessary directories and ensure correct ownership
RUN mkdir -p uploads logs \
    && adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app \
    && chmod +x /app/docker-entrypoint.sh || true

# Use non-root user for runtime
USER appuser

# Expose port
EXPOSE 8000

# Health check against the application health endpoint
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Entrypoint will run migrations and start the production server (Gunicorn + Uvicorn workers)
ENTRYPOINT ["/app/docker-entrypoint.sh"]
