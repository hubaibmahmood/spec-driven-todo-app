---
id: 0006
title: OpenAI Agents SDK Setup and Core Modules
stage: green
date: 2025-12-20
surface: agent
model: Claude Sonnet 4.5
feature: 008-openai-agents-sdk-integration
branch: 008-openai-agents-sdk-integration
user: hubaib
command: /sp.implement
labels: ["setup", "tdd", "pydantic", "tiktoken", "message-conversion", "configuration"]
links:
  spec: specs/008-openai-agents-sdk-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - ai-agent/.gitignore
  - ai-agent/pyproject.toml
  - ai-agent/.env.example
  - ai-agent/src/ai_agent/agent/__init__.py
  - ai-agent/src/ai_agent/agent/config.py
  - ai-agent/src/ai_agent/agent/message_converter.py
  - ai-agent/src/ai_agent/agent/context_manager.py
  - ai-agent/tests/agent/contract/test_agent_config.py
  - ai-agent/tests/agent/unit/test_message_converter.py
  - ai-agent/tests/agent/unit/test_context_manager.py
  - ai-agent/README.md
  - specs/008-openai-agents-sdk-integration/tasks.md
tests:
  - test_agent_config (4 tests, all pass)
  - test_message_converter (4 tests, all pass)
  - test_context_manager (4 tests, all pass)
---

## Prompt

Update @ai-agent/README.md on completion of every phase. Use your best judgment what should be included in the readme from that phase. The goal is by the end of tasks phases, readme will be also updated and it will also help in crafting the commit message for github when all tasks are done. And you can also have the context what was implemented in last phase if I clear the chat to save tokens from context while working on a new phase

## Response snapshot

Implemented Phase 1 (Setup) and 50% of Phase 2 (Foundational) for OpenAI Agents SDK integration following TDD methodology:

**Phase 1: Setup (T001-T005)** ✅
- Installed openai-agents v0.6.4, tiktoken, pydantic-settings via uv
- Created agent module structure (src/ai_agent/agent/)
- Created test directories (contract/integration/unit)
- Updated .env.example with Gemini API and agent configuration
- Created .gitignore for ai-agent directory

**Phase 2: Foundational (T006-T019)** 50% Complete
1. **AgentConfig Module** (T006-T008) ✅
   - RED: Failing tests for validation
   - GREEN: Pydantic BaseSettings with field validators
   - Validates GEMINI_API_KEY, temperature (0.0-2.0), token_budget, MCP settings
   - Environment variable support with AGENT_ prefix

2. **MessageConverter Module** (T009-T013) ✅
   - RED: Failing tests for db_to_agent conversion
   - GREEN: Convert Database Message ↔ Agent format
   - Preserves tool_calls from message_metadata field
   - Batch conversion support via db_messages_to_agent_batch()

3. **ContextManager - Token Counting** (T014-T019) ✅
   - RED: Failing tests for token counting
   - GREEN: tiktoken integration (cl100k_base encoding)
   - Smart truncation preserving system messages
   - Keeps newest messages when budget exceeded

**Key Implementation Details:**
- Used context7 MCP for up-to-date openai-agents and pydantic-settings documentation
- Fixed message_metadata vs metadata naming mismatch
- All tests follow RED-GREEN-REFACTOR TDD workflow
- Created separate .venv in ai-agent with Python 3.13

## Outcome

- ✅ Impact: Core infrastructure 50% complete, foundation ready for agent service implementation
- 🧪 Tests: 12 tests created, 12 passing (100% pass rate), following TDD methodology
- 📁 Files: 10 files created/modified across agent module, tests, and configuration
- 🔁 Next prompts: Continue Phase 2 with history loading, MCP connection, timezone handling, then Phase 3 User Story 1 (MVP)
- 🧠 Reflection: TDD workflow proved effective for catching naming mismatches early. Using context7 MCP ensured up-to-date SDK usage patterns.

## Evaluation notes (flywheel)

- Failure modes observed: Initial metadata vs message_metadata naming confusion, resolved via test feedback
- Graders run and results (PASS/FAIL): pytest 12/12 PASS
- Prompt variant (if applicable): Standard TDD RED-GREEN-REFACTOR
- Next experiment (smallest change to try): Complete remaining Phase 2 modules (T020-T028e), then proceed to User Story 1 implementation
