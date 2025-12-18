# FastAPI-to-MCP Skill Updates

## Version 2.1 - Production Templates & Documentation (2025-01-18)

This update adds production-ready templates and comprehensive documentation based on successful Spec 006 implementation (MCP Server Integration for Todo App).

### 🆕 New Templates

#### 1. **server.py.template** (Production Server Entry Point)

Modern server structure with direct tool registration:

**Key Features**:
- Direct tool import and registration (no register_tools() wrapper)
- Structured logging configuration
- Clear separation of concerns
- FastMCP best practices

**Replaces**: Old main.py template for Pattern 4

#### 2. **tool_file.template** (Individual Tool Files)

Comprehensive template for standalone tool files:

**Features**:
- Context-based user extraction (`ctx: Context`)
- Complete error handling (7 error types)
- Structured logging with audit fields
- AI-friendly error messages with suggestions
- Comprehensive docstrings with examples
- Finally block for resource cleanup

**Benefits over monolithic tools.py**:
- Each tool is independently testable
- Easier to maintain and review
- Clear boundaries between tools
- Better for teams (reduced merge conflicts)

#### 3. **schemas.template** (Pydantic Schemas Module)

Centralized schema definitions:

**Includes**:
- Enum definitions
- Response models
- Parameter models
- ErrorResponse with suggestions
- ValidationErrorDetail for field-level errors
- ERROR_TYPES taxonomy
- Comprehensive examples

**Benefits**:
- Type safety across tools
- Reusable validation logic
- Clear API contracts
- Better IDE support

#### 4. **SECURITY_REVIEW.template.md** (Security Audit Template)

Production security checklist:

**Sections**:
- Constant-time comparison verification
- Token logging prevention check
- Token storage validation
- Audit logging compliance
- Positive findings
- Recommendations
- Compliance summary

**Usage**: Generated after skill execution for security sign-off

### 📚 New Documentation

#### SKILL_IMPROVEMENTS_FROM_006.md

Comprehensive analysis of production learnings:

**Contents**:
- 10 key learnings from Spec 006 implementation
- Comparison: current skill vs production patterns
- Detailed recommendations for each improvement
- Implementation priority guide
- Success metrics for updated skill

**Covers**:
1. Modular tool structure
2. Dedicated schemas module
3. AI-friendly error taxonomy
4. Context-based user extraction
5. Direct tool registration
6. Documentation suite (5 guides)
7. Integration test structure
8. Logging best practices
9. Security checklist
10. E2E testing guide

### 🔧 Template Updates

#### Updated Structure for Pattern 4

**Before (v2.0)**:
```
mcp-server/
├── main.py              # Monolithic
├── tools.py             # All tools in one file
├── client.py
└── config.py
```

**After (v2.1)**:
```
mcp-server/
├── src/
│   ├── server.py          # NEW: Entry point
│   ├── client.py          # Enhanced with retry
│   ├── config.py          # Pydantic settings
│   ├── tools/             # NEW: Modular
│   │   ├── list_{entity}.py
│   │   ├── create_{entity}.py
│   │   ├── update_{entity}.py
│   │   ├── mark_completed.py
│   │   └── delete_{entity}.py
│   └── schemas/           # NEW: Centralized
│       └── {entity}.py
└── tests/
    ├── contract/          # Schema validation
    ├── unit/              # Component tests
    └── integration/       # E2E workflows
```

### 🎯 Error Handling Improvements

#### V2.0 Error Response
```python
return {"error": "Not found", "status_code": 404}
```

#### V2.1 Error Response
```python
return ErrorResponse(
    error_type="not_found_error",
    message="Task not found with ID: 123",
    details={"task_id": 123, "user_id": "user_123"},
    suggestions=[
        "Verify the task ID is correct",
        "Use list_tasks to see available tasks",
        "Check that the task belongs to your account"
    ]
).model_dump()
```

**Benefits**:
- AI can explain error clearly to user
- Actionable suggestions for resolution
- Structured for programmatic handling
- Consistent format across all tools

### 📊 Documentation Suite

New templates for production deployment:

1. **SECURITY_REVIEW.md** - Security audit checklist
2. **CLAUDE_DESKTOP_SETUP.md** - E2E integration guide
3. **E2E_SMOKE_TEST.md** - Manual testing guide (14 tests)
4. **SUCCESS_CRITERIA_VERIFICATION.md** - Validation checklist
5. **IMPLEMENTATION_SUMMARY.md** - Overview document

