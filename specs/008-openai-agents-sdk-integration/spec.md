# Feature Specification: OpenAI Agents SDK Integration

**Feature Branch**: `008-openai-agents-sdk-integration`
**Created**: 2025-12-20
**Status**: Draft
**Input**: User description: "OK lets implement OpenAI Agents SDK integration."

## Context & Dependencies

**This feature extends spec 007 (Chat Persistence Service)** by adding OpenAI Agents SDK capabilities to create an intelligent conversational AI agent with persistent chat history.

### Relationship to Existing System

- **Builds on**: Spec 007 - Chat Persistence Service
- **Implementation Location**: `ai-agent/` directory (existing AI agent codebase)
- **Existing Infrastructure Used**:
  - **From Spec 007 (Chat Persistence)**:
    - Conversation and Message database models with PostgreSQL persistence
    - FastAPI chat endpoints: `POST /api/chat`, `GET /api/conversations`, `GET /api/conversations/{id}`
    - Better-auth session authentication
    - Message role structure (`user`, `assistant`, `tool`) and metadata field for tool calls
  - **From Spec 006 (MCP Server)**:
    - MCP server with task management tools
    - Existing MCP tools: `list_tasks`, `create_task`, `update_task`, `delete_task`, `mark_task_completed`
    - Service-to-service authentication with X-User-ID header propagation

### What This Feature Adds

This feature transforms the basic chat persistence system (spec 007) into an intelligent AI agent by integrating OpenAI Agents SDK with Gemini API:
- **OpenAI Agents SDK integration with Gemini** - Replace simple echo responses with intelligent AI-powered conversations using Gemini 2.5 Flash model via OpenAI-compatible endpoint
- **Natural language task management** - Use OpenAI agent to understand and execute task operations via natural language
- **Tool calling capabilities** - Enable agent to invoke MCP tools (from spec 006) to perform actual task operations
- **Multi-turn conversation context** - Leverage OpenAI's context management with persistent storage from spec 007
- **Intelligent parsing and validation** - Extract task attributes and validate user inputs before operations
- **Sophisticated dialogue handling** - Ask clarifying questions and handle ambiguous queries

**Architecture Flow**: User (frontend/CLI) → FastAPI `/api/chat` endpoint (spec 007) → [OpenAI Agent runs inside endpoint handler + MCPServerStreamableHttp connection] → MCP Server (spec 006) → FastAPI Backend → Database. All conversations persisted via spec 007's infrastructure. Agent is initialized with async MCPServerStreamableHttp context manager within the request/response cycle, connecting to MCP server with X-User-ID header for authenticated tool access.

## Clarifications

### Session 2025-12-20

