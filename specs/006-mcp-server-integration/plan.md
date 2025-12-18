# Implementation Plan: MCP Server Integration

**Branch**: `006-mcp-server-integration` | **Date**: 2025-12-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-mcp-server-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create an MCP server that exposes FastAPI todo backend endpoints as AI-accessible tools. The server uses the official MCP Python SDK (FastMCP), supports HTTP transport, implements service-to-service authentication, and propagates user context to the backend. Five tools will be exposed: list_tasks, create_task, update_task, delete_task, and mark_task_completed.

## Technical Context

**Language/Version**: Python 3.12+ (matches existing backend)
**Primary Dependencies**: FastMCP (official MCP Python SDK), httpx (async HTTP client), pydantic (data validation)
**Storage**: N/A (MCP server is stateless; backend handles persistence via Neon PostgreSQL)
**Testing**: pytest with pytest-asyncio (matches backend testing framework)
**Target Platform**: Development server (local), production deployment TBD
**Project Type**: Microservice (separate service that communicates with FastAPI backend)
**Performance Goals**: <2 seconds per tool operation under normal network conditions (SC-007), support 100 concurrent AI requests (SC-009)
**Constraints**: 30-second timeout for backend HTTP requests (FR-023), retry logic with exponential backoff (FR-024)
**Scale/Scope**: Single MCP server instance, 5 AI tools (list/create/update/delete/bulk_delete), service-to-service authentication with user context propagation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Test-First Development (TDD)
**Status**: ✅ PASS
**Application**: All MCP tool implementations will follow TDD. Tests will be written before tool handlers, validating authentication, user context propagation, backend communication, error handling, and retry logic.

### Principle II: Clean Code & Simplicity
**Status**: ✅ PASS
**Application**: MCP server code will follow PEP 8, use type hints, keep functions focused (<20 lines preferred), and avoid over-engineering. YAGNI applies - only implement the 5 requested tools without premature abstractions.

### Principle III: Proper Project Structure
**Status**: ⚠️ REQUIRES JUSTIFICATION
**Violation**: Adding a new service component (MCP server) to existing web application architecture
**Justification**: The MCP server is a separate microservice required to expose backend API to AI assistants. It cannot be integrated into the existing backend (FastAPI) or frontend structure because:
- MCP protocol requires dedicated server implementation
- Separation enables independent scaling and deployment
- Service-to-service authentication pattern requires isolated authentication layer
- Aligns with microservices architecture already established (Node.js auth server, Python FastAPI backend, React frontend)

**Decision**: Create `mcp-server/` directory at repository root alongside `backend/`, `frontend/`, and `auth-server/`

### Principle IV: In-Memory Data Storage
**Status**: ✅ PASS
**Application**: MCP server is stateless and stores no data. All persistence is handled by the FastAPI backend via Neon PostgreSQL.

### Principle V: Command-Line Interface Excellence
**Status**: N/A
**Application**: This feature does not involve CLI; it creates a server that communicates via MCP protocol over HTTP transport.

### Principle VI: UV Package Manager Integration
**Status**: ✅ PASS
**Application**: MCP server will use UV for dependency management, matching backend project structure. Will initialize with `uv init --package .` in `mcp-server/` directory.

## Project Structure

### Documentation (this feature)

```text
specs/006-mcp-server-integration/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
mcp-server/              # NEW: MCP server microservice
├── src/
│   ├── __init__.py
│   ├── server.py        # FastMCP server initialization
│   ├── config.py        # Environment configuration (SERVICE_AUTH_TOKEN, FASTAPI_BASE_URL)
│   ├── client.py        # HTTP client for FastAPI backend communication
│   ├── auth.py          # Service authentication logic
│   ├── tools/           # MCP tool implementations
│   │   ├── __init__.py
│   │   ├── list_tasks.py
│   │   ├── create_task.py
│   │   ├── update_task.py
│   │   ├── delete_task.py
│   │   └── mark_completed.py
│   └── schemas/         # Pydantic schemas for tool parameters and responses
│       ├── __init__.py
│       └── task.py
├── tests/
│   ├── conftest.py      # pytest fixtures
│   ├── contract/        # Contract tests for tool interfaces
│   │   └── test_tool_contracts.py
│   ├── integration/     # End-to-end tests with backend
│   │   ├── test_list_tasks.py
│   │   ├── test_create_task.py
│   │   ├── test_update_task.py
│   │   ├── test_delete_task.py
│   │   └── test_mark_completed.py
│   └── unit/            # Unit tests for components
│       ├── test_client.py
│       └── test_auth.py
├── pyproject.toml       # Project configuration (UV)
├── .env.example         # Environment variable template
└── README.md            # Setup and usage instructions

backend/                 # MODIFIED: Dual authentication support
├── src/
│   ├── api/
│   │   └── dependencies.py  # MODIFY: Support service token + X-User-ID
│   └── ...              # (existing structure unchanged)
└── ...
```

**Structure Decision**: Microservice architecture. The MCP server is a new standalone service (`mcp-server/`) that communicates with the existing FastAPI backend (`backend/`) via HTTP. This aligns with the existing multi-service architecture (Node.js auth-server, Python backend, React frontend).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Adding 4th service (mcp-server) | Expose backend API to AI assistants via MCP protocol | Cannot integrate into backend: MCP server requires dedicated HTTP transport handling, separate service authentication layer, and independent lifecycle management. Cannot integrate into frontend: MCP protocol is server-side only. |

---

## Post-Design Constitution Review

**Re-evaluation Date**: 2025-12-18 (after Phase 1 design completion)

### Constitution Check Results

#### Principle I: Test-First Development
**Status**: ✅ PASS (Confirmed)
**Evidence**:
- Quickstart guide specifies TDD workflow for all components
- Test structure defined: contract/ → unit/ → integration/
- All tool implementations require tests before code
- Research doc confirms pytest + pytest-asyncio testing strategy

#### Principle II: Clean Code & Simplicity
**Status**: ✅ PASS (Confirmed)
**Evidence**:
- Data model uses simple Pydantic schemas
- No premature abstractions introduced
- Backend client is single-purpose HTTP wrapper
- Tool implementations follow single responsibility
- Type hints used throughout (mypy compatible)

#### Principle III: Proper Project Structure
**Status**: ✅ JUSTIFIED (Confirmed with justification)
**Evidence**:
- New `mcp-server/` directory with standard structure (src/, tests/)
- Separation justified: MCP protocol requirements, service auth isolation
- Aligns with existing microservices pattern
- Complexity tracking table documents decision rationale

#### Principle IV: In-Memory Data Storage
**Status**: ✅ PASS (Confirmed)
**Evidence**:
- MCP server is stateless (no persistence)
- All data storage handled by backend PostgreSQL
- Data models are transient (request/response only)

#### Principle V: Command-Line Interface Excellence
**Status**: N/A (Confirmed)
**Evidence**: No CLI component in this feature

#### Principle VI: UV Package Manager Integration
**Status**: ✅ PASS (Confirmed)
**Evidence**:
- Quickstart specifies `uv init --package .`
- pyproject.toml configured for UV
- Dependencies managed via UV sync
- Matches backend project structure

### Final Constitution Verdict

**Overall Status**: ✅ APPROVED

**Summary**: All constitution principles are satisfied. The single justified violation (adding 4th service) is necessary and properly documented. Design maintains simplicity, follows TDD, and integrates with existing project standards.

**Action**: Proceed to Phase 2 (/sp.tasks) to generate implementation tasks.