### 🧪 Testing Enhancements

#### Test Organization

**V2.0**: Simple `tests/` directory
**V2.1**: Structured by test type

```
tests/
├── conftest.py           # Shared fixtures
├── contract/             # Schema validation
│   └── test_{entity}_schemas.py
├── unit/                 # Component tests
│   ├── test_client.py
│   └── test_config.py
└── integration/          # E2E workflows
    ├── test_user_context.py
    ├── test_workflows.py
    ├── test_list_{entity}.py
    └── test_create_{entity}.py
```

### 🔐 Security Template Features

**SECURITY_REVIEW.template.md** validates:

1. ✅ Constant-time token comparison (`hmac.compare_digest`)
2. ✅ No token logging (grep verification)
3. ✅ Environment-only storage (no hardcoding)
4. ✅ Comprehensive audit logging
5. ✅ Input validation (Pydantic)
6. ✅ Error sanitization

**Auto-generated** after skill execution with:
- Line number references
- Code snippets
- Verification commands
- Compliance summary

### 📈 Production Validation

**Tested on Spec 006 (Todo App MCP Server)**:

**Architecture**:
- Pattern 4 (service-to-service auth)
- 5 MCP tools
- Modular structure
- Complete test suite
- E2E validated with Claude Desktop

**Results**:
- ✅ All 11 success criteria met
- ✅ Security review passed
- ✅ E2E tests successful
- ✅ <2s operation latency
- ✅ 100% data isolation
- ✅ Production-ready

### 🚀 Migration from V2.0 to V2.1

**If you generated MCP server with V2.0**:

1. **Restructure tools** (optional, recommended for 5+ tools):
   ```bash
   mkdir -p src/tools src/schemas
   # Move each tool to separate file
   ```

2. **Add schemas module**:
   ```bash
   # Copy schemas.template and populate
   ```

3. **Update error handling**:
   ```bash
   # Add ErrorResponse model
   # Update all error returns
   ```

4. **Add documentation**:
   ```bash
   # Generate security review
   # Add E2E test guide
   ```

**Or**: Regenerate with updated skill (recommended)

### 💡 Key Improvements Summary

| Aspect | V2.0 | V2.1 |
|--------|------|------|
| **Structure** | Monolithic tools.py | Modular src/tools/ |
| **Schemas** | Inline | Dedicated module |
| **Errors** | Simple dict | Structured taxonomy |
| **Context** | user_id param | FastMCP Context |
| **Registration** | register_tools() | Direct in server.py |
| **Docs** | README only | 5-doc suite |
| **Tests** | Basic | Contract/unit/integration |
| **Security** | Implicit | Explicit review checklist |

### 🎓 Learning Sources

Based on production implementation:
- **Spec 006**: MCP Server Integration
- **Duration**: 8 phases, 59 tasks
- **Testing**: TDD approach, comprehensive suite
- **Documentation**: Security review, E2E guide, setup docs
- **Validation**: Claude Desktop integration, manual E2E testing

### 📦 No New Dependencies

V2.1 is a **template and documentation update**. No new runtime dependencies required beyond V2.0.

### ⚡ Quick Start with V2.1

```python
# Skill automatically detects Pattern 4 and asks:
# "Use production structure with modular tools?" -> YES

# Generates:
# - src/server.py (direct registration)
# - src/tools/*.py (one per tool)
# - src/schemas/{entity}.py (centralized)
# - tests/ (contract/unit/integration)
# - SECURITY_REVIEW.md
# - CLAUDE_DESKTOP_SETUP.md
# - E2E_SMOKE_TEST.md

cd mcp-server
uv sync
pytest tests/contract/  # Schema validation
pytest tests/unit/      # Component tests
pytest tests/integration/  # E2E workflows
```

### 🔮 Future Enhancements (V2.2)

Planned additions:
- [ ] CLI generator for adding new tools to existing server
- [ ] OpenAPI schema diffing (detect backend changes)
- [ ] Performance benchmark templates
- [ ] Load testing templates
- [ ] Monitoring/metrics templates (Prometheus)

### 📝 Backward Compatibility

**100% backward compatible**:
- V2.0 templates still available
- Use V2.1 for Pattern 4 or 5+ tools
- Use V2.0 for simple cases (< 5 tools)

**Selection Logic**:
```python
if pattern == "service-to-service" or tool_count >= 5:
    use_v2_1_structure()  # Modular
else:
    use_v2_0_structure()  # Monolithic
```

