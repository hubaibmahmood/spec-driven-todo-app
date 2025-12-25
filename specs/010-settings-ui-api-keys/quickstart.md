# Quickstart Guide: Settings UI for API Key Management

**Feature**: 010-settings-ui-api-keys
**Date**: 2025-12-24
**Target Audience**: Developers implementing this feature

---

## Prerequisites

- ✅ Backend: Python 3.12+, FastAPI 0.127.0+, SQLAlchemy 2.0+, Alembic
- ✅ Frontend: Node.js 20+, Next.js 16+, React 19+
- ✅ Database: Neon PostgreSQL (shared with existing backend)
- ✅ Authentication: better-auth session (from spec 004)
- ✅ Encryption library: `cryptography` (install via pip)
- ✅ Gemini SDK: `google-generativeai` (install via pip)

---

## Setup Steps

### 1. Install Dependencies

**Backend** (`backend/pyproject.toml`):
```bash
cd backend
uv add cryptography google-generativeai
```

**Frontend** (`frontend/package.json`):
```bash
cd frontend
npm install lucide-react  # For Eye/EyeOff icons (may already be installed)
```

---

### 2. Generate Encryption Key

Generate a secure Fernet key for encrypting API keys at rest:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Output example**: `Hs5LhMvlQhR-N8jz5N6B5J6L9K2M3N4O5P6Q7R8S=`

---

### 3. Configure Environment Variables

**Backend** (`backend/.env`):
```bash
# Add this line to your existing .env
ENCRYPTION_KEY=<output-from-step-2>

# Example:
ENCRYPTION_KEY=Hs5LhMvlQhR-N8jz5N6B5J6L9K2M3N4O5P6Q7R8S=
```

**⚠️ Security Warning**:
- **Development**: Store in `.env` (add `.env` to `.gitignore`)
- **Production**: Use secrets manager (GitHub Secrets, AWS Secrets Manager, Railway secrets, etc.)
- **NEVER commit `ENCRYPTION_KEY` to git**

---

### 4. Update Backend Config

**File**: `backend/src/config.py`

```python
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet

class Settings(BaseSettings):
    # ... existing fields ...

    # NEW: Encryption key for API key storage
    ENCRYPTION_KEY: str

    class Config:
        env_file = ".env"

    def validate_encryption_key(self):
        """Validate ENCRYPTION_KEY is a valid Fernet key."""
        try:
            Fernet(self.ENCRYPTION_KEY.encode())
        except Exception:
            raise ValueError(
                "ENCRYPTION_KEY is not a valid Fernet key. "
                "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )

settings = Settings()
settings.validate_encryption_key()  # Validate on startup
```

---

### 5. Run Database Migration

**Create Migration**:
```bash
cd backend
alembic revision -m "Create user_api_keys table"
```

**Edit Migration** (`backend/alembic/versions/XXXX_create_user_api_keys_table.py`):

