# Research: Hybrid JWT Authentication

**Feature**: 013-hybrid-jwt-auth
**Date**: 2026-01-02
**Status**: Complete

This document consolidates research findings for implementing hybrid JWT authentication with Python FastAPI, Node.js better-auth, and React frontend.

---

## 1. JWT Token Structure & Security (PyJWT Library)

### Decision: Use HMAC-SHA256 (HS256) with PyJWT

**Rationale**:
- Symmetric key algorithm (HS256) sufficient for single-secret deployment across backend instances
- PyJWT is the industry-standard Python JWT library (40M+ downloads/month, actively maintained)
- Constant-time signature validation prevents timing attacks
- Simpler secret management compared to asymmetric keys (RS256)

**Implementation Pattern**:
```python
import jwt
from datetime import datetime, timedelta, UTC

# Token generation
payload = {
    "sub": user_id,           # Subject (user ID)
    "exp": datetime.now(UTC) + timedelta(minutes=30),  # Expiration
    "iat": datetime.now(UTC),  # Issued at
    "type": "access"           # Token type claim
}
token = jwt.encode(payload, secret_key, algorithm="HS256")

# Token validation
try:
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    user_id = payload["sub"]
except jwt.ExpiredSignatureError:
    # Handle expired token (return 401 with "token_expired" error code)
except jwt.InvalidTokenError:
    # Handle invalid signature/malformed token
```

**Security Considerations**:
- Secret key MUST be minimum 32 characters (256 bits)
- Reuse existing `BETTER_AUTH_SECRET` from auth-server for consistency
- Store in environment variable, never hardcode
- Use `algorithms=["HS256"]` parameter in decode to prevent algorithm substitution attacks

**Alternatives Considered**:
- RS256 (asymmetric): Rejected - overkill for monolithic backend; requires key pair management; useful for microservices where validation happens without access to signing key
- None algorithm: Rejected - security vulnerability

**References**:
- PyJWT documentation: https://pyjwt.readthedocs.io/
- RFC 7519 (JWT): https://datatracker.ietf.org/doc/html/rfc7519
- OWASP JWT Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html

---

## 2. Refresh Token Storage & Security

### Decision: SHA-256 hashing with database storage

**Rationale**:
- SHA-256 is cryptographically secure one-way hash (cannot reverse to get original token)
- Fast validation performance (hash incoming token, compare with stored hash)
- Industry best practice for token storage (GitHub, GitLab use similar approach)
- Better performance than bcrypt for this use case (tokens are cryptographically random, not user passwords)

**Implementation Pattern**:
```python
import hashlib
import secrets

# Token generation (32 bytes = 256 bits)
refresh_token = secrets.token_urlsafe(32)  # Cryptographically secure random

# Token hashing (before storage)
token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

# Store in database:
# - token_hash (hashed value)
# - user_id (foreign key)
# - expires_at (UTC timestamp, 7 days from now)
# - ip_address, user_agent (audit trail)

# Token validation (constant-time comparison)
import hmac
incoming_hash = hashlib.sha256(incoming_token.encode()).hexdigest()
is_valid = hmac.compare_digest(token_hash, incoming_hash)
```

**Security Considerations**:
- Use `secrets` module for cryptographically secure random generation (NOT `random` module)
- Always use `hmac.compare_digest()` to prevent timing attacks
- Store hash, NEVER plain token
- Implement expiration check: `expires_at > datetime.now(UTC)`

**Alternatives Considered**:
- bcrypt hashing: Rejected - intentionally slow (designed for passwords); SHA-256 sufficient for high-entropy tokens
- Plain token storage: Rejected - database compromise leaks all active sessions
- Opaque token rotation: Considered for future enhancement (issue new refresh token on each use)

**References**:
- Python secrets module: https://docs.python.org/3/library/secrets.html
- OWASP Session Management: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

---

## 3. Cross-Tab Token Synchronization (Frontend)

### Decision: BroadcastChannel API with localStorage fallback

**Rationale**:
- BroadcastChannel API is modern, purpose-built for cross-tab communication
- No polling required (event-driven)
- Supported in all modern browsers (Chrome 54+, Firefox 38+, Safari 15.4+)
- localStorage events as fallback for older browsers

**Implementation Pattern**:
```typescript
// Tab 1 (detects token expiration first)
const channel = new BroadcastChannel('auth_channel');

// Acquire refresh lock (timestamp-based, 5-second expiry)
const lock = {
  timestamp: Date.now(),
  tabId: crypto.randomUUID()
};
localStorage.setItem('refresh_lock', JSON.stringify(lock));

// Perform token refresh
const newToken = await refreshAccessToken();

// Broadcast new token to all tabs
channel.postMessage({
  type: 'TOKEN_REFRESHED',
  accessToken: newToken
});

// Other tabs (waiting for new token)
channel.onmessage = (event) => {
  if (event.data.type === 'TOKEN_REFRESHED') {
    updateAccessToken(event.data.accessToken);
    retryPendingRequests();
  }
};
```

