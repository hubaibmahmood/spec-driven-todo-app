# FastAPI-to-MCP Quick Reference for Agents

## Decision Tree: Which Pattern?

```
START
  │
  ├─ Microservices? (MCP server = separate service)
  │   YES → Pattern 4 (Service-to-Service) ⭐ PRODUCTION
  │   NO ↓
  │
  ├─ Modern SPA with JWT?
  │   YES → Pattern 3 (JWT Bearer)
  │   NO ↓
  │
  ├─ Traditional web app with sessions?
  │   YES → Pattern 2 (Session-Based)
  │   NO ↓
  │
  └─ Simple app or prototype?
      YES → Pattern 1 (user_id Parameter)
```

## Pattern 4: Service-to-Service (Most Common for MCP)

### When Agent Should Use This

**Keywords in user request**:
- "microservices"
- "separate service"
- "production"
- "secure"
- "service-to-service"
- "authentication between services"
- "data isolation"

**Architecture indicators**:
- ✅ MCP server in separate `mcp-server/` directory
- ✅ Backend already exists (`backend/` or `api/`)
- ✅ Multiple services mentioned
- ✅ Security requirements mentioned

### Agent Implementation Checklist

**Phase 1: MCP Server Setup**
```bash
# 1. Create structure
mkdir -p mcp-server/src/tools mcp-server/src/schemas mcp-server/tests/{contract,unit,integration}

# 2. Generate token
python -c "import secrets; print(secrets.token_urlsafe(32))"
# → Save this token!

# 3. Initialize project
cd mcp-server && uv init --package .
```

**Phase 2: Generate Files**

Create in this order:

1. **mcp-server/pyproject.toml**
   ```toml
   dependencies = [
       "fastmcp>=0.5.0",
       "httpx>=0.27.0",
       "pydantic>=2.0.0",
       "pydantic-settings>=2.0.0",
       "python-dotenv>=1.0.0",
       "tenacity>=8.0.0",  # Critical for Pattern 4!
   ]
   ```

2. **mcp-server/src/config.py** (Settings with service_auth_token)

3. **mcp-server/src/schemas/task.py** (All Pydantic schemas + ERROR_TYPES)

4. **mcp-server/src/client.py** (BackendClient with @retry decorator)

5. **mcp-server/src/tools/list_tasks.py** (etc. - one per tool)

6. **mcp-server/src/server.py** (FastMCP entry point)

**Phase 3: Backend Modifications** ⚠️ CRITICAL

1. **backend/src/config.py**:
   ```python
   SERVICE_AUTH_TOKEN: str = ""
   ```

2. **backend/src/api/dependencies.py**:
   - Add `import hmac`
   - Create `get_current_user_or_service()` function
   - Use `hmac.compare_digest()` for token comparison

3. **backend/src/api/routers/tasks.py**:
   - Change ALL endpoints from `Depends(get_current_user)` to `Depends(get_current_user_or_service)`

**Phase 4: Configuration**

1. **mcp-server/.env**:
   ```env
   SERVICE_AUTH_TOKEN=<generated-token>
   FASTAPI_BASE_URL=http://localhost:8000
   ```

2. **backend/.env**:
   ```env
   SERVICE_AUTH_TOKEN=<same-token-as-above>
   ```

### Code Templates

#### BackendClient with Retry (copy-paste ready)

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=2),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    reraise=True,
)
async def _request(self, method, endpoint, user_id, json=None):
    headers = self._build_headers(user_id)
    response = await self.client.request(method, endpoint, headers=headers, json=json)
    # Add logging here
    return response
```

#### Error Translation (copy-paste ready)

```python
ERROR_TYPES = {
    "authentication_error": "Service authentication failed",
    "authorization_error": "User not authorized to access this resource",
    "not_found_error": "Requested resource not found",
    "validation_error": "Input validation failed",
    "backend_error": "Backend service error",
    "timeout_error": "Request timed out",
    "connection_error": "Unable to connect to backend service",
}

# In tool:
try:
    response = await client.get_tasks(user_id)
    if response.status_code == 200:
        return {"tasks": response.json(), "status": "success"}
    elif response.status_code == 401:
        return {"error_type": "authentication_error", "message": "..."}
except httpx.TimeoutException:
    return {"error_type": "timeout_error", "message": "..."}
```

#### Dual Auth Dependency (copy-paste ready)

```python
async def get_current_user_or_service(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    db: AsyncSession = Depends(get_db),
) -> str:
    # Service auth (MCP)
    if x_user_id is not None:
        token = credentials.credentials
        if not hmac.compare_digest(token, settings.SERVICE_AUTH_TOKEN):
            raise HTTPException(401, "Invalid service token")
        return x_user_id

    # User session (frontend)
    user_id = await validate_session(credentials.credentials, db)
    if not user_id:
        raise HTTPException(401, "Invalid session")
    return user_id
