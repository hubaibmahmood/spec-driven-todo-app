#!/bin/bash
# ============================================================================
# AI Agent Entrypoint Script
# ============================================================================
# Runs database migrations before starting the FastAPI application
# Uses uv run to execute commands within the virtual environment
# ============================================================================

set -e  # Exit on error

echo "🚀 Starting AI Agent microservice..."

# Run Alembic migrations (if alembic.ini exists)
if [ -f "alembic.ini" ]; then
    echo "📦 Running database migrations..."
    alembic upgrade head || {
        echo "⚠️  Migration failed, but allowing service to start..."
    }
fi

echo "✅ Starting Uvicorn server..."

# Start the FastAPI application (venv already activated via PATH)
# - 4 workers for production concurrency
# - Bind to all interfaces (0.0.0.0) on port 8002
# - Use exec to ensure proper signal handling for graceful shutdown
exec uvicorn ai_agent.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8002}" \
    --workers 4 \
    --log-level info