---

**Questions?** See SKILL_IMPROVEMENTS_FROM_006.md for detailed analysis.

**Contributing?** New templates and patterns welcome!

## Version 2.0 - Microservices Support (2025-12-18)

This update adds comprehensive microservices patterns based on real-world implementation of an MCP server for a production FastAPI todo application.

### 🆕 New Features

#### 1. **Pattern 4: Service-to-Service Authentication**

Added enterprise-grade authentication pattern for microservices architectures:

- **Dual Authentication**: Service identity + user context propagation
- **Security**: SERVICE_AUTH_TOKEN (32+ chars) + constant-time comparison
- **Data Isolation**: Backend enforces user-level permissions
- **Headers**: `Authorization: Bearer {token}` + `X-User-ID: {user_id}`

**File**: `MICROSERVICES_PATTERNS.md` (NEW)

**When to use**:
- ✅ MCP server as separate microservice
- ✅ Security-critical systems
- ✅ Multi-tenant with strict data isolation
- ✅ Production deployments

#### 2. **Advanced Retry Logic**

Implemented production-ready retry with exponential backoff:

- **Library**: Tenacity-based retry decorator
- **Strategy**: 3 attempts (initial + 2 retries)
- **Backoff**: Exponential (1s → 2s)
- **Selective**: Only retries on timeout/connection errors
- **Logging**: Structured logging for all attempts

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=2),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
)
```

#### 3. **AI-Friendly Error Taxonomy**

7-type error classification with actionable messages:

| Error Type | Backend Status | AI Message |
|------------|----------------|------------|
| `authentication_error` | 401 | "Unable to authenticate. Check SERVICE_AUTH_TOKEN" |
| `authorization_error` | 403 | "You don't have permission to access this resource" |
| `not_found_error` | 404 | "Task not found or doesn't belong to you" |
| `validation_error` | 422 | "Invalid input: {field-level details}" |
| `backend_error` | 500 | "Backend service unavailable. Try again later" |
| `timeout_error` | Timeout | "Request timed out after 30s" |
| `connection_error` | Connection | "Unable to connect to backend" |

#### 4. **Structured Logging**

Production-grade logging with all required fields:

```python
logger.info(
    "Backend API call completed",
    extra={
        "timestamp": "2025-12-18T10:30:45.123Z",
        "endpoint": "/tasks",
        "method": "GET",
        "status_code": 200,
        "user_id": "user_123",
        "duration_ms": 145.2,
    }
)
```

#### 5. **Enhanced Project Structure**

Added **Option B: Structured (Microservices)** for better maintainability:

```
mcp-server/
├── src/                    # NEW: Source subdirectory
│   ├── server.py
│   ├── config.py
│   ├── client.py
│   ├── tools/              # NEW: Separate file per tool
│   │   ├── list_tasks.py
│   │   ├── create_task.py
│   │   └── ...
│   └── schemas/            # NEW: Centralized schemas
│       └── task.py
└── tests/
    ├── contract/           # NEW: Schema validation tests
    ├── unit/               # NEW: Component tests
    └── integration/        # NEW: E2E tests