**Edge Cases Handled**:
- Lock expiration: 5 seconds (handles crashed/closed tabs)
- Lock collision: First tab to write lock wins (timestamp comparison)
- Multiple expirations: Queued requests wait for single refresh
- Fallback: localStorage 'storage' event listener for Safari < 15.4

**Alternatives Considered**:
- Shared Worker: Rejected - more complex, not supported in Safari
- localStorage polling: Rejected - inefficient, introduces delay
- WebSocket coordination: Rejected - requires server infrastructure

**References**:
- BroadcastChannel API: https://developer.mozilla.org/en-US/docs/Web/API/Broadcast_Channel_API
- Cross-tab communication patterns: https://developer.chrome.com/blog/cross-tab-communication/

---

## 4. Token Refresh Retry Logic

### Decision: Exponential backoff with 3 retry attempts

**Rationale**:
- Industry standard: 3 retries balances recovery vs user experience
- Exponential backoff (1s, 2s, 4s) reduces server load during outages
- Total retry window: ~7 seconds (acceptable for UX)
- Distinguishes network errors (retry) from auth errors (immediate redirect)

**Implementation Pattern**:
```typescript
async function refreshWithRetry(maxRetries = 3): Promise<string> {
  const delays = [1000, 2000, 4000]; // Exponential backoff in ms

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include' // Send httpOnly refresh token cookie
      });

      if (response.status === 401 || response.status === 403) {
        // Authentication error - don't retry, redirect to login
        throw new AuthError('Session expired');
      }

      if (!response.ok) {
        // Network/server error - retry with backoff
        throw new NetworkError(`HTTP ${response.status}`);
      }

      const { accessToken } = await response.json();
      return accessToken;

    } catch (error) {
      if (error instanceof AuthError) {
        throw error; // Don't retry auth errors
      }

      if (attempt < maxRetries - 1) {
        await sleep(delays[attempt]);
        continue; // Retry
      }

      throw new RefreshError('Unable to refresh token after 3 attempts');
    }
  }
}
```

**Error Handling**:
- 401/403: Redirect to login immediately (no retries)
- 500/502/503/timeout: Retry with exponential backoff
- Network errors (fetch failure): Retry with backoff
- After all retries: Show user-friendly error message

**Alternatives Considered**:
- Infinite retries: Rejected - poor UX for expired refresh tokens
- No retries: Rejected - fails on transient network issues
- Linear backoff: Rejected - less effective at reducing server load

**References**:
- Google Cloud retry guidance: https://cloud.google.com/architecture/best-practices-for-cloud-storage-retries
- AWS retry strategies: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/

---

## 5. Feature Flag-Based Migration Strategy

### Decision: Environment-based feature flag with user cohort rollout

**Rationale**:
- Gradual rollout minimizes risk: 0% → 10% → 25% → 50% → 100%
- Easy rollback (change flag, restart service)
- Enables A/B testing and monitoring
- No code deployment required to adjust rollout percentage

**Implementation Pattern**:
```python
# config.py
class Settings(BaseSettings):
    JWT_AUTH_ENABLED: bool = False  # Master switch
    JWT_ROLLOUT_PERCENTAGE: int = 0  # 0-100

    def should_use_jwt(self, user_id: str) -> bool:
        """Determine if user should use JWT auth."""
        if not self.JWT_AUTH_ENABLED:
            return False

        if self.JWT_ROLLOUT_PERCENTAGE >= 100:
            return True

        # Stable hash-based cohort assignment (user always in same cohort)
        import hashlib
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        cohort = user_hash % 100
        return cohort < self.JWT_ROLLOUT_PERCENTAGE

# dependencies.py
async def get_current_user(
    credentials: HTTPAuthorizationCredentials,
    db: AsyncSession
) -> str:
    """Hybrid authentication: JWT or session based on feature flag."""
    token = credentials.credentials

    # Try JWT validation first if enabled
    if settings.JWT_AUTH_ENABLED:
        try:
            user_id = validate_jwt(token)
            if settings.should_use_jwt(user_id):
                return user_id  # JWT path
        except jwt.InvalidTokenError:
            pass  # Fall through to session validation

    # Fall back to session validation (existing better-auth flow)
    user_id = await validate_session(token, db)
    return user_id
```

**Migration Phases**:
1. **Phase 1 (0%)**: Deploy code with flags disabled, verify no regression
2. **Phase 2 (10%)**: Enable for 10% of users, monitor error rates and performance
3. **Phase 3 (25-50%)**: Gradually increase if metrics are healthy
4. **Phase 4 (100%)**: Full rollout, deprecate session-based auth in future release

