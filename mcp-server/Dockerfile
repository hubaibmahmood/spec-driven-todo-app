# Use Python 3.12 slim image
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files and source code
COPY pyproject.toml ./
COPY src ./src
COPY README.md ./

# Install dependencies and project using pip via uv
# Since there's no uv.lock, we install directly from pyproject.toml
RUN uv pip install --system --no-cache -e .

# Environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose the port (Railway will override PORT, but this is good documentation)
EXPOSE 3000

# Command to run the server
CMD ["python", "-m", "src.server"]
