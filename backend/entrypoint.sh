#!/bin/bash
set -e

echo "Starting backend service..."

# Run database migrations
echo "Running Alembic migrations..."
alembic upgrade head || {
    echo "WARNING: Migration failed, continuing anyway..."
}

# Start the FastAPI application
echo "Starting Uvicorn server..."
exec uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info