**Rollback Strategy**:
- Set `JWT_AUTH_ENABLED=false` in environment
- Restart services (no code deployment)
- Users revert to session-based auth automatically

**Alternatives Considered**:
- Big-bang migration: Rejected - high risk, no rollback
- Database flag per user: Rejected - complex, requires migration
- Time-based rollout: Rejected - not stable (users switch auth methods)

**References**:
- Feature flag best practices: https://launchdarkly.com/blog/feature-flag-best-practices/
- Gradual rollout strategies: https://research.google/pubs/pub42542/

---

## 6. Database Schema Reuse (user_sessions Table)

### Decision: Reuse existing better-auth `user_sessions` table

**Rationale**:
- Minimizes schema changes and migration complexity
- Table already has required fields: userId, token, expiresAt, ipAddress, userAgent
- FastAPI can read/write to same table as better-auth (Node.js)
- No new table creation or data migration required

**Existing Schema** (managed by better-auth Prisma):
```prisma
model UserSession {
  id        String   @id @default(cuid())
  userId    String
  token     String   @unique  // Will store HASHED refresh token
  expiresAt DateTime
  ipAddress String?
  userAgent String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

**FastAPI SQLAlchemy Mapping**:
```python
class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String(255), primary_key=True)
    user_id = Column("userId", String(255), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True)  # Stores SHA-256 hash
    expires_at = Column("expiresAt", DateTime(timezone=False), nullable=False)
    ip_address = Column("ipAddress", Text, nullable=True)
    user_agent = Column("userAgent", Text, nullable=True)
    created_at = Column("createdAt", DateTime(timezone=False), nullable=True)
    updated_at = Column("updatedAt", DateTime(timezone=False), nullable=True)
```

**Compatibility Notes**:
- better-auth currently stores plain session tokens in `token` field
- Hybrid approach: JWT refresh tokens stored as SHA-256 hashes (64 hex characters)
- No collision: session tokens and refresh token hashes have different formats
- Both systems can coexist during migration

**Migration Impact**: None - reuses existing table structure

**Alternatives Considered**:
- New `refresh_tokens` table: Rejected - unnecessary complexity, duplicate fields
- Separate database: Rejected - increases infrastructure cost and latency

---

## 7. Performance Optimization Targets

### Baseline (Session-Based Auth)
- **Database query per request**: 1 query to `user_sessions` table
- **Query latency (p95)**: ~15ms (Neon serverless cold start)
- **Load at 1000 concurrent users**: 167 queries/sec (10 req/min/user)

### Target (Hybrid JWT Auth)
- **Database query per request**: 0 queries (JWT signature validation only)
- **Validation latency (p95)**: <1ms (in-memory signature check)
- **Refresh queries**: <5 queries/sec (only when access token expires)
- **Performance improvement**: >90% reduction in auth queries

### Measurement Approach
```python
import time
from prometheus_client import Histogram

auth_validation_time = Histogram(
    'auth_validation_seconds',
    'Time spent validating authentication',
    ['method']  # 'jwt' or 'session'
)

@auth_validation_time.labels(method='jwt').time()
def validate_jwt(token: str) -> str:
    # JWT validation logic
    pass
```

**Monitoring Metrics**:
- `auth_validation_seconds{method="jwt"}` - JWT validation time
- `auth_validation_seconds{method="session"}` - Session validation time
- `token_refresh_total` - Refresh endpoint call rate
- `token_refresh_errors_total` - Failed refresh attempts

**Success Criteria** (from spec.md SC-002, SC-003, SC-005):
- ✅ 90%+ reduction in auth database queries
- ✅ <1ms p95 JWT validation latency
- ✅ <100ms p95 token refresh latency

---

## Summary

| Research Area | Decision | Key Benefit |
|--------------|----------|-------------|
| JWT Library | PyJWT with HS256 | Industry standard, secure, well-documented |
| Refresh Token Storage | SHA-256 hashing in PostgreSQL | Fast validation, secure against DB compromise |
| Cross-Tab Sync | BroadcastChannel API | Zero polling, event-driven, modern browsers |
| Retry Logic | 3 attempts, exponential backoff | Handles transient failures, good UX |
| Migration Strategy | Feature flags with cohort rollout | Low risk, easy rollback, gradual validation |
| Database Schema | Reuse user_sessions table | Zero migration, minimal changes |
| Performance | <1ms JWT validation, 90% query reduction | Scalability for 1000+ concurrent users |

**No unresolved "NEEDS CLARIFICATION" items remain.** All technical decisions documented with rationale and alternatives.
