# Feature Specification: Hybrid JWT Authentication

**Feature Branch**: `013-hybrid-jwt-auth`
**Created**: 2026-01-01
**Updated**: 2026-01-03 (Full JWT Migration)
**Status**: In Progress
**Input**: User description: "Hybrid JWT Authentication for Scalable Session Management - Full Migration"
**Related ADR**: [ADR-0004: Hybrid JWT Authentication Architecture](../../history/adr/0004-hybrid-jwt-authentication-architecture.md)

**Migration Strategy**: Full JWT migration - replacing session-based authentication with JWT (access + refresh tokens) across all services

## Clarifications

### Session 2026-01-02

- Q: What is your preferred migration strategy for transitioning from session-based to JWT authentication? → A: Feature flag-based gradual rollout (new users get JWT, old users keep sessions, configurable percentage rollout)
- Q: How should refresh tokens be stored in the database to balance security and implementation complexity? → A: Hash refresh tokens before storage (use bcrypt or SHA-256, validate by hashing incoming token and comparing) - Industry best practice
- Q: When multiple browser tabs detect token expiration simultaneously, how should concurrent token refresh be handled? → A: Shared lock with single refresh (one tab refreshes and broadcasts new token to other tabs via localStorage/BroadcastChannel - most efficient, best UX)
- Q: How many retry attempts should the client make when the token refresh endpoint fails due to network errors? → A: 3 retry attempts with exponential backoff: 1s, 2s, 4s delays (industry standard, balances recovery vs UX)
- Q: What cookie security attributes should be used for refresh token httpOnly cookies? → A: SameSite=Strict, Secure, HttpOnly (strongest security, prevents CSRF, requires re-login from external links)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Seamless Long-Duration Sessions (Priority: P1)

As a registered user, I want to stay logged in for 7 days without re-entering my credentials, so that I can access my tasks conveniently across multiple sessions without authentication friction.

**Why this priority**: Core user experience requirement. Users expect modern web applications to maintain authenticated sessions without frequent re-login prompts. This is the baseline authentication experience that must work flawlessly.

**Independent Test**: Can be fully tested by logging in once, closing the browser, returning after hours/days (within 7 days), and confirming tasks are still accessible without re-authentication. Delivers immediate value by eliminating login friction.

**Acceptance Scenarios**:

1. **Given** a user has successfully logged in, **When** they close and reopen their browser within 7 days, **Then** they remain authenticated and can access their tasks immediately
2. **Given** a user has been inactive for 20 minutes, **When** they return and perform any action, **Then** the action succeeds without requiring re-login
3. **Given** a user's session is 6 days and 23 hours old, **When** they perform an action, **Then** the action succeeds and they remain authenticated
4. **Given** a user's session is exactly 7 days old, **When** they attempt to perform an action, **Then** they are redirected to login with a message "Your session has expired. Please log in again."

---

### User Story 2 - Transparent Token Refresh (Priority: P1)

As a user actively using the application, I want my authentication to renew automatically in the background, so that I never experience unexpected logouts or interruptions during my workflow.

**Why this priority**: Critical for user experience. Silent token refresh is the mechanism that makes P1 (long sessions) work without database bottlenecks. Without this, users would be logged out every 30 minutes.

**Independent Test**: Can be tested by using the application continuously for 60+ minutes (spanning multiple 30-minute access token expirations), monitoring network requests, and confirming that token refresh happens automatically without user-visible interruptions. Delivers value by maintaining session continuity.

**Acceptance Scenarios**:

1. **Given** a user's access token has expired (30 minutes since last refresh), **When** they perform any action (e.g., create a task), **Then** the system automatically refreshes their token in the background and completes the action without showing a login prompt
2. **Given** a user is actively working, **When** their access token expires during a request, **Then** the request retries automatically with a new token and completes successfully
3. **Given** a user has been idle for 8 days, **When** they return and try to use the app, **Then** they are prompted to log in again (refresh token expired)
4. **Given** the token refresh endpoint fails (network error), **When** the user retries their action, **Then** the system attempts to refresh again before showing an error

