---
id: 0002
title: OpenAI Agents SDK Integration Planning
stage: plan
date: 2025-12-20
surface: agent
model: claude-sonnet-4.5
feature: 008-openai-agents-sdk-integration
branch: 008-openai-agents-sdk-integration
user: developer
command: /sp.plan
labels: ["planning", "openai-agents-sdk", "gemini-api", "mcp-integration", "tdd"]
links:
  spec: ./specs/008-openai-agents-sdk-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-openai-agents-sdk-integration/plan.md
  - specs/008-openai-agents-sdk-integration/research.md
  - specs/008-openai-agents-sdk-integration/data-model.md
  - specs/008-openai-agents-sdk-integration/quickstart.md
  - specs/008-openai-agents-sdk-integration/contracts/agent_interfaces.py
  - specs/008-openai-agents-sdk-integration/contracts/api_schema.yaml
  - specs/008-openai-agents-sdk-integration/contracts/README.md
  - CLAUDE.md
tests:
  - None (planning phase - tests defined in contracts and quickstart)
---

## Prompt

Create: architecture sketch, section structure, research approach, quality validation.
Decisions needing documentation: list important choices with options and tradeoffs.
Testing strategy: validation checks based on acceptance criteria

User input context: User requested planning for OpenAI Agents SDK integration feature (spec 008) with focus on architecture, research, and testing strategy.

## Response snapshot

**Planning Complete for Feature 008: OpenAI Agents SDK Integration**

Successfully completed comprehensive planning workflow following `/sp.plan` command structure:

**Phase 0 - Research & Technical Decisions (research.md)**:
- Documented 8 key technical decisions with rationale and alternatives
- OpenAI Agents SDK with Gemini 2.5 Flash via OpenAI-compatible endpoint
- MCPServerStreamableHttp for MCP server connection with X-User-ID auth
- Token-based truncation strategy (tiktoken, 80% budget) for context window management
- Message format conversion between DB models and agent format
- Integration with existing `/api/chat` endpoint from spec 007
- 3-tier testing strategy (contract/integration/unit)
- Layered error handling with specific user-facing messages
- Pydantic BaseSettings for configuration management

**Phase 1 - Design & Contracts**:
- data-model.md: Documented runtime entities (AgentConfig, AgentMessage, AgentContext, AgentResult) and relationships to existing DB models from spec 007
- contracts/agent_interfaces.py: Python interface contracts using ABC and Protocol for all components (IAgentService, IContextManager, IMessageConverter, IMCPConnection)
- contracts/api_schema.yaml: OpenAPI 3.0 specification for enhanced `/api/chat` endpoint with agent integration
- contracts/README.md: Contract testing strategy and validation rules
- quickstart.md: Step-by-step TDD implementation guide with Red-Green-Refactor examples for each component

**Constitution Check**:
- Initial: 3 PASS, 2 NOT APPLICABLE (justified by architectural context)
- Re-evaluation post-design: All principles remain compliant
- No violations introduced by design phase

**Architecture Summary**:
- Backend extension adding `backend/src/agent/` module
- 6 key components: AgentConfig, MessageConverter, ContextManager, MCPConnection, AgentService, Enhanced ChatEndpoint
- Integrates with existing FastAPI backend (spec 003), chat persistence (spec 007), and MCP server (spec 006)
- No database schema changes - uses existing Conversation/Message models

**Key Design Decisions**:
1. Agent runs inside `/api/chat` endpoint handler (synchronous integration)
2. Gemini 2.5 Flash via Google's OpenAI-compatible endpoint (cost-effective)
3. Token-based truncation at 80% of context limit (industry standard)
4. MCPServerStreamableHttp with X-User-ID header (service-to-service auth)
5. Explicit message format conversion (type safety)
6. 3-tier testing with mocked external services (TDD-compliant)

**Testing Strategy Documented**:
- Contract tests: Interface compliance verification
- Integration tests: Component interaction with mocked Gemini API and MCP server
- Unit tests: Business logic isolation (token counting, message conversion)
- API tests: HTTP endpoint behavior and error handling
- All tests use pytest-asyncio for async support

## Outcome

- ✅ Impact: Comprehensive planning artifacts generated for OpenAI Agents SDK integration. All technical decisions documented with rationale. TDD implementation path clearly defined in quickstart.md.
- 🧪 Tests: No tests executed (planning phase). Test strategy and contracts defined for implementation phase.
- 📁 Files: 7 files created/modified (plan.md, research.md, data-model.md, quickstart.md, contracts/, CLAUDE.md)
- 🔁 Next prompts: Run `/sp.tasks` to generate detailed task breakdown from plan.md. Then begin TDD implementation following quickstart.md workflow.
- 🧠 Reflection: Planning workflow successfully completed all phases (Technical Context, Constitution Check, Phase 0 Research, Phase 1 Design). All constitution principles remain compliant after design phase. Ready for task generation and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Planning workflow executed successfully without errors or blockers.
- Graders run and results (PASS/FAIL): Constitution Check PASS (3 PASS, 2 N/A justified), Re-evaluation PASS (no violations introduced)
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Proceed with /sp.tasks command to generate implementation tasks based on planning artifacts
