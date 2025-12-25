# Use Python 3.12 slim image
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml ./
COPY README.md ./

# Install dependencies (ignoring lock file if missing)
RUN uv pip install --system --no-cache .

# Copy source code and database migration files
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./

# Environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose the port (Railway will override PORT)
EXPOSE 8000

# Run database migrations on startup, then start the server
CMD alembic upgrade head && uvicorn ai_agent.main:app --host 0.0.0.0 --port ${PORT:-8000}