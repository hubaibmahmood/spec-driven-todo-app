# Implementation Plan: OpenAI Agents SDK Integration

**Branch**: `008-openai-agents-sdk-integration` | **Date**: 2025-12-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-openai-agents-sdk-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Transform the basic chat persistence system (spec 007) into an intelligent AI agent by integrating OpenAI Agents SDK with Gemini API backend. The agent runs inside the FastAPI `/api/chat` endpoint handler, uses MCPServerStreamableHttp to connect to the MCP server (spec 006) for task operations, and maintains multi-turn conversation context by loading message history from PostgreSQL and passing to Runner.run(). Natural language queries like "show my tasks" or "add a task to buy groceries" are parsed and executed via MCP tools (list_tasks, create_task, update_task, delete_task, mark_task_completed) with service-to-service authentication using X-User-ID headers.

## Technical Context

**Language/Version**: Python 3.12+ (matches existing FastAPI backend from spec 003)
**Primary Dependencies**:
- OpenAI Agents SDK (openai-agents-python) - agent framework with built-in MCP support
- OpenAI Python SDK (AsyncOpenAI) - for Gemini API via OpenAI-compatible endpoint
- FastAPI 0.104+ - existing chat endpoint handler (spec 007)
- httpx - async HTTP client for MCP server communication
- tiktoken or similar - token counting for context window management
- SQLAlchemy 2.0+ (async) - existing ORM for conversation history (spec 007)
- Pydantic 2.0+ - data validation and settings

**Storage**: Neon serverless PostgreSQL (shared with FastAPI backend, conversation/message tables from spec 007)
**Testing**: pytest (async test support), pytest-asyncio, httpx for async testing
**Target Platform**: Linux server (existing FastAPI deployment environment)
**Project Type**: Web (backend extension - FastAPI chat endpoint enhancement)
**Performance Goals**:
- Agent responds within 3s for simple operations (SC-002)
- Agent responds within 10s for complex operations (SC-002)
- 95% accuracy for clear natural language requests (SC-001)
- 90% accuracy for task attribute extraction (SC-004)

**Constraints**:
- Must integrate with existing `/api/chat` endpoint from spec 007
- Must use service-to-service auth (X-User-ID header) for MCP calls
- Must stay within Gemini 2.5 Flash token limits (implement 80% budget truncation)
- Must handle Gemini API failures gracefully (<5s error response, SC-005)
- Must maintain conversation context across 10+ turns (SC-003)

**Scale/Scope**:
- Single agent instance per request (no shared state)
- Support multi-turn conversations (10+ messages)
- 5 MCP tools (list_tasks, create_task, update_task, delete_task, mark_task_completed)
- Token-based context window management (truncate at 80% of model limit)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development (TDD) ✅ PASS

**Status**: Compliant with modifications for integration testing

**Plan**:
- Tests WILL be written before implementation following Red-Green-Refactor
- Contract tests for agent initialization, MCP connection, message history loading
- Integration tests for end-to-end agent workflows (natural language → MCP tool execution)
- Unit tests for context window management, token counting, message format conversion
- Async test patterns using pytest-asyncio

**Modification**: Integration testing will include external service mocking (Gemini API, MCP server) to maintain test isolation while verifying integration contracts.

### II. Clean Code & Simplicity ✅ PASS

**Status**: Compliant

**Plan**:
- Follow PEP 8, use type hints for all functions
- Keep functions focused and single-purpose
- Descriptive names for agent configuration, message conversion, context management
- No premature optimization - implement token counting simply first
- YAGNI principle: implement only features from spec (no extra agent capabilities)

### III. Proper Project Structure ✅ PASS

**Status**: Compliant - extends existing backend structure

**Plan**:
- Agent code in `ai-agent/src/ai_agent/agent/` (new submodule)
- Tests in `ai-agent/tests/agent/` with contract/integration/unit subdirectories
- Clear separation: agent initialization, MCP connection, context management, message conversion
- Dependencies explicitly declared in `ai-agent/pyproject.toml`

**Rationale**: Extends existing ai-agent FastAPI application structure from spec 007, maintains consistency with existing ai_agent package.

### IV. In-Memory Data Storage ⚠️ NOT APPLICABLE

**Status**: N/A - This feature uses existing PostgreSQL persistence from spec 007

**Justification**: This feature builds on spec 007 (Chat Persistence Service) which already established PostgreSQL for conversation/message storage. The constitution's in-memory constraint was for the initial TODO CLI implementation and does not apply to backend services that require persistence across sessions.

**Why simpler alternative rejected**: In-memory storage would lose conversation history between requests, breaking multi-turn conversation context (core requirement FR-004, SC-003).

### V. Command-Line Interface Excellence ⚠️ NOT APPLICABLE

**Status**: N/A - This feature provides API-based agent, not CLI

**Justification**: This feature enhances the FastAPI `/api/chat` endpoint (spec 007) with intelligent agent capabilities. User interaction is via HTTP API, not CLI. The constitution's CLI standards apply to the original TODO CLI application, not backend API services.

**Alternative compliance**: Agent responses MUST be user-friendly and well-formatted (FR-013) - applies API-level UX standards equivalent to CLI excellence.

