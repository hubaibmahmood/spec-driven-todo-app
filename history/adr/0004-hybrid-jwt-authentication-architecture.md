# ADR-0004: Hybrid JWT Authentication Architecture

> **Scope**: This ADR documents the complete authentication approach including token strategy, validation mechanism, storage, and refresh flow as an integrated solution.

- **Status:** Proposed
- **Date:** 2026-01-01
- **Feature:** Cross-cutting (affects all authenticated endpoints)
- **Context:** Scalability and Performance

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: YES - Long-term architectural decision affecting performance, scalability, and security
     2) Alternatives: YES - Multiple viable options (pure JWT, Redis caching, current DB sessions, hybrid)
     3) Scope: YES - Cross-cutting concern affecting all API authentication
-->

## Context

The current authentication implementation uses **better-auth with database-backed session tokens**, which performs a PostgreSQL query on **every authenticated request** to validate the session token (see `backend/src/services/auth_service.py:89-94`).

### Current Implementation Performance
- **At 100 users** (10 req/min each): ~17 auth queries/second
- **At 1,000 users**: ~167 auth queries/second
- **Database roundtrip latency**: 5-20ms per request
- **Overhead**: Every API call includes DB query even for valid sessions

### Scalability Concerns
- Database becomes a bottleneck at scale (hundreds of concurrent users)
- Connection pool exhaustion risk
- Increased latency on every request
- Vertical scaling required (more expensive DB tier)

### Requirements
- Support 1,000+ concurrent users
- Maintain session revocation capability
- Preserve audit trail (IP, user agent, session list)
- Keep user experience unchanged (7-day login sessions)
- Reduce database load by 90%+

## Decision

Implement **Hybrid JWT Authentication** with two-token system:

### Architecture Components

1. **Access Token (JWT)**
   - Type: JSON Web Token (signed with HS256)
   - Lifetime: 30 minutes (short-lived)
   - Storage: Frontend memory/localStorage
   - Validation: Signature verification only (NO database query)
   - Claims: `{sub: user_id, exp, iat, type: "access"}`
   - Library: PyJWT (Python), jose/jsonwebtoken (Node.js)

2. **Refresh Token (Opaque)**
   - Type: Cryptographically secure random string (32 bytes)
   - Lifetime: 7 days (long-lived)
   - Storage: PostgreSQL `user_sessions` table (reuse existing schema)
   - Validation: Database lookup (only when refreshing)
   - Purpose: Issue new access tokens

3. **Validation Flow**
   - **99% of requests**: JWT signature check (CPU-only, ~0.5ms, no DB query)
   - **1% of requests**: Token refresh via `/api/auth/refresh` endpoint (DB query)
   - Refresh happens automatically in frontend (transparent to user)

4. **Session Management**
   - Refresh tokens stored in `user_sessions` table (same as current implementation)
   - Enables session listing, audit trail, and revocation
   - Deleting refresh token from DB = logout (access token expires within 30 min)

5. **Frontend Token Refresh**
   - HTTP interceptor detects 401 (token expired)
   - Automatically calls `/api/auth/refresh` with refresh token
   - Retries original request with new access token
   - User never sees logout or loading spinner

### Migration Strategy
- Phase 1: Implement JWT service alongside current session validation
- Phase 2: Update auth endpoints to issue both token types
- Phase 3: Gradual rollout with feature flag
- Phase 4: Monitor performance metrics
- Phase 5: Complete migration and remove old session validation

## Consequences

### Positive

1. **Massive Database Load Reduction**
   - 90-99% reduction in auth-related DB queries
   - At 1,000 users: 167 queries/sec → ~1 query/sec
   - Only DB query on token refresh (~every 15 min per user)

2. **Improved Request Latency**
   - Access token validation: ~0.5ms (vs 5-20ms DB query)
   - 95th percentile latency improvement: 10-30ms per request
   - More responsive user experience

3. **Horizontal Scalability**
   - Stateless access token validation
   - No shared session state required
   - Add FastAPI instances without scaling database
   - Better support for future microservices architecture

4. **Production-Ready Pattern**
   - Industry standard (Google, Facebook, GitHub, Auth0)
   - Well-documented security best practices
   - Extensive library ecosystem (PyJWT, python-jose)
   - Proven at massive scale

5. **Maintains All Current Features**
   - Session management UI (list/revoke sessions)
   - Audit trail (IP, user agent, timestamps)
   - 7-day login duration (same UX)
   - Immediate revocation via refresh token deletion

### Negative

1. **Delayed Revocation Window**
   - Access tokens remain valid for up to 30 minutes after logout/revocation
   - Acceptable for most applications (configurable to 15-20 min if needed)
   - For high-security scenarios: Can add Redis blacklist for immediate revocation

2. **Increased Code Complexity**
   - Two token types instead of one
   - Frontend refresh logic (HTTP interceptor)
   - Token refresh endpoint implementation
   - More comprehensive error handling

3. **Token Refresh Infrastructure**
   - New `/api/auth/refresh` endpoint
   - Frontend token storage management
   - Race condition handling (concurrent refresh requests)
   - Token rotation logic

4. **JWT Secret Management**
   - Requires secure secret key (min 32 characters)
   - Key rotation strategy needed for long-term security
   - Secret must be shared across all FastAPI instances

5. **Debugging Complexity**
   - Two-token flow can be harder to debug
   - JWT decoding required for troubleshooting
   - Need better logging for token lifecycle

## Alternatives Considered

### Alternative 1: Pure JWT (Stateless)
**Components**: Single JWT token (1-7 days), no database storage