---

### User Story 3 - Explicit Logout (Priority: P2)

As a user finishing my work session, I want to explicitly log out, so that my account is secure especially when using shared or public computers.

**Why this priority**: Essential security feature. Users who explicitly logout expect immediate effect, especially when using shared or public computers.

**Independent Test**: Can be tested by logging in, clicking logout, and confirming that all subsequent requests require re-authentication. Delivers security value independently.

**Acceptance Scenarios**:

1. **Given** a user is authenticated, **When** they click the "Logout" button, **Then** their refresh token is deleted from the system and they are redirected to the login page
2. **Given** a user has logged out, **When** they try to access a protected page, **Then** they are redirected to login
3. **Given** a user has logged out, **When** their previous access token is still valid (<30 minutes), **Then** API requests with that token may still succeed until the token expires (acceptable 30-minute window)
4. **Given** a user has logged out, **When** 30 minutes pass, **Then** no requests can be made with the old tokens (both access and refresh are invalidated)

---

### User Story 4 - Performance and Scalability (Priority: P3)

As a system operator monitoring application performance, I want authentication to impose minimal database load, so that the application can support thousands of concurrent users without requiring expensive database scaling.

**Why this priority**: Performance optimization that enables future growth but doesn't affect current user experience. This is the architectural benefit that justifies the hybrid JWT approach.

**Independent Test**: Can be tested by monitoring database query rates during load testing (1000+ concurrent users) and confirming that authentication-related queries are <1% of what they would be with database-only sessions. Delivers scalability value measurable through metrics.

**Acceptance Scenarios**:

1. **Given** 1000 concurrent users making 10 requests per minute each, **When** monitoring database queries, **Then** authentication validation queries are less than 5 per second (vs 167/sec with old approach)
2. **Given** a user makes 10 API requests within 30 minutes, **When** reviewing database logs, **Then** only 0-1 authentication queries occurred (0 if access token valid, 1 if refresh was needed)
3. **Given** the application is under normal load, **When** measuring API response times, **Then** average authentication overhead is <1ms (vs 15ms with database sessions)
4. **Given** load testing with 2000 concurrent users, **When** measuring system resource usage, **Then** database CPU usage related to authentication is <5% of total load

---

### Edge Cases

- **What happens when a user's access token expires during a multi-step operation (e.g., file upload)?**
  - System should queue the operation, refresh the token, and retry with the new token automatically
  - User should not see the upload fail or have to restart

- **What happens when multiple tabs refresh tokens simultaneously?**
  - Frontend implements cross-tab coordination using localStorage events or BroadcastChannel API
  - First tab to detect expiration acquires a refresh lock (timestamp-based lock in localStorage)
  - Other tabs detect the lock and enter waiting state (poll for new token in localStorage)
  - Refreshing tab completes request, broadcasts new access token to all tabs via storage event/BroadcastChannel
  - All tabs update their in-memory access token and resume pending requests
  - No duplicate refresh requests sent to server (only one HTTP call)
  - Lock expires after 5 seconds (fallback for crashed tab scenarios)

- **What happens when the token refresh endpoint is temporarily unavailable?**
  - Client implements exponential backoff retry: 3 attempts with 1s, 2s, and 4s delays (total ~7 seconds)
  - Network/server errors (500, timeout, connection refused) trigger retries
  - Authentication errors (401, 403) skip retries and redirect to login immediately
  - After all retries exhausted, user sees "Unable to connect. Please check your connection and try again." message
  - Once network recovers and user retries action, normal refresh flow resumes
  - User is only logged out if refresh token has actually expired (7 days) or was revoked

- **What happens when a user changes their password while having active sessions?**
  - All existing refresh tokens remain valid (session list unchanged)
  - User can explicitly revoke all sessions if desired
  - Alternative: Future enhancement could auto-revoke all sessions on password change

