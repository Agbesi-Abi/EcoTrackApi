#!/bin/sh
set -e

# Simple entrypoint for Docker production image
# - applies Alembic migrations (if DATABASE_URL provided)
# - ensures uploads and logs directories exist
# - starts gunicorn with uvicorn workers

: ${DATABASE_URL:=}
: ${GUNICORN_WORKERS:=4}
: ${GUNICORN_BIND:=0.0.0.0:8000}
: ${PROJECT_MODULE:=main:app}

echo "[entrypoint] starting with ENVIRONMENT=${ENVIRONMENT:-production}"

# Ensure directories
mkdir -p /app/uploads /app/logs
chown -R appuser:appuser /app/uploads /app/logs || true

# Run migrations if alembic is available and DATABASE_URL is set
if [ -n "$DATABASE_URL" ] && [ -f "/app/alembic.ini" ]; then
  echo "[entrypoint] Running alembic upgrade head"
  alembic upgrade head || echo "[entrypoint] Alembic upgrade failed (continuing)"
fi

# Start Gunicorn with Uvicorn workers
exec gunicorn -k uvicorn.workers.UvicornWorker \
  --bind "$GUNICORN_BIND" \
  --workers "$GUNICORN_WORKERS" \
  --log-level info \
  --access-logfile '-' \
  "$PROJECT_MODULE"
