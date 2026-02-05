# Quickstart: Hybrid JWT Authentication

**Feature**: 013-hybrid-jwt-auth
**Date**: 2026-01-02
**Audience**: Developers implementing or testing JWT authentication

This guide provides step-by-step instructions for implementing, testing, and deploying hybrid JWT authentication.

---

## Prerequisites

### Development Environment
- Python 3.12+ (backend)
- Node.js 20+ (auth-server)
- PostgreSQL (Neon serverless or local)
- Git (for version control)

### Required Packages
```bash
# Backend (Python)
pip install pyjwt cryptography httpx pytest pytest-asyncio

# Auth-server (Node.js)
npm install jsonwebtoken @types/jsonwebtoken

# Frontend (Next.js)
npm install @types/node
```

### Environment Variables
Create/update `.env` files in each service:

**backend/.env**:
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/momentum
JWT_SECRET=your-secret-key-minimum-32-characters-long  # Same as BETTER_AUTH_SECRET
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_AUTH_ENABLED=false  # Feature flag (set to true to enable)
JWT_ROLLOUT_PERCENTAGE=0  # 0-100 (percentage of users on JWT auth)
ENVIRONMENT=development
```

**auth-server/.env**:
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/momentum
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long  # Same as JWT_SECRET
JWT_ENABLED=false  # Feature flag (set to true to enable JWT issuance on login)
```

**frontend/.env.local**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_URL=http://localhost:3001
```

---

## Implementation Workflow

### Phase 1: Backend (FastAPI) - JWT Validation & Refresh Endpoint

#### Step 1.1: Create JWT Service (TDD - RED)
```bash
cd backend
# Write failing test first
cat > tests/contract/test_jwt_service.py << 'EOF'
"""Contract tests for JWT service."""
import pytest
from datetime import datetime, timedelta, UTC
from src.services.jwt_service import JWTService, TokenExpiredError, InvalidTokenError

def test_generate_access_token_contains_required_claims():
    """Access token MUST contain sub, iat, exp, and type claims."""
    service = JWTService(secret="test-secret-32-characters-long!!")
    token = service.generate_access_token("user_123")

    payload = service.decode_token(token)
    assert payload["sub"] == "user_123"
    assert payload["type"] == "access"
    assert "iat" in payload
    assert "exp" in payload

def test_validate_access_token_rejects_expired():
    """Access token validation MUST reject expired tokens."""
    service = JWTService(secret="test-secret-32-characters-long!!")
    # Create token that expired 1 hour ago
    expired_token = service.generate_access_token(
        "user_123",
        expires_delta=timedelta(hours=-1)
    )

    with pytest.raises(TokenExpiredError):
        service.validate_access_token(expired_token)
EOF

# Run test (should FAIL - RED)
uv run pytest tests/contract/test_jwt_service.py -v
```

#### Step 1.2: Implement JWT Service (GREEN)
```bash
# Create service implementation
cat > src/services/jwt_service.py << 'EOF'
"""JWT token generation and validation service."""
import jwt
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
from src.config import settings

class TokenExpiredError(Exception):
    """Raised when token has expired."""
    pass

class InvalidTokenError(Exception):
    """Raised when token is invalid."""
    pass

