# MCP Server - Todo Backend Integration

MCP (Model Context Protocol) server that exposes the FastAPI todo backend as AI-accessible tools.

## Overview

This MCP server enables AI assistants (like Claude) to manage todo tasks by providing 5 tools:
- `list_tasks` - Retrieve all tasks for the authenticated user
- `create_task` - Create a new task
- `update_task` - Update task fields (title, description, priority, due_date)
- `mark_task_completed` - Mark a task as completed
- `delete_task` - Delete a task

## Architecture

```
AI Assistant (Claude Desktop)
        ↓
MCP Server (HTTP Transport)
        ↓ Service Auth (Bearer Token + X-User-ID)
FastAPI Backend
        ↓
Neon PostgreSQL Database
```

### Authentication Flow

The MCP server uses **service-to-service authentication**:
1. MCP server authenticates with backend using `SERVICE_AUTH_TOKEN`
2. User context is propagated via `X-User-ID` header
3. Backend validates service token AND ensures data isolation per user

## Setup

### Prerequisites

- Python 3.12+
- UV package manager
- FastAPI backend running (see `../backend`)

### Installation

```bash
# Install dependencies
cd mcp-server
uv sync

# Create environment configuration
cp .env.example .env

# Generate a secure service token (32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))" > /tmp/token.txt

# Add the token to .env
echo "SERVICE_AUTH_TOKEN=$(cat /tmp/token.txt)" >> .env
echo "FASTAPI_BASE_URL=http://localhost:8000" >> .env

# Add the same token to backend/.env
echo "SERVICE_AUTH_TOKEN=$(cat /tmp/token.txt)" >> ../backend/.env

# Clean up
rm /tmp/token.txt
```

## Development

### Project Structure

```
mcp-server/
├── src/
│   ├── server.py          # FastMCP server entry point
│   ├── config.py          # Environment configuration
│   ├── client.py          # HTTP client for backend communication
│   ├── tools/             # MCP tool implementations
│   └── schemas/           # Pydantic schemas
├── tests/
│   ├── contract/          # Contract tests for tool interfaces
│   ├── unit/              # Unit tests for components
│   └── integration/       # End-to-end tests with backend
└── README.md              # This file
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run type checking
uv run mypy src/

# Run linting
uv run ruff check src/
```

See full documentation in the project README for setup, configuration, and usage instructions.