**Pros**:
- Maximum performance (no DB queries ever)
- Simplest implementation
- True statelessness

**Cons**:
- ❌ No real-time revocation (security risk)
- ❌ No session management UI
- ❌ No audit trail
- ❌ Cannot logout users (tokens valid until expiry)

**Rejected because**: Loses critical features (revocation, session management) that are requirements for the application.

---

### Alternative 2: Redis Cache Layer (Keep DB Sessions)
**Components**: Current DB sessions + Redis cache (5-min TTL)

**Pros**:
- Simpler than JWT (keep existing code)
- 90-95% cache hit rate (similar DB reduction)
- Immediate revocation (cache invalidation)
- Keep all current features

**Cons**:
- Requires Redis infrastructure (additional dependency)
- Cache warming and invalidation complexity
- Still couples to session storage
- Cache stampede risk on mass invalidation
- Doesn't prepare for future microservices

**Rejected because**: While simpler short-term, doesn't provide the horizontal scalability and microservices-readiness that JWT offers. Redis caching is a good interim step but not the long-term solution.

---

### Alternative 3: Keep Current DB Sessions
**Components**: Current better-auth implementation (no changes)

**Pros**:
- Zero implementation effort
- No migration risk
- All features work as-is
- Simple debugging

**Cons**:
- ❌ Doesn't solve scalability problem
- ❌ Database remains bottleneck at scale
- ❌ High latency on every request
- ❌ Expensive vertical scaling required

**Rejected because**: Fails to address the core scalability concern that motivated this architectural review.

---

### Alternative 4: Short-lived DB Sessions (5-min TTL)
**Components**: Current implementation but with 5-min session cache in DB

**Pros**:
- Minimal code changes
- Keeps existing architecture
- Some DB load reduction

**Cons**:
- Still requires DB query on every request
- Users re-login every 5 minutes (poor UX)
- Doesn't solve fundamental scalability issue

**Rejected because**: Doesn't achieve the performance goals and degrades user experience.

---

## Why Hybrid JWT Was Chosen

The hybrid approach provides **the best tradeoffs**:

1. **Achieves 90-99% DB load reduction** (vs Redis 90-95%, Pure JWT 100%)
2. **Maintains all required features** (revocation, audit, session management)
3. **Industry-proven pattern** (Google, Auth0, GitHub use similar approaches)
4. **Acceptable revocation delay** (≤30 min vs immediate for Redis, hours for pure JWT)
5. **Prepares for microservices** (stateless validation enables distributed systems)
6. **Minimal user impact** (transparent token refresh, same 7-day login)

The 30-minute revocation window is an acceptable security tradeoff for the massive performance and scalability gains.

## Implementation Checklist

**Phase 1: Core JWT Authentication**
- [ ] Create JWT service (`backend/src/services/jwt_auth_service.py`)
- [ ] Implement token refresh endpoint (`POST /api/auth/refresh`)
- [ ] Update login/signup to issue both tokens
- [ ] Add JWT validation dependency (`backend/src/api/dependencies.py`)
- [ ] Update logout to revoke refresh token
- [ ] Write unit tests for JWT service
- [ ] Write integration tests for authentication flow

**Phase 2: Frontend Integration**
- [ ] Implement frontend HTTP interceptor for auto-refresh
- [ ] Add token storage in frontend (memory + httpOnly cookie for refresh)
- [ ] Handle token expiration and refresh errors
- [ ] Update frontend authentication state management

**Phase 3: Monitoring & Documentation**
- [ ] Add monitoring metrics (refresh rate, token validation time)
- [ ] Document migration strategy in deployment guide
- [ ] Update API documentation with new authentication flow

**Future Enhancements (Out of Scope)**
- [ ] Session management UI (view active sessions, revoke specific sessions)
- [ ] "Logout from all devices" functionality
- [ ] Token rotation on refresh
- [ ] Redis-based token blacklisting for immediate revocation

## References

- Feature Spec: [specs/013-hybrid-jwt-auth/spec.md](../../specs/013-hybrid-jwt-auth/spec.md)
- Implementation Plan: Not needed (this ADR provides sufficient architectural detail)
- Related ADRs: None (first authentication architecture decision)
- Technical Discussion: Conversation on 2026-01-01 covering scalability analysis, performance benchmarks, and tradeoff evaluation

## Security Considerations

1. **JWT Secret**: Use `BETTER_AUTH_SECRET` (already 32+ characters, cryptographically secure)
2. **Token Storage**:
   - Access token: Memory/localStorage (short-lived, acceptable risk)
   - Refresh token: httpOnly cookie (prevents XSS theft)
3. **HTTPS Required**: All tokens transmitted over HTTPS in production
4. **Signature Algorithm**: HS256 (HMAC-SHA256, symmetric signing)
5. **Token Rotation**: Refresh tokens can be rotated on each refresh for added security
6. **Immediate Revocation** (if needed): Add Redis blacklist for revoked access token JTIs

## Performance Targets

| Metric | Current | Target (Hybrid JWT) |
|--------|---------|---------------------|
| Auth queries/sec (1000 users) | 167/sec | <5/sec |
| DB load reduction | 0% | 90-99% |
| Avg auth latency | 15ms | <1ms |
| Revocation latency | Immediate | ≤30 min |
| User session duration | 7 days | 7 days (unchanged) |

## Monitoring & Observability

Track these metrics post-implementation:
- Access token validation time (p50, p95, p99)
- Refresh token endpoint latency
- Refresh rate (requests/min)
- Failed token validations (expired, invalid signature)
- Database auth query rate (should drop 90%+)
- Session revocation usage patterns
