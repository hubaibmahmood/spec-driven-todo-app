# ============================================================================
# AI Agent Microservice - Production Multi-Stage Dockerfile
# ============================================================================
# Optimized for FastAPI + uv + Alembic migrations
# Uses multi-stage build for minimal image size and improved security
# ============================================================================

# ============================================================================
# Stage 1: Builder - Install dependencies and prepare virtual environment
# ============================================================================
FROM python:3.12-slim AS builder

# Install uv (fastest Python package installer)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy only metadata files needed for dependency resolution
# (source code is not needed for this approach)
COPY ai-agent/pyproject.toml ./ai-agent/pyproject.toml

# Compile dependencies to requirements.txt and install
# This approach avoids editable install issues in build stage
# This layer is cached and only rebuilds when dependencies change
RUN uv pip compile ai-agent/pyproject.toml -o requirements.txt && \
    uv venv && \
    uv pip install -r requirements.txt

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.12-slim

# Install runtime dependencies
# - libpq5: PostgreSQL client library (required for asyncpg)
# - curl: Health check support
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv in runtime (needed for "uv run" commands in entrypoint)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser ai-agent/src/ ./src/
COPY --chown=appuser:appuser ai-agent/alembic/ ./alembic/
COPY --chown=appuser:appuser ai-agent/alembic.ini ./
COPY --chown=appuser:appuser ai-agent/pyproject.toml ./
COPY --chown=appuser:appuser ai-agent/README.md ./

# Install the ai-agent package itself (dependencies already installed in stage 1)
RUN uv pip install --no-deps -e .

# Copy and make entrypoint script executable
COPY --chown=appuser:appuser ai-agent/entrypoint.sh ./
RUN chmod +x /app/entrypoint.sh

# Environment variables
ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8002

# Health check (uses /health endpoint)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Use entrypoint script (runs migrations before starting server)
ENTRYPOINT ["/app/entrypoint.sh"]