```

**Benefits**:
- Each tool in separate file (easier maintenance)
- Clear test organization (contract/unit/integration)
- Better separation of concerns
- Scales to 10+ tools without becoming monolithic

#### 6. **Backend Modification Templates**

Automatic generation of backend dual authentication:

**Generated Code**:
- `backend/src/api/dependencies.py::get_current_user_or_service()`
- `backend/src/config.py::SERVICE_AUTH_TOKEN` field
- Constant-time token comparison with `hmac.compare_digest()`
- X-User-ID header validation

### 📝 Updated Documentation

#### Enhanced SKILL.md

- Added authentication pattern comparison table
- Added Pattern 4 with complete examples
- Added project structure options (A vs B)
- Added pattern selection flowchart
- Updated dependencies (added `tenacity`)
- Enhanced checklist with Pattern 4 specifics

#### New MICROSERVICES_PATTERNS.md

Comprehensive guide covering:
- Architecture diagrams
- Step-by-step implementation
- Complete code examples
- Security checklist
- Testing strategy
- When (and when NOT) to use Pattern 4

#### Updated README.md

Enhanced with:
- Pattern 4 quick reference
- Service token generation instructions
- Backend modification guide

### 🔄 Migration Guide

#### From Pattern 1/2/3 to Pattern 4

If you have an existing MCP server using simple auth patterns:

1. **Generate SERVICE_AUTH_TOKEN**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update MCP Server**:
   - Add token to `mcp-server/.env`
   - Update `client.py` to use `_build_headers()` with service auth
   - Add retry logic with tenacity
   - Implement error taxonomy

3. **Update Backend**:
   - Add `SERVICE_AUTH_TOKEN` to `backend/src/config.py`
   - Create `get_current_user_or_service()` in `dependencies.py`
   - Update all endpoints from `Depends(get_current_user)` to `Depends(get_current_user_or_service)`

4. **Add Tests**:
   - Create service auth fixtures
   - Add integration tests for dual auth
   - Verify data isolation

See `MICROSERVICES_PATTERNS.md` for complete migration guide.

### 🎯 Use Cases

**Pattern 4 is ideal for**:

1. **Multi-Tenant SaaS**: Strict data isolation requirements
2. **Enterprise Systems**: Audit logging and security compliance
3. **Microservices**: MCP server as separate deployable service
4. **Production Deployments**: Reliability and error handling critical

**Still use Pattern 1/2/3 for**:

- Quick prototypes
- Single-service applications
- Development/testing environments
- Simple integrations without strict security requirements

### 📊 Real-World Validation

These patterns are based on actual implementation of:

- **Project**: Todo App MCP Server
- **Architecture**: Microservices (Node.js auth-server, Python FastAPI backend, Python MCP server, React frontend)
- **Database**: Neon PostgreSQL (shared between services)
- **Scale**: 5 MCP tools, dual authentication, test-driven development

**Results**:
- ✅ 100% data isolation (users cannot access each other's tasks)
- ✅ <2s latency per operation
- ✅ Supports 100 concurrent requests
- ✅ Secure service-to-service communication
- ✅ Production-ready error handling

### 🔐 Security Enhancements

1. **Constant-Time Token Comparison**: Prevents timing attacks
2. **Token Length Requirements**: Minimum 32 characters
3. **No Token Logging**: Never log SERVICE_AUTH_TOKEN
4. **Environment-Only Storage**: Tokens only in `.env` files
5. **Request Auditing**: Log user_id and endpoint for every request

### 🧪 Testing Improvements

Enhanced test organization:

- **Contract Tests**: Validate Pydantic schemas match API contracts
- **Unit Tests**: Test isolated components (client, config, auth)
- **Integration Tests**: End-to-end flows with real backend

**New Fixtures**:
- `test_service_token`: Mock SERVICE_AUTH_TOKEN
- `test_service_auth_headers`: Pre-built auth headers
- `mock_backend_client`: Mocked BackendClient for unit tests

### 📦 Dependencies Added

```toml
tenacity>=8.0.0  # Retry logic with exponential backoff
```

### ⚠️ Breaking Changes

None! Pattern 4 is **additive** - existing Patterns 1/2/3 remain unchanged.

### 🚀 Quick Start with Pattern 4

```python
# 1. Invoke skill with microservices flag
# The skill will ask: "Is this a microservices architecture?"
# Answer: "Yes"

# 2. Skill automatically:
# - Generates SERVICE_AUTH_TOKEN
# - Creates structured project (Option B)
# - Generates backend modifications
# - Sets up retry logic and error handling
# - Creates comprehensive tests

# 3. Review and run:
cd mcp-server
uv sync
pytest tests/
uv run python -m src.server
```

### 📚 Additional Resources

- **MICROSERVICES_PATTERNS.md**: Complete implementation guide
- **SKILL.md**: Updated with Pattern 4 examples
- **MCP_REFERENCE.md**: MCP SDK reference (unchanged)
- **FASTAPI_PATTERNS.md**: FastAPI integration patterns (unchanged)

### 🎉 Credits

Patterns and implementations validated by:
- Real-world production deployment
- Test-driven development approach
- Security best practices (OWASP, constant-time comparison)
- Spec-Kit Plus constitution compliance

### 🔮 Future Enhancements

Planned for v2.1:
- [ ] Template system for custom tool transformations
- [ ] OpenTelemetry integration for distributed tracing
- [ ] Circuit breaker pattern for backend failures
- [ ] Rate limiting support
- [ ] Metrics collection (Prometheus format)

---

**Questions or issues?** See troubleshooting in `MICROSERVICES_PATTERNS.md` or file an issue.

**Want to contribute?** Patterns welcome! Follow the structure in `MICROSERVICES_PATTERNS.md`.