```

## Common Mistakes to Avoid

### ❌ DON'T:
1. **Forget tenacity dependency** → Retry logic won't work
2. **Skip backend modifications** → Authentication will fail
3. **Use simple string comparison** → Security vulnerability
4. **Log SERVICE_AUTH_TOKEN** → Security breach
5. **Generate short tokens (<32 chars)** → Weak security
6. **Forget X-User-ID header** → Backend can't identify user
7. **Use same dependency for MCP and frontend** → Dual auth breaks

### ✅ DO:
1. **Use `hmac.compare_digest()`** for token comparison
2. **Add retry logic with tenacity** for reliability
3. **Implement error taxonomy** for AI-friendly errors
4. **Structure project with src/ and tests/** for maintainability
5. **Create separate tool files** (not monolithic tools.py)
6. **Add structured logging** with all required fields
7. **Test dual authentication** (both service and user flows)

## Testing Requirements

### Minimum Tests for Pattern 4

**Contract Tests** (mcp-server/tests/contract/):
- Validate all Pydantic schemas
- Test error response structures

**Unit Tests** (mcp-server/tests/unit/):
- `test_client.py`: BackendClient, retry logic, headers
- `test_config.py`: Settings validation

**Integration Tests** (mcp-server/tests/integration/):
- `test_service_auth.py`: Service token validation
- `test_<tool>.py`: Each tool end-to-end

**Backend Tests** (backend/tests/):
- Service auth with valid token
- Service auth with invalid token
- X-User-ID missing
- Data isolation (user A can't access user B's data)

## File Size Expectations

Pattern 4 typical file sizes (for reference):

| File | Lines | Complexity |
|------|-------|------------|
| `config.py` | 20-30 | Simple |
| `schemas/task.py` | 100-150 | Medium |
| `client.py` | 150-200 | Complex |
| Each tool | 50-80 | Simple |
| `server.py` | 30-50 | Simple |
| Backend `dependencies.py` addition | 80-100 | Medium |

## Time Estimates

**For agent generating Pattern 4**:

- Discovery & analysis: 2-3 minutes
- MCP server generation: 5-7 minutes
- Backend modifications: 3-5 minutes
- Test scaffolding: 3-4 minutes
- **Total: 13-19 minutes**

**For user completing**:

- Review generated code: 5-10 minutes
- Run tests & fix issues: 10-15 minutes
- Manual E2E testing: 5-10 minutes
- **Total: 20-35 minutes**

## Validation Checklist for Agent

Before marking task complete, verify:

```
[ ] SERVICE_AUTH_TOKEN in both .env files (same value)
[ ] tenacity in pyproject.toml dependencies
[ ] @retry decorator on _request() method
[ ] hmac.compare_digest() used (not ==)
[ ] X-User-ID in header names (exact capitalization)
[ ] get_current_user_or_service() in backend
[ ] All endpoints updated to use dual auth
[ ] ERROR_TYPES dict with 7 error types
[ ] Structured logging with timestamp, endpoint, user_id, duration_ms
[ ] Test fixtures for service auth in both projects
[ ] README mentions Pattern 4 and backend modifications
```

## Quick Debugging

### "401 Unauthorized"
→ Check SERVICE_AUTH_TOKEN matches in both .env files

### "400 Bad Request"
→ X-User-ID header missing or misspelled (case-sensitive!)

### "No retry happening"
→ Missing `tenacity` dependency or `@retry` decorator

### "Timing attack vulnerability"
→ Using `==` instead of `hmac.compare_digest()`

### "Backend doesn't recognize MCP requests"
→ Endpoints not updated to use `get_current_user_or_service`

## Success Indicators

**MCP server working**:
```bash
cd mcp-server
uv run python -m src.server
# Should start without errors
```

**Backend accepting service auth**:
```bash
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer <SERVICE_AUTH_TOKEN>" \
  -H "X-User-ID: test_user_123"
# Should return tasks for user
```

**End-to-end test**:
```bash
cd mcp-server
pytest tests/integration/test_list_tasks.py -v
# Should pass
```

## Resources

- **Full Guide**: MICROSERVICES_PATTERNS.md
- **Examples**: Review our implementation in Phases 1-2
- **Updates**: See UPDATES.md for v2.0 changes
- **Skill Docs**: SKILL.md for all 4 patterns

---

**Quick Tip**: When in doubt, use Pattern 4 for any production MCP server. It's more initial work but provides proper security and maintainability.
