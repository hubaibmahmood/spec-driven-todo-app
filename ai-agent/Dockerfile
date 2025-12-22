# Use Python 3.12 slim image
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first
COPY pyproject.toml ./

# Install dependencies
# Note: Since there's no uv.lock yet, we'll use pip-compile approach
RUN uv pip install --system -e .

# Copy source code
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./
COPY README.md ./

# Environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose the port (Railway will override PORT)
EXPOSE 8000

# Run database migrations on startup, then start the server
CMD alembic upgrade head && uvicorn ai_agent.main:app --host 0.0.0.0 --port ${PORT:-8000}
