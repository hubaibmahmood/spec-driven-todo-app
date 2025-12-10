# Session Authentication Demo

## Quick Test Example

### 1. Create a session in database (simulating better-auth)

```python
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# Configuration
SESSION_HASH_SECRET = "dev-secret-key-change-in-production"
user_id = uuid4()
token = "my_session_token_abc123"

# Hash the token (same as better-auth would do)
token_hash = hmac.new(
    SESSION_HASH_SECRET.encode(),
    token.encode(),
    hashlib.sha256
).hexdigest()

# Insert into user_sessions table
session = {
    "id": uuid4(),
    "user_id": user_id,
    "token_hash": token_hash,
    "expires_at": datetime.now(timezone.utc) + timedelta(hours=24),
    "revoked": False
}
```

### 2. Make authenticated API request

```bash
# Set token as Bearer token
TOKEN="my_session_token_abc123"

# List all tasks (authenticated)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/tasks/

# Create a task (authenticated)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Authenticated Task","description":"Created by user"}' \
  http://localhost:8000/tasks/
```

## Authentication Flow

```
Client → FastAPI Endpoint → get_current_user() → validate_session() → TaskRepository
                           (HTTPBearer)         (Hash + Query DB)    (Filter by user_id)
```

## Security Features

- HMAC-SHA256 token hashing
- Constant-time comparison
- Session expiration validation
- Revocation support
- User isolation on all endpoints

## HTTP Status Codes

| Scenario | Status | Response |
|----------|--------|----------|
| Valid session, task found | 200 | Task data |
| Missing/invalid token | 401 | Error |
| Task not found | 404 | Error |

## Testing

```bash
pytest tests/integration/test_auth.py -v
```
