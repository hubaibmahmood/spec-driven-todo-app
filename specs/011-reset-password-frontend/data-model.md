# Data Model: Reset Password Frontend Integration

**Feature**: 011-reset-password-frontend
**Date**: 2025-12-27
**Type**: Frontend Data Structures

## Overview

This feature is **frontend-only** and does not define database entities. All data persistence is handled by the existing better-auth server (spec 004-auth-server) with Neon PostgreSQL. This document defines the **client-side data structures** (TypeScript interfaces) for form state, validation results, and API request/response types.

---

## Client-Side Data Structures

### 1. Form State Interfaces

#### ForgotPasswordFormState

Manages state for the forgot password page.

```typescript
interface ForgotPasswordFormState {
  // Input fields
  email: string;

  // UI state
  isLoading: boolean;
  error: string | null;
  successMessage: string | null;

  // Rate limiting
  rateLimitRemaining: number | null; // Seconds until next attempt allowed
}
```

**Usage**: State management for forgot password form component

**Validation Rules**:
- `email`: Required, valid email format (regex: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`)

---

#### ResetPasswordFormState

Manages state for the reset password page.

```typescript
interface ResetPasswordFormState {
  // Input fields
  newPassword: string;
  confirmPassword: string;

  // Token state
  token: string | null;
  tokenError: string | null;

  // UI state
  isLoading: boolean;
  showPassword: boolean;
  showConfirmPassword: boolean;
  error: string | null;

  // Validation state
  passwordValidation: PasswordValidation | null;
  passwordsMatch: boolean;
}
```

**Usage**: State management for reset password form component

**Validation Rules**:
- `newPassword`: Required, must pass password strength validation
- `confirmPassword`: Required, must match `newPassword`
- `token`: Required (extracted from URL), must match format `/^[A-Za-z0-9_-]{32,}$/`

---

### 2. Validation Interfaces

#### PasswordValidation

Result of password strength validation.

```typescript
interface PasswordValidation {
  isValid: boolean;
  errors: string[];
}
```

**Fields**:
- `isValid`: True if password meets all requirements
- `errors`: Array of validation error messages

**Validation Requirements** (from spec FR-007):
1. Minimum 8 characters
2. At least one uppercase letter (A-Z)
3. At least one lowercase letter (a-z)
4. At least one number (0-9)
5. At least one special character (!@#$%^&*()_+-=[]{};':"\\|,.<>/?)

**Example**:
```typescript
{
  isValid: false,
  errors: [
    "Password must contain at least one uppercase letter",
    "Password must contain at least one special character"
  ]
}
```

---

#### RateLimitCheck

Result of rate limit check.

```typescript
interface RateLimitCheck {
  allowed: boolean;
  remainingTime?: number; // Seconds until next attempt (if not allowed)
}
```

**Usage**: Check if user can submit another password reset request

**Example**:
```typescript
// Allowed
{ allowed: true }

// Rate limited
{ allowed: false, remainingTime: 240 } // 4 minutes remaining
```

---

### 3. API Request/Response Types

These types match the better-auth client SDK but are documented here for clarity.

#### ForgetPasswordRequest

```typescript
interface ForgetPasswordRequest {
  email: string;
  redirectTo?: string; // URL to redirect with token
}
```

**API Method**: `authClient.forgetPassword(request, options)`

**Example**:
```typescript
{
  email: "user@example.com",
  redirectTo: "https://momentum.intevia.cc/reset-password"
}
```

---

#### ForgetPasswordResponse

```typescript
interface ForgetPasswordResponse {
  success: boolean;
  message: string;
}
```

**Note**: Generic message returned regardless of email existence (email enumeration prevention)

**Example**:
```typescript
{
  success: true,
  message: "Password reset email sent if user exists."
}
```

---

#### ResetPasswordRequest

```typescript
interface ResetPasswordRequest {
  newPassword: string;
  token: string;
}
```

**API Method**: `authClient.resetPassword(request, options)`

**Example**:
```typescript
{
  newPassword: "SecurePass123!",
  token: "abc123def456ghi789jkl012mno345pqr"
}
```

---

#### ResetPasswordResponse

```typescript
interface ResetPasswordResponse {
  success: boolean;
  user?: {
    id: string;
    email: string;
    name: string;
  };
}
```

**Example Success**:
```typescript
{
  success: true,
  user: {
    id: "user_123",
    email: "user@example.com",
    name: "John Doe"
  }
}
```

**Example Error** (handled in onError callback):
```typescript
{
  error: {
    status: 400,
    message: "Invalid or expired token"
  }
}
```

---

### 4. Error Types

#### PasswordResetError

Standardized error structure for password reset operations.

```typescript
interface PasswordResetError {
  type: 'network' | 'validation' | 'token' | 'rate_limit' | 'server' | 'unknown';
  message: string;
  action?: 'retry' | 'wait' | 'request_new';
  retryAfter?: number; // Seconds (for rate limit errors)
}
```

**Error Type Mapping**:

| Type | Scenario | User Message | Action |
|------|----------|--------------|--------|
| `network` | No internet, timeout | "Unable to connect. Please check your internet connection." | `retry` |
| `validation` | Password doesn't meet requirements | "Password must be at least 8 characters..." | (inline) |
| `token` | Invalid or expired token | "This reset link has expired. Please request a new one." | `request_new` |
| `rate_limit` | Too many requests | "Too many attempts. Please wait 5 minutes." | `wait` |
| `server` | 500 errors | "Something went wrong on our end. Please try again." | `retry` |
| `unknown` | Unexpected error | "An unexpected error occurred. Please try again." | `retry` |

---

### 5. LocalStorage Data Structures

#### RateLimitEntry

Stored in localStorage for client-side rate limiting.

```typescript
interface RateLimitEntry {
  email: string;
  attempts: number;
  firstAttemptAt: number; // Unix timestamp (ms)
}
```

**Storage Key**: `password_reset_rate_limit`

**Storage Format**: JSON array of `RateLimitEntry[]`

**Example**:
```json
[
  {
    "email": "user@example.com",
    "attempts": 2,
    "firstAttemptAt": 1703692800000
  }
]
```

**Cleanup Policy**: Entries older than 5 minutes are automatically removed

---

## State Transitions

### Forgot Password Flow

```
[Initial State]
  ↓
[User enters email]
  ↓
[Client-side validation]
  ↓ (valid)
[Check rate limit]
  ↓ (allowed)
[Submit to better-auth API]
  ↓
[Show generic success message]
  ↓
[Record attempt in localStorage]
  ↓
[User checks email]
```

### Reset Password Flow

```
[Page loads with token in URL]
  ↓
[Extract and validate token format]
  ↓ (valid format)
[User enters new password]
  ↓
[Real-time password validation]
  ↓ (valid)
[User enters confirmation]
  ↓
[Check passwords match]
  ↓ (match)
[Submit to better-auth API with token]
  ↓
[Sign out if session exists]
  ↓
[Redirect to login with success message]
```

---

## Data Flow Diagram

```
┌─────────────────┐
│  Browser URL    │ /reset-password?token=abc123...
│  (Query Params) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ useSearchParams │ Extract token
│   (Next.js)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Token Validator │ Regex validation
│  (Client-side)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Form Component │ User input
│   (React State) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Password        │ Strength validation
│  Validator      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ authClient      │ API request
│ .resetPassword  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Better-Auth     │ Token verification
│    Server       │ Password update
│ (spec 004)      │ Session invalidation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Success/Error  │ User feedback
│    Callback     │ Redirect to login
└─────────────────┘
```

---

## Validation Rules Summary

### Client-Side Validations

| Field | Validation | Error Message |
|-------|------------|---------------|
| Email (forgot) | Required, valid format | "Please enter a valid email address" |
| New Password | Min 8 chars | "Password must be at least 8 characters" |
| New Password | Contains uppercase | "Password must contain at least one uppercase letter" |
| New Password | Contains lowercase | "Password must contain at least one lowercase letter" |
| New Password | Contains number | "Password must contain at least one number" |
| New Password | Contains special char | "Password must contain at least one special character" |
| Confirm Password | Matches new password | "Passwords do not match" |
| Reset Token | Present in URL | "No reset token provided" |
| Reset Token | Valid format | "Invalid reset link format" |

### Server-Side Validations

(Handled by better-auth server, spec 004)

| Field | Validation | Error Response |
|-------|------------|----------------|
| Email | User exists | Generic success (no enumeration) |
| Token | Not expired (<1 hour) | "Invalid or expired token" |
| Token | Valid signature | "Invalid token" |
| Password | Meets strength requirements | "Password does not meet requirements" |

---

## Notes

- **No Database Changes**: This feature does not modify the database schema. All persistence is handled by the existing better-auth server.
- **Ephemeral Data**: Form state exists only in React component memory and is lost on page refresh.
- **localStorage Usage**: Only used for client-side rate limiting (non-critical data, graceful degradation if unavailable).
- **Type Safety**: All interfaces use TypeScript for compile-time type checking and IDE autocomplete.
- **API Contract**: Follows better-auth v1.4.6 client SDK types (no custom backend endpoints).