### VI. UV Package Manager Integration ✅ PASS

**Status**: Compliant - uses existing ai-agent environment

**Plan**:
- Add new dependencies to existing `ai-agent/pyproject.toml`
- Use UV for package management (existing ai-agent practice)
- Python 3.12+ requirement already established
- Development dependencies: pytest-asyncio, httpx for testing

**Summary**: 3 PASS | 2 NOT APPLICABLE (with justification)

**Violations Requiring Justification**: None - N/A items are justified by architectural context (backend API service vs original CLI application scope).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
ai-agent/                         # EXISTING: AI agent FastAPI application
├── src/
│   └── ai_agent/                # EXISTING: Main Python package
│       ├── __init__.py
│       ├── main.py              # EXISTING: FastAPI app
│       ├── api/                 # EXISTING: API routes
│       │   ├── __init__.py
│       │   ├── chat.py          # MODIFIED: /api/chat endpoint - integrate agent
│       │   ├── history.py       # EXISTING: Conversation history endpoints
│       │   ├── health.py        # EXISTING: Health check
│       │   └── deps.py          # EXISTING: Dependencies
│       ├── database/            # EXISTING: Database layer
│       │   ├── __init__.py
│       │   ├── models.py        # EXISTING: Conversation, Message from spec 007
│       │   └── connection.py    # EXISTING: DB connection
│       ├── services/            # EXISTING: Services
│       │   ├── __init__.py
│       │   └── auth.py          # EXISTING: Auth service
│       └── agent/               # NEW: OpenAI Agents SDK integration
│           ├── __init__.py
│           ├── config.py        # Agent configuration, Gemini API setup, RunConfig
│           ├── agent_service.py # Agent initialization, Runner orchestration
│           ├── mcp_connection.py# MCPServerStreamableHttp connection management
│           ├── context_manager.py# Message history loading, token counting, truncation
│           └── message_converter.py# Convert DB messages to agent format
├── tests/                       # EXISTING: Test directory
│   └── agent/                   # NEW: Agent tests
│       ├── contract/            # Agent initialization, MCP connection contracts
│       ├── integration/         # End-to-end agent workflows (mocked Gemini/MCP)
│       └── unit/                # Context management, message conversion, token counting
├── alembic/                     # EXISTING: DB migrations
└── pyproject.toml               # EXISTING: Dependencies (will add agent SDK deps)

mcp-server/                      # EXISTING: MCP server from spec 006 (no changes)
└── src/
    └── todo_mcp_server/
        └── server.py            # Provides list_tasks, create_task, etc.