- **What happens when the JWT secret key is rotated?**
  - Existing access tokens signed with old key become invalid
  - Users are forced to refresh (using their refresh tokens from DB)
  - New access tokens signed with new key
  - Graceful rotation: Support both old and new keys for a transition period

- **What happens when a user's refresh token is deleted from database (e.g., admin action)?**
  - Access token works until expiration (≤30 minutes)
  - When client tries to refresh, request fails with 401
  - User is redirected to login page
  - Clear error message: "Your session has been terminated. Please log in again."

- **What happens when browser localStorage is cleared while user is authenticated?**
  - Access token is lost from memory/localStorage
  - Refresh token still exists in httpOnly cookie
  - Next request triggers automatic token refresh
  - User stays logged in (seamless recovery)

- **What happens when a user manually modifies their access token?**
  - JWT signature validation fails
  - Request returns 401 Unauthorized
  - Client attempts automatic refresh with refresh token
  - User continues working (assuming refresh token is valid)

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & Token Management

- **FR-001**: System MUST issue two separate tokens upon successful login: a short-lived access token (30 minutes) and a long-lived refresh token (7 days)
- **FR-002**: System MUST validate access tokens using cryptographic signature verification without querying the database for 99% of authenticated requests
- **FR-003**: System MUST provide a token refresh endpoint that accepts a valid refresh token and returns a new access token
- **FR-004**: System MUST hash refresh tokens (using SHA-256 or bcrypt) before storing in the database to prevent token theft in case of database compromise. Database records MUST include: hashed refresh token, user association, expiration timestamp, IP address, and user agent for audit purposes. Token validation MUST hash the incoming token and compare against stored hash.
- **FR-005**: System MUST reject expired access tokens (>30 minutes old) with a 401 status code and "token_expired" error code
- **FR-006**: System MUST reject expired refresh tokens (>7 days old) and require user to log in again
- **FR-007**: System MUST generate access tokens containing user ID, expiration timestamp, issued-at timestamp, and token type claim
- **FR-008**: System MUST delete the refresh token from database when user explicitly logs out
- **FR-009**: System MUST prevent revoked sessions from refreshing access tokens (refresh endpoint returns 401)

#### Client-Side Token Refresh

- **FR-010**: Frontend MUST implement an HTTP request interceptor that detects 401 responses with "token_expired" error code
- **FR-011**: Frontend MUST automatically call the token refresh endpoint when access token expires
- **FR-012**: Frontend MUST retry the original failed request with the new access token after successful refresh
- **FR-013**: Frontend MUST store access tokens in memory or localStorage (short-lived, acceptable risk)
- **FR-014**: System MUST store refresh tokens in httpOnly cookies with the following security attributes: `HttpOnly=true` (prevents XSS theft), `Secure=true` (HTTPS-only transmission), `SameSite=Strict` (prevents CSRF attacks, blocks cross-site requests), and appropriate `Max-Age` (7 days). Note: SameSite=Strict requires users clicking links from external sites (emails, messages) to re-authenticate, which is acceptable for security.
- **FR-015**: Frontend MUST implement retry logic for token refresh failures with exponential backoff: maximum 3 retry attempts with delays of 1 second, 2 seconds, and 4 seconds respectively (total ~7 seconds). After all retries are exhausted, redirect user to login page with appropriate error message.
- **FR-016**: Frontend MUST distinguish between network/server errors (retry with backoff) and authentication errors (401/403 - redirect to login immediately without retries)
- **FR-017**: Frontend MUST implement cross-tab token synchronization to prevent duplicate refresh requests when multiple tabs detect expiration simultaneously. Implementation MUST use one of: localStorage events, BroadcastChannel API, or shared worker to coordinate refresh across tabs. Only one tab MUST execute the refresh request; other tabs MUST wait and reuse the new token broadcast from the refreshing tab.

#### Security

