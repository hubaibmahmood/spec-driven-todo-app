# API Contract: Better-Auth Password Reset Endpoints

**Feature**: 011-reset-password-frontend
**Date**: 2025-12-27
**Provider**: better-auth server (spec 004-auth-server)
**Client**: better-auth React SDK v1.4.6

## Overview

This document defines the API contract between the frontend password reset feature and the existing better-auth server. The frontend uses the better-auth React client SDK which abstracts HTTP calls to these endpoints.

**Important**: This feature does NOT create new backend endpoints. It integrates with existing better-auth server endpoints deployed in spec 004-auth-server.

---

## Endpoint 1: Request Password Reset

### HTTP Details

```
POST /api/auth/request-password-reset
Content-Type: application/json
```

### Client SDK Method

```typescript
authClient.forgetPassword(request, options)
```

### Request

**Schema**:
```typescript
{
  email: string;        // Required - User's email address
  redirectTo?: string;  // Optional - URL to redirect with token
}
```

**Example**:
```json
{
  "email": "user@example.com",
  "redirectTo": "https://momentum.intevia.cc/reset-password"
}
```

**Validation**:
- `email`: Must be valid email format
- `redirectTo`: Must be valid URL (if provided)

### Response

**Success Response** (200 OK):
```json
{
  "message": "Password reset email sent if user exists."
}
```

**Note**: Generic message returned regardless of whether the email exists in the database (prevents email enumeration attacks per FR-004).

**Error Responses**:

| Status Code | Scenario | Response Body | Frontend Handling |
|-------------|----------|---------------|-------------------|
| 400 | Invalid email format | `{"error": "Invalid email"}` | Show validation error |
| 429 | Rate limit exceeded | `{"error": "Too many requests"}` | Show "Too many attempts" message |
| 500 | Server error | `{"error": "Internal server error"}` | Show "Something went wrong" message |
| 503 | Email service unavailable | `{"error": "Service unavailable"}` | Show "Unable to send email" message |

### Side Effects

**If email exists in database**:
1. Generate secure reset token (32+ character random string)
2. Store token in database with 1-hour expiration
3. Send email via Resend service with reset link: `{redirectTo}?token={token}`
4. Email subject: "Reset your password"

**If email does NOT exist**:
1. No email sent
2. No token generated
3. Same response returned (security)

### Rate Limiting

- **Server-side**: 5 requests per email per hour (enforced by better-auth)
- **Client-side**: 2 requests per email per 5 minutes (enforced by frontend per FR-004a)

---

## Endpoint 2: Reset Password

### HTTP Details

```
POST /api/auth/reset-password
Content-Type: application/json
```

### Client SDK Method

```typescript
authClient.resetPassword(request, options)
```

### Request

**Schema**:
```typescript
{
  newPassword: string;  // Required - New password meeting strength requirements
  token: string;        // Required - Token from reset email URL
}
```

**Example**:
```json
{
  "newPassword": "SecurePassword123!",
  "token": "abc123def456ghi789jkl012mno345pqr"
}
```

**Validation**:
- `newPassword`: Must meet password strength requirements (8+ chars, uppercase, lowercase, number, special char)
- `token`: Must be 32+ character alphanumeric string

### Response

**Success Response** (200 OK):
```json
{
  "success": true,
  "user": {
    "id": "user_123abc",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Error Responses**:

| Status Code | Scenario | Response Body | Frontend Handling |
|-------------|----------|---------------|-------------------|
| 400 | Token expired (>1 hour) | `{"error": "Token expired"}` | Show "Link expired, request new one" |
| 400 | Invalid token | `{"error": "Invalid token"}` | Show "Invalid link, request new one" |
| 400 | Password too weak | `{"error": "Password requirements not met"}` | Show validation errors |
| 404 | Token not found | `{"error": "Token not found"}` | Show "Invalid link" |
| 500 | Server error | `{"error": "Internal server error"}` | Show "Something went wrong" |

### Side Effects

**On success**:
1. Update user's password hash in database
2. Invalidate the reset token (single-use only)
3. Invalidate ALL active sessions for the user (security measure per FR-013a)
4. Return user object

**On failure**:
1. Token remains valid (if not expired)
2. No password change
3. No session invalidation

### Security Considerations

1. **Token Validation**:
   - Must exist in database
   - Must not be expired (<1 hour since creation)
   - Must not have been used previously
   - Must match the token signature

2. **Password Hashing**:
   - New password is hashed using bcrypt (handled by better-auth)
   - Original password is never logged or stored

3. **Session Invalidation**:
   - All sessions (across all devices) are terminated
   - User must log in again with new password
   - Prevents account takeover if password reset was malicious

---

## Data Flow

### Forgot Password Flow

```
[Frontend Form]
      │
      ▼ authClient.forgetPassword({ email, redirectTo })