```

**Structure Decision**: This feature adds a new `ai-agent/src/ai_agent/agent/` submodule to the existing ai-agent FastAPI application. The ai-agent application already contains the chat API (spec 007) and database models (Conversation, Message). The new agent module integrates OpenAI Agents SDK with Gemini and connects to the MCP server (spec 006) via MCPServerStreamableHttp. The `/api/chat` endpoint in `ai_agent/api/chat.py` will be enhanced to use the agent service.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations requiring justification. All constitution principles either PASS or are NOT APPLICABLE with clear architectural justification (backend API service vs original CLI application scope).

---

## Constitution Check Re-evaluation (Post-Design)

**Date**: 2025-12-20
**Phase**: After Phase 1 Design Completion

### Re-evaluation Summary

All constitution principles remain in compliance after detailed design phase. The planning artifacts (research.md, data-model.md, contracts/, quickstart.md) confirm the initial assessment:

**I. Test-First Development (TDD)** ✅ REMAINS COMPLIANT
- Quickstart.md provides detailed TDD workflow with Red-Green-Refactor examples for each component
- Contract tests defined in `contracts/agent_interfaces.py`
- Test strategy documented with 3-tier approach (contract/integration/unit)
- All test examples follow pytest-asyncio async patterns

**II. Clean Code & Simplicity** ✅ REMAINS COMPLIANT
- Research decisions favor simplicity (token truncation over summarization for MVP)
- Interfaces use single-purpose methods (IMessageConverter, IContextManager)
- No premature abstractions - each component has clear responsibility
- YAGNI applied (deferred streaming, summarization, multi-language support to future)

**III. Proper Project Structure** ✅ REMAINS COMPLIANT
- Structure documented in plan.md matches ai-agent/ layout from spec 007
- Clear module separation: ai_agent/agent/config.py, ai_agent/agent/agent_service.py, ai_agent/agent/context_manager.py, etc.
- Tests organized in ai-agent/tests/agent/{contract,integration,unit}/
- Dependencies added to ai-agent/pyproject.toml (not scattered)

**IV. In-Memory Data Storage** ⚠️ REMAINS NOT APPLICABLE
- Confirmed: Uses PostgreSQL from spec 007 (Conversation, Message models unchanged)
- data-model.md explicitly documents "No database schema changes"
- Runtime entities (AgentContext, AgentResult) are ephemeral in-memory only

**V. Command-Line Interface Excellence** ⚠️ REMAINS NOT APPLICABLE
- Confirmed: API-based service, not CLI
- API contract documented in contracts/api_schema.yaml (OpenAPI 3.0)
- User-friendly error messages defined (400/401/403/503 responses with clear messages)

**VI. UV Package Manager Integration** ✅ REMAINS COMPLIANT
- Quickstart.md uses `uv add` for dependency installation
- All test commands use `uv run pytest`
- Dependencies: openai-agents-python, openai, httpx, tiktoken, pytest-asyncio

**Conclusion**: NO constitution violations introduced by design phase. Ready for implementation following TDD workflow in quickstart.md.

---

## Phase 3 Implementation Learnings *(post-implementation)*

**Date**: 2025-12-21
**Phase**: After Phase 3 Completion (User Story 1 - Natural Language Task Management)

### OpenAI Agents SDK Integration Corrections

During phase 3 implementation and testing, several critical API details were discovered that differ from initial assumptions. These corrections are now incorporated into the codebase:

#### 1. Runner.run API Changes (openai-agents v0.6.4+)
**Initial Assumption**: `Runner.run(agent, user_message, messages=history, run_config=config)`
**Actual API**: `Runner.run(agent, input=messages, config=run_config)`

**Impact**:
- File: `ai-agent/src/ai_agent/agent/agent_service.py`
- Changed parameter names: `input` instead of `messages`, `config` instead of `run_config`
- Full conversation history passed as single `input` parameter (no separate user_message)

#### 2. RunResult Attribute Structure
**Initial Assumption**: `result.messages` contains responses, simple token counting
**Actual API**:
- `result.new_items` - list of `MessageOutputItem` objects (not `result.messages`)
- `result.context_wrapper.usage.total_tokens` - token usage (not manual counting)

**Impact**:
- File: `ai-agent/src/ai_agent/agent/agent_service.py`
- Updated `_extract_tool_calls()` to process `result.new_items`
- Token counting uses `result.context_wrapper.usage.total_tokens` directly
- Handle `MessageOutputItem` objects (attribute access) vs dictionaries (`.get()` access)

#### 3. MCP Server Adapter Requirements
**Initial Assumption**: MCP `ClientSession` can be passed directly to agent
**Actual Requirement**: Agent expects server object with `.name` and `.use_structured_content` attributes

**Impact**:
- File: `ai-agent/src/ai_agent/agent/mcp_connection.py`
- Created `MCPServerAdapter` wrapper class
- Added required attributes: `name` (string), `use_structured_content` (boolean)
- Adapted `list_tools()` and `call_tool()` methods to match SDK expectations

#### 4. ContextManager Parameter Naming
**Initial Assumption**: Database session parameter named `db`
**Actual Convention**: Parameter named `session` for SQLAlchemy async session consistency

**Impact**:
- File: `ai-agent/src/ai_agent/agent/context_manager.py`
- Changed method signature: `load_conversation_history(session, conversation_id, user_id)`
- File: `ai-agent/src/ai_agent/api/chat.py`
- Updated call site to use `session=db`

#### 5. MCP Connection Function Signature
**Initial Assumption**: `create_mcp_connection(user_id, config)`
**Actual Signature**: `create_mcp_connection(config, user_id)`

**Impact**:
- File: `ai-agent/src/ai_agent/agent/agent_service.py`
- Corrected argument order in async context manager usage

#### 6. Message Type Polymorphism
**Discovery**: Need to handle both dictionary messages (from database) and `MessageOutputItem` objects (from SDK)

**Impact**:
- Files: `ai-agent/src/ai_agent/agent/agent_service.py`
- Methods: `_extract_tool_calls()`, `_count_tokens()`
- Added type checking: `isinstance(message, dict)` vs attribute access
- Use `getattr()` for `MessageOutputItem` objects, `.get()` for dictionaries

#### 7. MessageConverter Input Format Detection
**Discovery**: Conversation history from `ContextManager` may already be in agent format (list of dicts)

**Impact**:
- File: `ai-agent/src/ai_agent/agent/agent_service.py`
- Method: `run_agent_with_context()`
- Added format detection: check if `conversation_history[0]` is already a dict
- Skip conversion if already in correct format

### Verification Status
**Date**: 2025-12-21
**Method**: E2E API testing
**Endpoint**: `POST /api/chat`
**Result**: ✅ PASS - Agent successfully initializes, connects to MCP, processes natural language, and executes tool calls

**Test Command**:
```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Timezone: America/New_York" \
  -d '{"message": "Hello, can you help me manage my tasks?"}'
```

### Documentation Updates
- [x] spec.md: Added "Integration Learnings" section with SDK API details
- [x] plan.md: This section documents implementation corrections
- [ ] tasks.md: Mark phase 3 tasks as complete with reference to learnings
- [ ] quickstart.md: Update code examples to match corrected API usage (if needed)

### Recommendations for Future Phases
1. **Type Safety**: Consider creating type stubs or protocol definitions for `MessageOutputItem`
2. **Testing**: Add integration tests for SDK API compatibility to catch future version changes
3. **Documentation**: Keep SDK version pinned in `pyproject.toml` and document upgrade checklist
4. **Error Handling**: Add specific exception handling for SDK-specific errors
5. **Monitoring**: Log SDK version and API call patterns for debugging