- **FR-018**: System MUST sign access tokens using HMAC-SHA256 (HS256) algorithm with a secure secret key (minimum 32 characters)
- **FR-019**: System MUST transmit all tokens over HTTPS in production environments
- **FR-020**: System MUST use the same secret key across all backend instances for consistent token validation
- **FR-021**: System MUST validate JWT signatures using constant-time comparison to prevent timing attacks
- **FR-022**: System MUST generate refresh tokens using cryptographically secure random number generation (32 bytes minimum)

#### Migration Strategy

- **FR-023**: System MUST fully migrate from session-based to JWT-based authentication across all services (backend, AI agent, frontend)
- **FR-024**: System MUST use JWT exclusively for user authentication - all authenticated requests use JWT access tokens in Authorization header

#### Monitoring & Observability

- **FR-025**: System MUST log token refresh events with user ID, timestamp, and success/failure status
- **FR-026**: System MUST expose metrics for: token validation time (p50, p95, p99), refresh rate (requests/min), failed validations, and database auth query rate
- **FR-027**: System MUST log logout events with user ID, timestamp, and session identifier

### Key Entities

- **Access Token (JWT)**: A cryptographically signed token containing user identity claims. Issued for 30 minutes, validated via signature check (no database lookup). Stored in browser memory/localStorage.

- **Refresh Token**: An opaque, cryptographically secure random string (32+ bytes). Issued for 7 days, hashed (SHA-256 or bcrypt) before database storage to prevent theft in case of database compromise. Transmitted via httpOnly cookie with security attributes (HttpOnly=true, Secure=true, SameSite=Strict, Max-Age=7 days) to prevent XSS theft and CSRF attacks. Used exclusively to obtain new access tokens. Validation performed by hashing incoming token and comparing against stored hash.

- **Session Record**: Database entity representing an active user session. Contains hashed refresh token (SHA-256/bcrypt hash of the original token), user ID, expiration timestamp, IP address, user agent, device information, and creation timestamp. Enables session listing, audit trail, and revocation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users remain authenticated for 7 consecutive days without re-login prompts, measurable by session duration analytics showing median session length ≥7 days for active users
- **SC-002**: Authentication-related database queries reduce by at least 90% compared to current implementation, measurable by database query logs showing <10 auth queries per second at 1000 concurrent users (vs 167/sec baseline)
- **SC-003**: Average authentication validation latency improves to <1 millisecond, measurable by application performance monitoring (APM) showing p95 auth validation time <1ms (vs 15ms baseline)
- **SC-004**: Users experience zero visible interruptions or logout prompts during active usage across multiple 30-minute periods, measurable by tracking zero "unexpected logout" error reports and zero failed requests due to token expiration (excluding actual 7-day expiry)
- **SC-005**: 95% of token refresh operations complete in under 100 milliseconds, measurable by monitoring token refresh endpoint latency
- **SC-006**: Session revocation takes effect within 30 minutes for all access token requests, measurable by testing revoked session access attempt failures after revocation delay window
- **SC-007**: Application supports 1000+ concurrent users without authentication becoming a bottleneck, measurable by load testing showing consistent <50ms total API response time (including auth) at 1000+ concurrent users
- **SC-008**: Zero production incidents related to token validation failures or session inconsistencies in first 30 days post-deployment, measurable by incident tracking system
- **SC-009**: All services (backend API, AI agent, frontend) successfully migrate to JWT authentication with zero authentication failures, measurable by 100% JWT usage in production logs

## Assumptions

The following assumptions were made where the feature description did not provide explicit details:

1. **Token Lifetimes**: 30-minute access tokens and 7-day refresh tokens balance security and user experience while minimizing refresh frequency. This is within industry-standard ranges (15-60 minutes for access tokens).

2. **User Experience**: Users expect modern web application authentication to "just work" without frequent login prompts. Silent token refresh is the standard mechanism to achieve this.

3. **Security Tradeoff**: A 30-minute revocation delay (the access token lifetime) is an acceptable security tradeoff for massive performance gains. For most applications, this window is not a critical risk. High-security applications can reduce access token lifetime to 15 minutes if needed.

