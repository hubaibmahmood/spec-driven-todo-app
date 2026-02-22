# ========================================
# Stage 1: Builder - Install dependencies
# ========================================
FROM python:3.12-slim AS builder

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy only metadata files needed for dependency resolution
# (source code is not needed for this approach)
COPY mcp-server/pyproject.toml ./mcp-server/pyproject.toml

# Compile dependencies to requirements.txt and install
# This approach avoids editable install issues in build stage
# This layer is cached and only rebuilds when dependencies change
RUN uv pip compile mcp-server/pyproject.toml -o requirements.txt && \
    uv venv && \
    uv pip install -r requirements.txt

# ========================================
# Stage 2: Runtime - Minimal production image
# ========================================
FROM python:3.12-slim

# Install uv in runtime (needed for running the server and potential runtime commands)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application source code and metadata
COPY mcp-server/src/ ./src/
COPY mcp-server/README.md ./
COPY mcp-server/pyproject.toml ./

# Install the mcp-server package itself (dependencies already installed in stage 1)
RUN uv pip install --no-deps -e .

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Environment variables
ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Expose default MCP server port (can be overridden by PORT env var)
EXPOSE 3000

# Health check (MCP server doesn't expose HTTP health endpoint, so check process)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD pgrep -f "python.*server" || exit 1

# Run the MCP server using the registered script
CMD ["python", "-m", "src.server"]