- Q: What interface will users use to interact with the OpenAI agent? → A: Via existing FastAPI chat API endpoints (POST /api/chat) - frontend/CLI sends messages to backend, which communicates with OpenAI agent
- Q: Which OpenAI model should be used for the agent? → A: Custom setup using Gemini API (gemini-2.5-flash) with OpenAI Agents SDK via Google's OpenAI-compatible endpoint (https://generativelanguage.googleapis.com/v1beta/openai/). Uses GEMINI_API_KEY environment variable, AsyncOpenAI client with custom base_url, OpenAIChatCompletionsModel wrapper, and RunConfig with model provider.
- Q: Where will the OpenAI Agents SDK agent code run? → A: Inside the FastAPI /api/chat endpoint handler (agent initialized and runs within the endpoint request/response cycle)
- Q: How will the OpenAI Agent access the MCP tools? → A: Using OpenAI Agents SDK's built-in MCP support via MCPServerStreamableHttp class. Agent connects to MCP server (spec 006) with async context manager, passing X-User-ID header for service-to-service authentication. MCP server tools are automatically exposed to the agent.
- Q: How will conversation history be passed to the OpenAI Agent for multi-turn context? → A: Load messages from database via conversation_id (spec 007 persistence), convert to agent message format (user/assistant/tool roles), pass to Runner.run() as messages parameter. Allows filtering/truncation for token management.
- Q: Which context window management strategy should the system implement? → A: Token-based truncation - count tokens in message history, keep messages within token budget (e.g., 80% of model's context limit), truncate oldest messages first while preserving system prompts and recent context.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Management via OpenAI Agent (Priority: P1)

Users can interact with their todo tasks using natural language through an OpenAI-powered conversational agent, enabling intuitive task management without memorizing commands or navigating menus.

**Why this priority**: This is the core value proposition - enabling AI-driven natural language interaction. Without this, there's no integration to deliver. This story alone provides immediate value by letting users manage tasks conversationally.

**Independent Test**: Can be fully tested by sending natural language queries like "show my tasks", "add a task to buy groceries", or "mark task 5 as done" to the agent and verifying correct task operations occur.

**Acceptance Scenarios**:

1. **Given** a user authenticated with the todo system, **When** they ask the agent "what are my tasks?", **Then** the agent retrieves and displays all their tasks in a readable format
2. **Given** a user wants to add a task, **When** they tell the agent "add a task to call the dentist tomorrow with high priority", **Then** the agent creates a task with title "call the dentist", due date set to tomorrow, and priority "High"
3. **Given** a user has task ID 3, **When** they tell the agent "mark task 3 as complete", **Then** the agent marks the task as completed and confirms the action
4. **Given** a user wants to modify a task, **When** they say "update task 5 to change the title to 'finish report'", **Then** the agent updates the task title and confirms the change

---

### User Story 2 - Multi-Turn Conversation Context (Priority: P2)

Users can have natural, multi-turn conversations with the agent where context is maintained across messages, enabling follow-up questions and refinements without repeating information.

**Why this priority**: Enhances user experience significantly but requires the basic agent (P1) to be functional first. Multi-turn conversations make the interaction feel natural and human-like.

**Independent Test**: Can be tested by having a conversation like "show my urgent tasks" followed by "mark the first one as complete" - verifying the agent remembers which tasks were "urgent" from the previous message.

**Acceptance Scenarios**:

1. **Given** a user asked "show my high priority tasks", **When** they follow up with "delete the second one", **Then** the agent deletes the second task from the previously shown high priority tasks
2. **Given** a user is creating a task, **When** they say "add a task" then "title should be buy milk" then "make it urgent", **Then** the agent creates a single task combining all three messages
3. **Given** a user asked about tasks due today, **When** they ask "how many are there?", **Then** the agent responds with the count from the previous query without re-fetching

---

### User Story 3 - Intelligent Task Parsing and Validation (Priority: P2)

The agent intelligently parses natural language inputs to extract task attributes (title, description, priority, due date) and validates them before creating/updating tasks, providing helpful feedback for invalid inputs.

**Why this priority**: Improves accuracy and user trust but depends on basic agent functionality (P1). Prevents errors and reduces frustration from misunderstood commands.

**Independent Test**: Can be tested by providing ambiguous or invalid inputs like "add a task for next Fbruary 30th" and verifying the agent catches the invalid date and requests clarification.

**Acceptance Scenarios**:

1. **Given** a user says "add a task for next Wednesday to prepare presentation", **When** the agent processes this, **Then** it correctly calculates next Wednesday's date and creates the task with appropriate due date
2. **Given** a user provides an invalid date like "February 30th", **When** the agent tries to create the task, **Then** it detects the invalid date and asks for clarification
3. **Given** a user says "make a task with low priority", **When** no title is provided, **Then** the agent asks for the task title before proceeding
4. **Given** a user says "urgent task: finish report by EOD", **When** the agent parses this, **Then** it extracts priority "Urgent", title "finish report", and sets due date to end of current day

---

### User Story 4 - Batch Operations via Natural Language (Priority: P3)

Users can perform bulk operations on tasks using natural language, such as "mark all urgent tasks as complete" or "delete all completed tasks from last month".

**Why this priority**: Nice-to-have enhancement that improves efficiency for power users but not essential for MVP. Requires solid foundation from P1-P2 stories.

**Independent Test**: Can be tested by creating 5 urgent tasks, then saying "complete all urgent tasks" and verifying all 5 are marked as completed in one operation.

**Acceptance Scenarios**:

1. **Given** a user has 10 tasks with "High" priority, **When** they say "mark all high priority tasks as done", **Then** the agent marks all 10 tasks as completed
2. **Given** a user has 15 completed tasks, **When** they say "delete all completed tasks", **Then** the agent deletes all 15 tasks after confirming the action
3. **Given** a user has tasks from the past week, **When** they say "show me tasks I completed this week", **Then** the agent filters and displays only tasks completed within the current week

---

### Edge Cases

- What happens when the user's natural language query is ambiguous (e.g., "add a task for it tomorrow")? Agent should ask for clarification on what "it" refers to.
- How does the system handle authentication failures when the agent tries to access tasks? Agent should detect auth errors and guide user to re-authenticate.
- What happens when a user references a task ID that doesn't exist (e.g., "delete task 999")? Agent should return a helpful error message indicating the task was not found.
- How does the agent handle concurrent modifications (user updates task via CLI while agent is processing a command)? Agent should gracefully handle stale data and retry or notify user of conflict.
- What happens when Gemini API is down or rate-limited? System should provide fallback behavior or clear error messaging to the user.
- How does the agent handle very long conversation histories that exceed token limits? System implements token-based truncation: count tokens, maintain budget at 80% of model's limit, truncate oldest messages first while preserving system prompts.
- How does the system handle timezone for relative dates (e.g., "add task by tomorrow at 9pm")? Client sends X-Timezone header (auto-detected from browser/device with IANA timezone ID like "America/New_York"), agent uses this timezone for parsing relative dates and times, converts to UTC for storage. System falls back to UTC if header not provided and may ask user for timezone clarification.
- How does the system interpret "EOD" (End of Day) in natural language? Agent interprets EOD as 23:59:59 (end of calendar day) in user's timezone. COB (Close of Business) interprets as 17:00:00 in user's timezone. Agent confirms interpretation when ambiguous: "By EOD, I'll set the deadline to 11:59pm today. Is that correct?"
- How does the system handle week boundary references like "this week" or "next week"? Agent uses locale-based week start (Sunday for en-US, Monday for en-GB/ISO 8601 default). "This week" = current calendar week, "next week" = following calendar week, "business week" = Monday-Friday. Agent clarifies if ambiguous based on context.
- How does the agent resolve task references in multi-turn conversations (e.g., "mark the first one complete")? System stores displayed task list in conversation metadata (spec 007 Message.metadata field) with position-to-ID mapping. Ordinal references ("first", "second", "last") resolve against most recent display context. Context expires after 5 turns or 5 minutes. Agent asks for clarification if no valid context exists.
- How does the system normalize natural language priority expressions to API enum values? Agent uses priority mapping: "urgent/critical/asap" → Urgent, "high/important" → High, "normal/regular" → Medium (default), "low/whenever" → Low. Only valid enum values ("Urgent", "High", "Medium", "Low") are sent to MCP server. Agent validates and defaults to Medium if uncertain.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST integrate OpenAI Agents SDK with Gemini API (gemini-2.5-flash model via Google's OpenAI-compatible endpoint) to enable conversational AI capabilities for task management
- **FR-002**: System MUST provide natural language parsing to extract task attributes (title, description, priority, due_date) from user messages
- **FR-003**: System MUST support the following task operations via natural language: create, read, update, delete, and mark as completed
- **FR-004**: System MUST maintain conversation context across multiple turns by loading message history from database via conversation_id, converting to agent message format (user/assistant/tool roles), and passing to Runner.run() as messages parameter. This enables follow-up questions and references to previous context.
- **FR-005**: System MUST authenticate users and enforce task ownership (users can only access/modify their own tasks)
- **FR-006**: System MUST validate all task operations before execution and provide clear error messages for invalid inputs
- **FR-007**: System MUST handle ambiguous queries by asking clarifying questions before proceeding
- **FR-008**: System MUST integrate with spec 007's chat persistence infrastructure for conversation storage and spec 006's MCP server for task operations using MCPServerStreamableHttp with X-User-ID header authentication. MCP tools (list_tasks, create_task, update_task, delete_task, mark_task_completed) are automatically exposed to the agent via mcp_servers parameter.
- **FR-009**: System MUST support both interactive conversational mode (POST /api/chat with conversation_id to maintain context across turns) and single-query mode (POST /api/chat without conversation_id for one-off requests)
- **FR-010**: System MUST log all agent interactions for debugging and audit purposes
- **FR-011**: System MUST implement rate limiting and error handling for Gemini API calls (via OpenAI-compatible endpoint)
- **FR-012**: System MUST gracefully degrade when Gemini API is unavailable (provide clear error messages, not crash)
- **FR-013**: Agent responses MUST be formatted in a user-friendly, readable manner (use markdown, lists, tables where appropriate)
- **FR-014**: System MUST implement token-based context window management by counting tokens in message history and keeping messages within a token budget (e.g., 80% of gemini-2.5-flash's context limit). Truncate oldest messages first while always preserving system prompts and recent context. This prevents API errors from exceeding token limits.
- **FR-015**: System MUST provide configuration via environment variables (GEMINI_API_KEY) and code-level RunConfig for model (gemini-2.5-flash), temperature, and other parameters
- **FR-016**: System MUST accept X-Timezone header in ISO timezone format (IANA timezone identifiers such as "America/New_York", "Europe/London", "Asia/Tokyo") and use it for parsing relative dates and times in natural language queries. System MUST default to UTC if header not provided.
- **FR-017**: Agent MUST convert all parsed datetimes to UTC before sending to MCP server for task creation/updates, ensuring consistent storage regardless of user timezone. Agent MUST include timezone context in system prompt to enable accurate parsing of expressions like "tomorrow at 9pm".
- **FR-018**: System MUST interpret "EOD" (End of Day) as 23:59:59 in user's timezone and "COB" (Close of Business) as 17:00:00 in user's timezone. Agent MUST confirm interpretation when ambiguous and convert to UTC before storage.
- **FR-019**: System MUST handle week boundary references ("this week", "next week") using locale-based week start day (Sunday for en-US, Monday for en-GB/ISO 8601). Agent MUST use Accept-Language header or default to ISO 8601 (Monday start). System MUST clarify "business week" vs "calendar week" when context is ambiguous.
- **FR-020**: System MUST store displayed task lists in conversation metadata (spec 007 Message.metadata field) with position-to-ID mapping to enable ordinal reference resolution ("first one", "second task", "last one"). Context MUST expire after 5 conversational turns or 5 minutes. Agent MUST ask for clarification (task ID or title) when no valid display context exists.
- **FR-021**: System MUST normalize natural language priority expressions to valid API enum values before MCP calls. Agent MUST use defined mapping: "urgent/critical/asap" → "Urgent", "high/important" → "High", "normal/regular/medium" → "Medium", "low/whenever" → "Low". Agent MUST validate priority value and default to "Medium" if uncertain or invalid.

### Key Entities

- **Agent Session**: Represents a conversational session with the OpenAI agent initialized within the /api/chat endpoint handler. Includes conversation history loaded from database via conversation_id (spec 007), converted to agent message format and passed to Runner.run() as messages parameter, user authentication state (from request session used for X-User-ID header), and session metadata
- **Agent Message**: Individual messages in the conversation (user input or agent response), with role (user/assistant/system), content, timestamp, and token count
- **Task Operation Request**: Parsed natural language intent mapped to structured task operations (action type, target task ID or filters, task attributes to create/update)
- **Agent Configuration**: Settings for the OpenAI Agents SDK with Gemini backend including AsyncOpenAI client with custom base_url (Google's OpenAI-compatible endpoint), OpenAIChatCompletionsModel wrapper (gemini-2.5-flash), RunConfig with model provider, MCPServerStreamableHttp connection to MCP server with X-User-ID header, temperature, max tokens, and system prompts (MCP tools are automatically discovered and exposed)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully create, read, update, delete, and complete tasks using natural language commands with 95% accuracy for clear, unambiguous requests
- **SC-002**: Agent responds to user queries within 3 seconds for simple operations (single task retrieval) and within 10 seconds for complex operations (batch updates, filtering)
- **SC-003**: System maintains conversation context accurately across at least 10 turns without losing relevant information or misinterpreting references
- **SC-004**: Agent correctly parses and extracts task attributes (title, priority, due date) from natural language with 90% accuracy for common date/time formats
- **SC-005**: System handles Gemini API failures gracefully, providing clear error messages to users within 5 seconds of detecting the failure
- **SC-006**: Users can complete their task management workflow 50% faster using natural language compared to traditional CLI menu navigation
- **SC-007**: Agent asks clarifying questions for ambiguous queries in 100% of cases where confidence is below a defined threshold
- **SC-008**: System successfully authenticates users and enforces task ownership for 100% of operations (no unauthorized access)

## Integration Learnings *(post-implementation)*

### OpenAI Agents SDK v0.6.4+ Integration Details

The following integration details were discovered during phase 3 implementation and testing (December 2025). These learnings are critical for successful integration with the `openai-agents` SDK:

#### 1. Runner.run API Signature
- **SDK API**: `Runner.run(agent, input=messages, config=run_config)`
- **Key Points**:
  - Use `input=messages` parameter (not `messages=`)
  - Use `config` parameter (not `run_config`)
  - Pass full conversation history as `input` (includes user message)
  - No separate positional user_message argument needed

#### 2. RunResult Response Structure
- **Attributes**:
  - `result.new_items`: List of new message items (assistant responses, tool calls)
  - `result.context_wrapper.usage.total_tokens`: Token usage tracking
  - **Not available**: `result.messages` (does not exist)
- **Message Item Types**: Items in `new_items` are `MessageOutputItem` objects (not dictionaries)
  - Access via attributes: `item.role`, `item.content`, `item.tool_calls`
  - Cannot use dictionary methods (`.get()`, `[]` access)

#### 3. MCP Server Integration
- **SDK Requirement**: MCP server object must have `.name` attribute
- **Solution**: Create `MCPServerAdapter` wrapper class
  ```python
  class MCPServerAdapter:
      def __init__(self, session, name: str):
          self.session = session
          self.name = name
          self.use_structured_content = False  # Required by SDK
  ```
- **Required Attributes**:
  - `.name` (string): Server identifier
  - `.use_structured_content` (boolean): Content format flag

#### 4. ContextManager API Consistency
- **Method Signature**: `load_conversation_history(session, conversation_id, user_id)`
- **Key Point**: Parameter is `session` (not `db`) for consistency with SQLAlchemy async sessions

#### 5. MCP Connection Parameter Order
- **Correct Order**: `create_mcp_connection(config, user_id)`
- **Context Manager Usage**:
  ```python
  async with create_mcp_connection(self.config, user_id) as mcp_server:
      # Use mcp_server
  ```

#### 6. Message Type Handling (Mixed Formats)
- **Context**: Conversation history from database vs SDK responses
- **Solution**: Handle both dictionaries and `MessageOutputItem` objects:
  ```python
  if isinstance(message, dict):
      role = message.get("role")
  else:
      role = getattr(message, "role", None)
  ```
- **Use Cases**:
  - `_extract_tool_calls()`: Process tool calls from mixed message types
  - `_count_tokens()`: Token counting for hybrid message lists
  - Message format conversion for agent input

#### 7. MessageConverter Type Detection
- **Issue**: Conversation history may already be in agent format (list of dicts)
- **Solution**: Check format before conversion
  ```python
  if conversation_history and isinstance(conversation_history[0], dict):
      agent_messages = conversation_history  # Already converted
  else:
      converter = MessageConverter()
      agent_messages = converter.db_messages_to_agent_batch(conversation_history)
  ```

### Verification
These fixes were validated through successful E2E testing via:
```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-Timezone: America/New_York" \
  -d '{"message": "Hello, can you help me manage my tasks?"}'
```

**Status**: All phase 3 tests pass (agent initialization, MCP connection, natural language processing, tool execution)
