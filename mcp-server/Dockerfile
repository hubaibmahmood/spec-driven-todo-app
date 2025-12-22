# Use Python 3.12 slim image
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies
# --frozen: use uv.lock
# --no-dev: exclude dev dependencies
# --no-install-project: we'll install the project code separately (or just run from source)
RUN uv sync --frozen --no-dev --no-install-project

# Copy source code
COPY src ./src
COPY README.md ./

# Install the project itself (if needed, or just rely on pythonpath)
# We can just run using `uv run` which handles the venv
# But for production container, it's often cleaner to rely on the sync'd venv
ENV PATH="/app/.venv/bin:$PATH"

# Environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose the port (Railway will override PORT, but this is good documentation)
EXPOSE 3000

# Command to run the server
CMD ["python", "-m", "src.server"]