Use the migration script from [data-model.md](./data-model.md#alembic-migration).

**Run Migration**:
```bash
alembic upgrade head
```

**Verify**:
```bash
# Connect to PostgreSQL and check table exists
psql <your-database-url>
\d user_api_keys
```

---

### 6. Implement Backend Services

Create these files in order (TDD approach: write tests first):

1. **`backend/src/services/encryption_service.py`** - Encryption/decryption logic
2. **`backend/tests/unit/test_encryption_service.py`** - Unit tests (write FIRST)
3. **`backend/src/services/gemini_validator.py`** - API key validation
4. **`backend/tests/unit/test_gemini_validator.py`** - Unit tests (write FIRST)
5. **`backend/src/services/api_key_service.py`** - CRUD operations
6. **`backend/tests/unit/test_api_key_service.py`** - Unit tests (write FIRST)
7. **`backend/src/api/schemas/api_key.py`** - Pydantic request/response schemas
8. **`backend/src/api/routes/api_keys.py`** - FastAPI endpoints
9. **`backend/tests/integration/test_api_key_endpoints.py`** - Integration tests

**Code examples** available in [research.md](./research.md).

---

### 7. Implement Frontend Components

Create these files:

1. **`frontend/components/ui/PasswordInput.tsx`** - Reusable password input with show/hide toggle
2. **`frontend/components/settings/ApiKeyInput.tsx`** - API key input wrapper
3. **`frontend/components/settings/ApiKeyStatus.tsx`** - Status indicator
4. **`frontend/components/settings/TestConnectionButton.tsx`** - Test button with loading state
5. **`frontend/lib/api/apiKeys.ts`** - API client for `/api/user-api-keys` endpoints
6. **`frontend/lib/hooks/useApiKey.ts`** - React hook for API key state
7. **`frontend/app/(authenticated)/settings/page.tsx`** - Settings page

**Code examples** available in [research.md](./research.md#4-frontend-password-input-best-practices).

---

### 8. Update AI Agent

**File**: `ai-agent/src/services/api_key_retrieval.py` (NEW)

```python
import httpx
from typing import Optional

class ApiKeyRetrievalService:
    """Retrieves user-specific API keys from backend."""

    def __init__(self, backend_url: str):
        self.backend_url = backend_url

    async def get_gemini_key(self, user_id: str) -> Optional[str]:
        """
        Fetch user's Gemini API key from backend.

        Returns:
            Decrypted API key or None if not configured.

        Raises:
            HTTPException if user has no key configured.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.backend_url}/api/user-api-keys/current",
                headers={"X-User-ID": user_id},  # Service-to-service auth
            )

            if response.status_code == 404:
                return None  # User hasn't configured a key

            response.raise_for_status()
            data = response.json()

            if not data.get("configured"):
                return None

            # Backend returns decrypted key for service-to-service calls
            return data.get("plaintext_key")
```

**File**: `ai-agent/src/ai_agent/agent/agent_service.py` (UPDATED)

```python
# Replace global GEMINI_API_KEY with per-user key retrieval

async def process_chat_request(user_id: str, message: str):
    # Retrieve user-specific API key
    api_key_service = ApiKeyRetrievalService(settings.BACKEND_URL)
    user_api_key = await api_key_service.get_gemini_key(user_id)

    if not user_api_key:
        raise HTTPException(
            status_code=400,
            detail="Please configure your Gemini API key in Settings to use AI features"
        )

    # Use user's API key for Gemini request
    genai.configure(api_key=user_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(message)

    return response.text
```

---

## Testing

### Unit Tests (No Database)

```bash
cd backend
pytest tests/unit/test_encryption_service.py -v
pytest tests/unit/test_gemini_validator.py -v
pytest tests/unit/test_api_key_service.py -v
```

### Contract Tests (Database Required)

```bash
pytest tests/contract/test_user_api_key_model.py -v
```

### Integration Tests (Full API)

```bash
pytest tests/integration/test_api_key_endpoints.py -v
pytest tests/integration/test_gemini_validation.py -v
```

### Frontend Tests

```bash
cd frontend
npm test -- components/settings/
```

### E2E Test (Manual)

1. Start backend: `cd backend && uvicorn src.api.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Login as user
4. Navigate to `/settings`
5. Enter Gemini API key: `AIza...` (obtain from https://aistudio.google.com/apikey)
6. Click "Test Connection" → should show success
7. Click "Save" → should show "API key saved successfully"
8. Navigate away and return → should show masked key
9. Try AI chat feature → should use your API key

---

## Deployment Checklist

### Backend

- [ ] Set `ENCRYPTION_KEY` in production secrets (Railway/AWS/GCP)
- [ ] Run Alembic migration: `alembic upgrade head`
- [ ] Add `cryptography` and `google-generativeai` to dependencies
- [ ] Verify logs don't contain plaintext API keys
- [ ] Test API endpoints with curl/Postman

### Frontend

- [ ] Build production bundle: `npm run build`
- [ ] Test settings page on mobile (320px width)
- [ ] Verify password input is masked by default
- [ ] Verify Eye/EyeOff toggle works
- [ ] Test error states (invalid key, network error)

### AI Agent

- [ ] Update to use `ApiKeyRetrievalService`
- [ ] Remove global `GEMINI_API_KEY` environment variable
- [ ] Test per-user API key retrieval
- [ ] Verify error message when user has no key configured

### Security

- [ ] Confirm `ENCRYPTION_KEY` not in git
- [ ] Test encryption/decryption round-trip
- [ ] Verify API keys are never logged
- [ ] Test HTTPS is enforced (production)
- [ ] Rate limit Test Connection endpoint (5 tests/hour per user)

---

## Troubleshooting

### Issue: "Invalid encryption key" error on startup

**Solution**:
```bash
# Regenerate a valid Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Update .env
ENCRYPTION_KEY=<new-key>
```

### Issue: "Decryption failed" when retrieving keys

**Cause**: `ENCRYPTION_KEY` changed after keys were encrypted.

**Solution**: Either restore old key or re-encrypt all keys:
```python
# Script to re-encrypt all keys with new ENCRYPTION_KEY
old_key = "old-key"
new_key = "new-key"

old_cipher = Fernet(old_key.encode())
new_cipher = Fernet(new_key.encode())

for record in session.query(UserApiKey).all():
    plaintext = old_cipher.decrypt(record.encrypted_key.encode()).decode()
    record.encrypted_key = new_cipher.encrypt(plaintext.encode()).decode()

session.commit()
```

### Issue: Test Connection always times out

**Cause**: Gemini API may be rate limiting or network issues.

**Solution**:
- Check API key is valid: https://aistudio.google.com/apikey
- Verify network can reach `https://generativelanguage.googleapis.com`
- Check Gemini API quotas/limits

### Issue: Frontend shows "Missing authentication credentials"

**Cause**: better-auth session cookie not being sent.

**Solution**:
- Verify CORS is configured with `allow_credentials=True`
- Check browser sends `Authorization: Bearer <token>` header
- Verify better-auth session is valid (not expired)

---

## Performance Benchmarks

| Operation | Target | Actual (Expected) |
|-----------|--------|-------------------|
| Encrypt API key | <1ms | ~0.5ms |
| Decrypt API key | <1ms | ~0.5ms |
| Save API key (POST) | <500ms p95 | ~200ms (DB write + encryption) |
| Get API key status (GET) | <100ms p95 | ~50ms (DB read) |
| Test Connection | <3s | 1-2s (depends on Gemini API) |
| Settings page load | <1s | ~500ms (includes auth + API call) |

---

## Monitoring

### Metrics to Track

- API key save success rate (target: >95%)
- Test Connection success rate (target: >90% for valid keys)
- API key retrieval latency (target: <50ms p95)
- Encryption/decryption errors (target: 0)

### Logs to Monitor

```python
# Example logging (don't log plaintext!)
logger.info("API key saved", extra={"user_id": user_id, "provider": "gemini"})
logger.info("API key validated", extra={"user_id": user_id, "status": "success"})
logger.error("Decryption failed", extra={"user_id": user_id, "error": str(e)})
```

**⚠️ NEVER log plaintext API keys**

---

## Related Documentation

- [Spec](./spec.md) - Full feature specification
- [Research](./research.md) - Technical research and decisions
- [Data Model](./data-model.md) - Database schema details
- [API Contracts](./contracts/api-keys.openapi.yaml) - OpenAPI specification

---

## Next Steps

After completing this quickstart:

1. Run `/sp.tasks` to generate atomic 20-30 minute implementation tasks
2. Follow TDD cycle (Red-Green-Refactor) for each task
3. Create pull request with spec reference
4. Deploy to staging for QA testing
5. Monitor metrics and error rates

**Estimated implementation time**: 8-12 hours (20-30 minute tasks × 16-24 tasks)