4. **Database Schema**: The existing `user_sessions` table from better-auth can be reused for storing refresh tokens, minimizing schema changes and migration complexity.

5. **Frontend Capability**: The frontend framework supports HTTP request interceptors (standard in modern frameworks like React, Angular, Vue with axios/fetch wrappers).

6. **Deployment Environment**: Production environment uses HTTPS for all API communication (required for secure token transmission).

7. **Secret Management**: The existing `BETTER_AUTH_SECRET` environment variable (32+ characters) can be reused as the JWT signing secret, avoiding additional secret management infrastructure.

8. **Migration Strategy**: Full migration to JWT authentication is required across all services. Session-based authentication will be completely replaced with JWT (access + refresh tokens).

9. **Service-to-Service Authentication**: MCP server continues using service-to-service authentication (X-User-ID header + SERVICE_AUTH_TOKEN) for internal service communication. Only user-facing authentication migrates to JWT.

10. **Monitoring Infrastructure**: Application performance monitoring (APM) tools are available for tracking latency metrics and query rates.

11. **Browser Support**: Target browsers support httpOnly cookies and localStorage (all modern browsers).

## Out of Scope

The following are explicitly excluded from this feature specification:

1. **Session Management UI**: Viewing active sessions across devices, revoking individual sessions, and "logout from all devices" functionality is not included in this specification. Users can only logout from their current device. Session management features can be added in a future iteration.

2. **Immediate Revocation**: Access tokens that are revoked will remain valid for up to 30 minutes. Implementing Redis-based token blacklisting for immediate revocation is not included in this spec but can be added as a future enhancement if needed.

3. **Token Rotation**: Rotating refresh tokens on each use (issuing a new refresh token with each access token refresh) is not included but can be added as a security enhancement.

4. **Multi-Factor Authentication (MFA)**: Any MFA-related changes or integration with MFA flows are outside the scope of this authentication infrastructure change.

5. **OAuth2/Social Login**: Integration with third-party OAuth providers (Google, GitHub, etc.) is not part of this spec. This focuses on the session management mechanism, not authentication methods.

6. **Public Key Cryptography**: Using asymmetric keys (RS256) instead of symmetric keys (HS256) for JWT signing is not required for single-backend deployment but could be considered for future microservices architecture.

7. **Cross-Domain Authentication**: Sharing authentication across multiple domains or subdomains is not in scope. This assumes a single domain deployment.

8. **Device Fingerprinting**: Advanced device fingerprinting or anomaly detection for session security is not included.

9. **Auto-Logout on Password Change**: Automatically revoking all sessions when user changes password is not required in this iteration.

10. **JWT Key Rotation**: Automated JWT secret key rotation is not in scope, though the architecture should support manual rotation if needed in the future.

## Dependencies

1. **ADR-0004**: This specification implements the architecture defined in [ADR-0004: Hybrid JWT Authentication Architecture](../../history/adr/0004-hybrid-jwt-authentication-architecture.md)

2. **Existing Authentication System**: This feature builds upon the existing better-auth session system and must maintain compatibility during migration.

3. **Database**: Requires PostgreSQL database with existing `user_sessions` table (reused for refresh tokens).

4. **Environment Variables**: Requires `BETTER_AUTH_SECRET` or equivalent JWT signing secret (minimum 32 characters).

5. **Frontend Framework**: Assumes frontend can implement HTTP interceptors for automatic token refresh.

6. **HTTPS**: Production deployment requires HTTPS for secure token transmission (development can use HTTP).

## Related Documentation

- [ADR-0004: Hybrid JWT Authentication Architecture](../../history/adr/0004-hybrid-jwt-authentication-architecture.md) - Architectural decision and alternatives analysis
- Current authentication implementation: `backend/src/services/auth_service.py` (session validation)
- Current authentication dependencies: `backend/src/api/dependencies.py` (get_current_user)
- Session database model: `backend/src/models/database.py` (UserSession)
