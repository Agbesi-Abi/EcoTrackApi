#!/bin/bash
# Production start script for EcoTrack Ghana API

# Get port from environment or default to 8000
PORT=${PORT:-8000}

echo "🌍 Starting EcoTrack Ghana API on port $PORT"

# Initialize database if needed
python -c "from database import init_db; init_db()" || true

# Start the server
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