[Better-Auth Server]
      │
      ├─▶ [Validate email format]
      │
      ├─▶ [Check rate limit]
      │
      ├─▶ [Lookup user in PostgreSQL]
      │       │
      │       ├─▶ Found: Generate token, send email
      │       └─▶ Not found: (no action)
      │
      └─▶ [Return generic success message]
            │
            ▼
      [Frontend: Show success message]
            │
            ▼
      [User: Check email inbox]
            │
            ▼
      [Email: Click reset link]
            │
            ▼
      [Frontend: Load /reset-password?token=...]
```

### Reset Password Flow

```
[Frontend Page Loads]
      │
      ▼ Extract token from URL
[Token Validation (client-side format check)]
      │
      ▼ User enters new password
[Password Validation (client-side)]
      │
      ▼ authClient.resetPassword({ newPassword, token })
[Better-Auth Server]
      │
      ├─▶ [Validate token in database]
      │       │
      │       ├─▶ Valid: Continue
      │       └─▶ Invalid/Expired: Return error
      │
      ├─▶ [Validate password strength]
      │
      ├─▶ [Hash new password]
      │
      ├─▶ [Update user password in PostgreSQL]
      │
      ├─▶ [Invalidate reset token]
      │
      ├─▶ [Invalidate ALL user sessions]
      │
      └─▶ [Return success with user object]
            │
            ▼
      [Frontend: Sign out if session exists]
            │
            ▼
      [Frontend: Redirect to /login?reset=success]
```

---

## Authentication & Authorization

### Forgot Password Endpoint

- **Authentication**: NOT required (public endpoint)
- **Authorization**: N/A (anyone can request password reset for any email)
- **Rate Limiting**: Required (prevents abuse)

### Reset Password Endpoint

- **Authentication**: NOT required (token serves as authentication)
- **Authorization**: Token proves user owns the email address
- **Rate Limiting**: NOT required (token is single-use and time-limited)

---

## Error Handling Guidelines

### Frontend Error Handling Strategy

```typescript
authClient.forgetPassword(request, {
  onSuccess: (ctx) => {
    // Always show generic success message (no email enumeration)
    setSuccessMessage("If an account exists, we've sent a reset link.");
  },
  onError: (ctx) => {
    // Handle specific error codes
    switch (ctx.error.status) {
      case 429:
        setError("Too many attempts. Please wait and check your email.");
        break;
      case 503:
        setError("Email service unavailable. Please try again later.");
        break;
      default:
        setError("Something went wrong. Please try again.");
    }
  }
});
```

### User-Facing Error Messages

| Backend Error | User Message | Action Button |
|---------------|--------------|---------------|
| Token expired | "This reset link has expired. Reset links are valid for 1 hour." | "Request New Reset Link" |
| Invalid token | "This reset link is invalid. Please request a new one." | "Request New Reset Link" |
| Password weak | "Password must be at least 8 characters with uppercase, lowercase, number, and special character." | (Inline validation) |
| Network error | "Unable to connect. Please check your internet connection and try again." | "Retry" |
| Rate limit (429) | "Too many attempts. Please check your email or wait 5 minutes before trying again." | (Disabled for 5 min) |
| Server error (500) | "Something went wrong on our end. Please try again in a few moments." | "Retry" |

---

## Testing Scenarios

### Happy Path

1. **Forgot Password**:
   - User submits valid email
   - Receives generic success message
   - Email arrives within 1 minute
   - Email contains valid reset link

2. **Reset Password**:
   - User clicks link from email
   - Page loads with valid token
   - User enters strong password
   - Password is accepted
   - Redirected to login
   - Can log in with new password

### Edge Cases

1. **Email Not Found**:
   - Request returns same success message
   - No email sent

2. **Expired Token**:
   - User clicks link >1 hour after request
   - Receives "expired" error
   - Link to request new reset

3. **Already Used Token**:
   - User completes reset
   - Tries to use same link again
   - Receives "invalid" error

4. **Rate Limit**:
   - User requests reset 3 times in 5 minutes
   - 3rd request receives 429 error
   - Told to wait 5 minutes

5. **Malformed Token**:
   - User modifies token in URL
   - Client-side validation catches malformed format
   - Server-side validation rejects invalid token

6. **User Already Logged In**:
   - User with active session resets password
   - Password reset succeeds
   - All sessions invalidated (including current)
   - Redirected to login

---

## Monitoring & Observability

### Metrics to Track (Backend)

- Password reset request rate (per email, per IP)
- Email delivery success rate (Resend API)
- Token expiration rate (unused tokens)
- Reset completion rate (token used vs. generated)
- Error rate by type (expired, invalid, etc.)

### Frontend Analytics

- Forgot password page views
- Reset password page views
- Form submission success rate
- Error types encountered
- Time to complete flow (request → reset)

---

## Notes

- **Email Template**: Configured in better-auth server (spec 004) using Resend service
- **Token Storage**: PostgreSQL database (Neon serverless)
- **Token Format**: 32+ character random alphanumeric string (generated by better-auth)
- **Token Expiration**: 1 hour (hardcoded in better-auth configuration)
- **Session Management**: Handled automatically by better-auth (invalidates all sessions on password reset)
- **CORS**: Configured in better-auth server to allow frontend domain
- **HTTPS**: Required in production (enforced by Vercel deployment)
