# Multi-stage production Dockerfile for FastAPI backend using uv
# Stage 1: Builder - Install dependencies with uv
FROM python:3.12-slim AS builder

# Install uv (official method - fast binary copy)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only metadata files needed for dependency resolution
# (source code is not needed for this approach)
COPY backend/pyproject.toml ./backend/pyproject.toml

# Compile dependencies to requirements.txt and install
# This approach avoids editable install issues in build stage
# This layer is cached and only rebuilds when dependencies change
RUN uv pip compile backend/pyproject.toml -o requirements.txt && \
    uv venv && \
    uv pip install -r requirements.txt

# Stage 2: Runtime - Create minimal production image
FROM python:3.12-slim

# Install uv in runtime (needed for uv run commands)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code and metadata
COPY --chown=appuser:appuser backend/src/ ./src/
COPY --chown=appuser:appuser backend/alembic/ ./alembic/
COPY --chown=appuser:appuser backend/alembic.ini ./
COPY --chown=appuser:appuser backend/pyproject.toml ./
COPY --chown=appuser:appuser backend/README.md ./

# Install the backend package itself (dependencies already installed in stage 1)
RUN uv pip install --no-deps -e .

# Copy entrypoint script
COPY --chown=appuser:appuser backend/entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Activate virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Use entrypoint script to run migrations before starting app
ENTRYPOINT ["./entrypoint.sh"]