class JWTService:
    """Service for JWT token operations."""

    def __init__(self, secret: Optional[str] = None, algorithm: str = "HS256"):
        self.secret = secret or settings.JWT_SECRET
        self.algorithm = algorithm

    def generate_access_token(
        self,
        user_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Generate JWT access token."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + expires_delta,
            "type": "access"
        }

        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def validate_access_token(self, token: str) -> str:
        """Validate access token and return user ID."""
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )

            if payload.get("type") != "access":
                raise InvalidTokenError("Invalid token type")

            return payload["sub"]

        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Access token expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {e}")

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode token without validation (for testing)."""
        return jwt.decode(
            token,
            self.secret,
            algorithms=[self.algorithm],
            options={"verify_signature": False}
        )
EOF

# Run test (should PASS - GREEN)
uv run pytest tests/contract/test_jwt_service.py -v
```

#### Step 1.3: Add Refresh Endpoint (TDD)
```bash
# Write integration test for refresh flow
cat > tests/integration/test_token_refresh_flow.py << 'EOF'
"""Integration test for token refresh flow."""
import pytest
from httpx import AsyncClient
from src.api.main import app

@pytest.mark.asyncio
async def test_refresh_endpoint_returns_new_access_token():
    """Refresh endpoint MUST return new access token with valid refresh token."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Simulate login to get refresh token
        # (Implementation depends on auth-server integration)

        # Call refresh endpoint
        response = await client.post(
            "/api/auth/refresh",
            cookies={"refreshToken": "valid_refresh_token_here"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert data["expiresIn"] == 1800
EOF

# Implement refresh endpoint (router)
cat > src/api/routers/auth.py << 'EOF'
"""Authentication endpoints for JWT token management."""
from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import get_db
from src.services.jwt_service import JWTService
from src.services.refresh_token_service import RefreshTokenService
from src.api.schemas.auth import TokenRefreshResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_access_token(
    refreshToken: str = Cookie(...),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token from httpOnly cookie."""
    try:
        # Validate refresh token and get user ID
        refresh_service = RefreshTokenService(db)
        user_id = await refresh_service.validate_refresh_token(refreshToken)

        # Generate new access token
        jwt_service = JWTService()
        access_token = jwt_service.generate_access_token(user_id)

        return TokenRefreshResponse(
            accessToken=access_token,
            expiresIn=1800
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
EOF
```

---

### Phase 2: Auth-Server (Node.js) - JWT Issuance on Login

#### Step 2.1: Add JWT Signing to Login Response
```bash
cd auth-server

# Create JWT utility
cat > src/lib/jwt.ts << 'EOF'
import jwt from 'jsonwebtoken';
import crypto from 'crypto';

const JWT_SECRET = process.env.BETTER_AUTH_SECRET!;
const ACCESS_TOKEN_EXPIRE_MINUTES = 30;
const REFRESH_TOKEN_EXPIRE_DAYS = 7;

export interface AccessTokenPayload {
  sub: string;  // user ID
  iat: number;  // issued at
  exp: number;  // expiration
  type: 'access';
}

export function generateAccessToken(userId: string): string {
  const now = Math.floor(Date.now() / 1000);
  const payload: AccessTokenPayload = {
    sub: userId,
    iat: now,
    exp: now + (ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    type: 'access'
  };

  return jwt.sign(payload, JWT_SECRET, { algorithm: 'HS256' });
}

export function generateRefreshToken(): string {
  // 32 bytes = 256 bits of cryptographic randomness
  return crypto.randomBytes(32).toString('base64url');
}

export async function hashRefreshToken(token: string): Promise<string> {
  return crypto.createHash('sha256').update(token).digest('hex');
}
EOF

# Modify login handler to issue JWT tokens
# (Add to existing auth.setup() callback in src/index.ts)
```

---

### Phase 3: Frontend (Next.js) - Token Storage & Refresh Interceptor

#### Step 3.1: Create Token Refresh Hook
```bash
cd frontend

cat > src/hooks/useTokenRefresh.ts << 'EOF'
import { useEffect, useRef } from 'react';

const REFRESH_LOCK_KEY = 'auth_refresh_lock';
const REFRESH_LOCK_TIMEOUT = 5000; // 5 seconds

export function useTokenRefresh() {
  const channelRef = useRef<BroadcastChannel | null>(null);

  useEffect(() => {
    // Create BroadcastChannel for cross-tab token sync
    if (typeof window !== 'undefined' && 'BroadcastChannel' in window) {
      channelRef.current = new BroadcastChannel('auth_channel');

      channelRef.current.onmessage = (event) => {
        if (event.data.type === 'TOKEN_REFRESHED') {
          // Update access token in memory
          localStorage.setItem('accessToken', event.data.accessToken);
        }
      };
    }

    return () => {
      channelRef.current?.close();
    };
  }, []);

  async function refreshToken(): Promise<string> {
    // Acquire refresh lock (prevents duplicate requests)
    const lock = {
      timestamp: Date.now(),
      tabId: crypto.randomUUID()
    };
    localStorage.setItem(REFRESH_LOCK_KEY, JSON.stringify(lock));

    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include' // Send httpOnly cookie
      });

      if (!response.ok) {
        throw new Error('Refresh failed');
      }

      const { accessToken } = await response.json();

      // Broadcast to other tabs
      channelRef.current?.postMessage({
        type: 'TOKEN_REFRESHED',
        accessToken
      });

      return accessToken;
    } finally {
      // Release lock
      localStorage.removeItem(REFRESH_LOCK_KEY);
    }
  }

  return { refreshToken };
}
EOF
```

---

## Testing

### Unit Tests (Backend)
```bash
cd backend

# Run all JWT-related tests
uv run pytest tests/contract/test_jwt_service.py -v
uv run pytest tests/contract/test_refresh_token_service.py -v
uv run pytest tests/unit/test_jwt_validation.py -v

# Check coverage
uv run pytest --cov=src/services --cov-report=html tests/
```

### Integration Tests
```bash
# Test end-to-end refresh flow
uv run pytest tests/integration/test_token_refresh_flow.py -v

# Test hybrid auth migration (JWT + session coexistence)
uv run pytest tests/integration/test_hybrid_auth_migration.py -v
```

### E2E Tests (Frontend)
```bash
cd frontend

# Run Playwright tests
npx playwright test tests/integration/token-refresh.spec.ts
```

### Manual Testing
```bash
# 1. Start all services
cd backend && uv run uvicorn src.api.main:app --reload --port 8000 &
cd auth-server && npm run dev &
cd frontend && npm run dev &

# 2. Login via frontend
# 3. Inspect browser DevTools → Application → Cookies
#    - Should see httpOnly refreshToken cookie
# 4. Inspect localStorage
#    - Should see accessToken (JWT format)
# 5. Wait 30 minutes or manually expire token
# 6. Make API request → Should auto-refresh

# 3. Test refresh endpoint directly
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Cookie: refreshToken=YOUR_REFRESH_TOKEN_HERE" \
  -v

# Expected response:
# {
#   "accessToken": "eyJhbGc...",
#   "expiresIn": 1800
# }
```

---

## Deployment

### Environment Configuration

**Production Environment Variables**:
```bash
# backend/.env.production
DATABASE_URL=postgresql://prod-user:pass@neon.tech:5432/momentum
JWT_SECRET=${BETTER_AUTH_SECRET}  # Same 32+ char secret
JWT_AUTH_ENABLED=true
JWT_ROLLOUT_PERCENTAGE=0  # Start with 0%, gradual rollout
ENVIRONMENT=production

# auth-server/.env.production
BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
JWT_ENABLED=true

# frontend/.env.production
NEXT_PUBLIC_API_URL=https://api.production.com
NEXT_PUBLIC_AUTH_URL=https://auth.production.com
```

### Deployment Steps

#### Step 1: Deploy with Feature Flags Disabled (0% rollout)
```bash
# Set environment variables
export JWT_AUTH_ENABLED=false
export JWT_ROLLOUT_PERCENTAGE=0

# Deploy backend
cd backend && uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Deploy auth-server
cd auth-server && npm run build && npm start

# Deploy frontend
cd frontend && npm run build && npm start

# Verify: All users still using session-based auth
```

#### Step 2: Enable JWT for 10% of Users
```bash
# Update environment (no code deployment required)
export JWT_AUTH_ENABLED=true
export JWT_ROLLOUT_PERCENTAGE=10

# Restart services
# Monitor metrics: auth_validation_seconds, token_refresh_total

# Watch for errors in logs:
# - Token signature failures
# - Refresh token mismatches
# - Database connection errors
```

#### Step 3: Gradual Rollout (25% → 50% → 100%)
```bash
# Increase rollout percentage based on metrics
# Wait 24-48 hours between increases
# Monitor:
#   - Error rate (should be <0.1%)
#   - Auth latency (should be <1ms p95)
#   - Database query rate (should drop 90%+)

# If any issues:
export JWT_ROLLOUT_PERCENTAGE=0  # Instant rollback
```

#### Step 4: Full Rollout
```bash
# After successful 100% rollout for 30 days:
# - Remove feature flags
# - Deprecate session-based auth (future release)
# - Clean up old session records
```

---

## Troubleshooting

### Issue: "Invalid token signature"
**Cause**: JWT_SECRET mismatch between auth-server and backend
**Solution**:
```bash
# Verify both services use same secret
echo $BETTER_AUTH_SECRET  # auth-server
echo $JWT_SECRET          # backend
# They MUST be identical
```

### Issue: "Refresh token not found"
**Cause**: httpOnly cookie not sent or refresh token not in database
**Solution**:
```bash
# Check cookie in browser DevTools → Application → Cookies
# Verify database has hash:
psql $DATABASE_URL -c "SELECT id, token, expires_at FROM user_sessions WHERE user_id='USER_ID';"
```

### Issue: "Token expired" immediately after refresh
**Cause**: Server clock skew or incorrect expiration calculation
**Solution**:
```bash
# Verify server time is synced
date -u
# Should match current UTC time

# Check token payload
python -c "
import jwt
token = 'YOUR_TOKEN_HERE'
payload = jwt.decode(token, options={'verify_signature': False})
print(f'Issued: {payload[\"iat\"]}, Expires: {payload[\"exp\"]}')
"
```

### Issue: Multiple tabs refreshing simultaneously
**Cause**: BroadcastChannel not working or lock not acquired
**Solution**:
```javascript
// Check BroadcastChannel support in browser console
'BroadcastChannel' in window  // Should be true

// Monitor storage events
window.addEventListener('storage', (e) => {
  console.log('Storage event:', e.key, e.newValue);
});
```

---

## Monitoring & Metrics

### Key Metrics to Track

**Performance**:
- `auth_validation_seconds{method="jwt"}` - JWT validation latency
- `auth_validation_seconds{method="session"}` - Session validation latency
- `token_refresh_duration_seconds` - Refresh endpoint latency

**Usage**:
- `token_refresh_total` - Total refresh requests
- `token_refresh_errors_total{reason="expired|invalid|revoked"}` - Failed refreshes
- `jwt_auth_users_total` - Users on JWT auth (vs session)

**Database**:
- `auth_db_queries_total{method="jwt|session"}` - Auth-related queries
- `user_sessions_table_size_mb` - Session table size

### Alerting Thresholds

```yaml
# Prometheus alert rules
groups:
  - name: jwt_auth_alerts
    rules:
      - alert: HighJWTValidationLatency
        expr: histogram_quantile(0.95, auth_validation_seconds{method="jwt"}) > 0.001
        annotations:
          summary: JWT validation p95 > 1ms

      - alert: HighRefreshErrorRate
        expr: rate(token_refresh_errors_total[5m]) > 0.01
        annotations:
          summary: >1% refresh requests failing

      - alert: RefreshTokenTableGrowth
        expr: user_sessions_table_size_mb > 100
        annotations:
          summary: Session table > 100MB (check cleanup job)
```

---

## Next Steps

After successful deployment:

1. **Monitor for 30 days** at 100% rollout
2. **Collect performance metrics** (before/after comparison)
3. **Document lessons learned** (update this guide)
4. **Plan deprecation** of session-based auth (future spec)
5. **Consider enhancements**:
   - Token rotation (refresh token changes on each use)
   - Redis-based token blacklist (immediate revocation)
   - Session management UI (view/revoke active sessions)

---

## Quick Reference

### Commands Cheat Sheet
```bash
# Run backend tests
cd backend && uv run pytest tests/ -v

# Start backend dev server
cd backend && uv run uvicorn src.api.main:app --reload --port 8000

# Check JWT token payload (debugging)
python -c "import jwt; print(jwt.decode('TOKEN', options={'verify_signature': False}))"

# Query active sessions
psql $DATABASE_URL -c "SELECT COUNT(*) FROM user_sessions WHERE expires_at > NOW();"

# Test refresh endpoint
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Cookie: refreshToken=TOKEN" -v
```

### File Locations
- JWT Service: `backend/src/services/jwt_service.py`
- Refresh Service: `backend/src/services/refresh_token_service.py`
- Auth Router: `backend/src/api/routers/auth.py`
- Auth Dependency: `backend/src/api/dependencies.py`
- Config: `backend/src/config.py`
- Contracts: `specs/013-hybrid-jwt-auth/contracts/openapi.yaml`
- Tests: `backend/tests/{contract,integration,unit}/`

---

**End of Quickstart Guide**
