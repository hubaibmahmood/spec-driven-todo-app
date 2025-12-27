# Phase 0: Research - Reset Password Frontend Integration

**Feature**: 011-reset-password-frontend
**Date**: 2025-12-27
**Status**: Complete

## Research Questions & Findings

### 1. Better-Auth Client API for Password Reset

**Question**: What are the exact better-auth client methods for password reset, and what parameters do they accept?

**Decision**: Use `authClient.forgetPassword` and `authClient.resetPassword` methods

**Rationale**:
- Better-auth React client (v1.4.6) provides built-in password reset methods
- `forgetPassword({ email, redirectTo? })` - Triggers password reset email
- `resetPassword({ newPassword, token })` - Completes password reset with token
- Both methods support `fetchOptions` with `onRequest`, `onSuccess`, `onError` callbacks for UI state management
- Consistent with existing login/register implementation patterns in the codebase

**Alternatives Considered**:
1. **Custom API calls to better-auth endpoints** - Rejected: Bypasses type-safe client SDK, loses automatic error handling
2. **Third-party password reset libraries** - Rejected: Unnecessary when better-auth already provides the functionality
3. **Magic link authentication** - Rejected: Out of scope; spec requires token-based password reset

**Code Reference**:
```typescript
// Forget Password API
await authClient.forgetPassword(
  {
    email: string,
    redirectTo?: string  // URL to redirect with token
  },
  {
    onRequest: (ctx) => { /* show loading */ },
    onSuccess: (ctx) => { /* show confirmation */ },
    onError: (ctx) => { /* handle error */ }
  }
)

// Reset Password API
await authClient.resetPassword(
  {
    newPassword: string,
    token: string  // Extract from URL query params
  },
  {
    onRequest: (ctx) => { /* show loading */ },
    onSuccess: (ctx) => { /* redirect to login */ },
    onError: (ctx) => { /* handle error */ }
  }
)
```

**Documentation**: https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/authentication/email-password.mdx

---

### 2. Password Strength Validation Requirements

**Question**: What are the specific password requirements enforced by better-auth, and how should we validate them on the frontend?

**Decision**: Implement client-side validation matching industry standards: minimum 8 characters, at least one uppercase, one lowercase, one number, one special character

**Rationale**:
- Spec explicitly defines password requirements (FR-007): "minimum 8 characters, at least one uppercase, one lowercase, one number, one special character"
- Client-side validation provides immediate user feedback (< 100ms target)
- Server-side validation in better-auth provides final enforcement
- Consistent with security best practices and common password policies

**Alternatives Considered**:
1. **Rely solely on server-side validation** - Rejected: Poor UX, no real-time feedback
2. **Use zod or yup validation library** - Rejected: Overkill for simple regex validation; adds unnecessary dependency
3. **Passwordless authentication** - Rejected: Out of scope for this feature

**Implementation Approach**:
```typescript
// lib/validation/password.ts
export interface PasswordValidation {
  isValid: boolean;
  errors: string[];
}

export function validatePassword(password: string): PasswordValidation {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push("Password must be at least 8 characters");
  }
  if (!/[A-Z]/.test(password)) {
    errors.push("Password must contain at least one uppercase letter");
  }
  if (!/[a-z]/.test(password)) {
    errors.push("Password must contain at least one lowercase letter");
  }
  if (!/[0-9]/.test(password)) {
    errors.push("Password must contain at least one number");
  }
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    errors.push("Password must contain at least one special character");
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

export function validatePasswordMatch(password: string, confirmPassword: string): boolean {
  return password === confirmPassword && password.length > 0;
}
```

---

### 3. Token Extraction and URL Parameter Handling

**Question**: How should we extract the reset token from the URL and handle malformed/missing tokens?

**Decision**: Use Next.js `useSearchParams` hook for client-side token extraction with client-side format validation

**Rationale**:
- Next.js 16.0.9 App Router provides `useSearchParams` hook for query parameter access
- Client-side extraction allows immediate token validation before form submission
- Better-auth sends token as query parameter: `/reset-password?token=...`
- Spec requires client-side token format validation (FR-005b) and user-friendly error handling

**Alternatives Considered**:
1. **Server-side token extraction with Server Components** - Rejected: Requires form submission to validate, worse UX
2. **Dynamic route segment (`/reset-password/[token]`)** - Rejected: Doesn't match better-auth URL format
3. **Hash fragment (`#token`)** - Rejected: Not standard for better-auth; harder to access server-side

**Implementation Approach**:
```typescript
'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [tokenError, setTokenError] = useState<string | null>(null);

  useEffect(() => {
    const tokenParam = searchParams.get('token');

    if (!tokenParam) {
      setTokenError('No reset token provided');
      // Auto-redirect to forgot-password after 3 seconds (FR-005a)
      setTimeout(() => router.push('/forgot-password'), 3000);
      return;
    }

    // Basic token format validation (client-side)
    // Better-auth tokens are typically 32+ alphanumeric characters
    if (!/^[A-Za-z0-9_-]{32,}$/.test(tokenParam)) {
      setTokenError('Invalid token format');
      return;
    }

    setToken(tokenParam);
  }, [searchParams, router]);

  // ... rest of component
}
```

---

### 4. Rate Limiting and Request Throttling

**Question**: How should we implement client-side rate limiting to prevent abuse of the password reset flow?

**Decision**: Implement client-side request throttling with localStorage tracking (2 requests per 5 minutes per email)

**Rationale**:
- Spec requires rate limiting (FR-004a): "maximum 2 password reset requests per email address within a 5-minute window"
- Client-side throttling provides immediate feedback without server round-trip
- localStorage persists across page refreshes (prevents simple bypass)
- Server-side rate limiting in better-auth provides final enforcement
- Graceful degradation if localStorage unavailable (falls back to server enforcement)

**Alternatives Considered**:
1. **Server-side only rate limiting** - Rejected: Still makes unnecessary server requests; no immediate feedback
2. **Session-based throttling** - Rejected: Lost on page refresh; easily bypassed
3. **IP-based rate limiting** - Rejected: Client can't determine IP; backend responsibility

**Implementation Approach**:
```typescript
// lib/validation/rate-limit.ts
interface RateLimitEntry {
  email: string;
  attempts: number;
  firstAttemptAt: number;
}

const RATE_LIMIT_KEY = 'password_reset_rate_limit';
const MAX_ATTEMPTS = 2;
const WINDOW_MS = 5 * 60 * 1000; // 5 minutes

export function checkRateLimit(email: string): { allowed: boolean; remainingTime?: number } {
  if (typeof window === 'undefined') return { allowed: true };

  try {
    const stored = localStorage.getItem(RATE_LIMIT_KEY);
    const entries: RateLimitEntry[] = stored ? JSON.parse(stored) : [];

    const now = Date.now();
    const entry = entries.find(e => e.email === email);

    if (!entry) {
      return { allowed: true };
    }

    const timeElapsed = now - entry.firstAttemptAt;

    if (timeElapsed > WINDOW_MS) {
      // Window expired, reset
      return { allowed: true };
    }

    if (entry.attempts >= MAX_ATTEMPTS) {
      const remainingTime = Math.ceil((WINDOW_MS - timeElapsed) / 1000);
      return { allowed: false, remainingTime };
    }

    return { allowed: true };
  } catch (error) {
    // localStorage error, allow request (server will enforce)
    console.error('Rate limit check failed:', error);
    return { allowed: true };
  }
}

export function recordAttempt(email: string): void {
  if (typeof window === 'undefined') return;

  try {
    const stored = localStorage.getItem(RATE_LIMIT_KEY);
    const entries: RateLimitEntry[] = stored ? JSON.parse(stored) : [];

    const now = Date.now();
    const entryIndex = entries.findIndex(e => e.email === email);

    if (entryIndex >= 0) {
      const entry = entries[entryIndex];
      const timeElapsed = now - entry.firstAttemptAt;

      if (timeElapsed > WINDOW_MS) {
        // Reset window
        entries[entryIndex] = { email, attempts: 1, firstAttemptAt: now };
      } else {
        entries[entryIndex].attempts++;
      }
    } else {
      entries.push({ email, attempts: 1, firstAttemptAt: now });
    }

    // Clean old entries
    const cleanedEntries = entries.filter(e => now - e.firstAttemptAt <= WINDOW_MS);
    localStorage.setItem(RATE_LIMIT_KEY, JSON.stringify(cleanedEntries));
  } catch (error) {
    console.error('Failed to record rate limit attempt:', error);
  }
}
```

---

### 5. Email Enumeration Prevention

**Question**: How do we prevent email enumeration attacks while providing good user experience?

**Decision**: Display generic success message for all email submissions, regardless of whether the email exists

**Rationale**:
- Spec requirement (FR-004): "generic success message after submission (whether email exists or not) to prevent email enumeration attacks"
- Security best practice: attackers can't determine valid email addresses by observing responses
- Better UX than showing errors: user assumes email was sent and checks inbox
- Consistent with better-auth backend behavior (returns success regardless of email existence)

**Alternatives Considered**:
1. **Different messages for existing/non-existing emails** - Rejected: Security vulnerability (email enumeration)
2. **CAPTCHA before submission** - Rejected: Out of scope (FR notes CAPTCHA is excluded)
3. **No feedback message** - Rejected: Poor UX, user doesn't know if action succeeded

**Implementation**:
```typescript
// Always show same success message
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setIsLoading(true);
  setError(null);

  await authClient.forgetPassword({
    email,
    redirectTo: `${window.location.origin}/reset-password`
  }, {
    onSuccess: () => {
      setIsLoading(false);
      // Generic message - don't reveal if email exists
      setSuccessMessage("If an account with that email exists, we've sent a password reset link. Please check your inbox.");
    },
    onError: (ctx) => {
      setIsLoading(false);
      // Only show errors for actual failures (network, etc), not "email not found"
      if (ctx.error.status === 429) {
        setError("Too many attempts. Please try again later.");
      } else {
        setError("Something went wrong. Please try again.");
      }
    }
  });
};
```

---

### 6. Session Invalidation After Password Reset

**Question**: How should we handle users who are already logged in when they reset their password?

**Decision**: Allow the reset flow to proceed and automatically sign out the user after successful password reset

**Rationale**:
- Spec requirement (FR-013a): "automatically log the user out and invalidate all active sessions for security before redirecting to the login page"
- Security best practice: password reset should invalidate all sessions (potential account takeover scenario)
- Better UX: user can reset password even if they have an active session
- Better-auth server handles session invalidation on backend

**Alternatives Considered**:
1. **Block password reset if logged in** - Rejected: Reduces flexibility, user might want to change password while logged in
2. **Keep user logged in after reset** - Rejected: Security risk, violates spec requirement
3. **Require re-authentication before reset** - Rejected: Out of scope, different from "forgot password" flow

**Implementation Approach**:
```typescript
const handleResetPassword = async (e: React.FormEvent) => {
  e.preventDefault();
  setIsLoading(true);
  setError(null);

  await authClient.resetPassword({
    newPassword,
    token: token!
  }, {
    onSuccess: async () => {
      // Check if user is logged in
      const session = await authClient.getSession();

      if (session) {
        // Sign out to invalidate session
        await authClient.signOut();
      }

      setIsLoading(false);
      // Redirect to login with success message
      router.push('/login?reset=success');
    },
    onError: (ctx) => {
      setIsLoading(false);

      if (ctx.error.message.includes('expired')) {
        setError('This reset link has expired. Please request a new one.');
      } else if (ctx.error.message.includes('invalid')) {
        setError('Invalid reset token. Please request a new reset link.');
      } else {
        setError('Failed to reset password. Please try again.');
      }
    }
  });
};
```

---

### 7. Error Handling and User Guidance

**Question**: What error scenarios should we handle, and what user guidance should we provide?

**Decision**: Implement comprehensive error handling with specific messages for common failure scenarios

**Rationale**:
- Spec requirement (SC-004): "Users receive clear, actionable error messages for 100% of failure scenarios"
- Better UX: users understand what went wrong and what to do next
- Reduces support burden: clear messages prevent user confusion

**Error Scenarios Identified**:

| Scenario | Detection | User Message | Action |
|----------|-----------|--------------|--------|
| No token in URL | `searchParams.get('token') === null` | "No reset token provided. Redirecting to request a new one..." | Auto-redirect to /forgot-password after 3s |
| Malformed token | Regex validation fails | "Invalid reset link. Please request a new password reset." | Show link to /forgot-password |
| Expired token | API error response | "This reset link has expired. Please request a new one." | Show link to /forgot-password |
| Network failure | API error (timeout/offline) | "Unable to connect. Please check your internet connection and try again." | Show retry button |
| Server error | API error (5xx) | "Something went wrong on our end. Please try again in a few moments." | Show retry button |
| Rate limit exceeded | API error (429) | "Too many attempts. Please check your email or wait 5 minutes before trying again." | Disable form for remaining time |
| Password validation failure | Client-side validation | "Password must be at least 8 characters with uppercase, lowercase, number, and special character" | Show inline validation errors |
| Password mismatch | Client-side validation | "Passwords do not match" | Highlight confirmation field |

**Implementation Pattern**:
```typescript
// Centralized error handler
function getErrorMessage(error: any): { message: string; action?: string } {
  if (!navigator.onLine) {
    return {
      message: "No internet connection. Please check your connection and try again.",
      action: "retry"
    };
  }

  if (error.status === 429) {
    return {
      message: "Too many attempts. Please check your email or wait 5 minutes.",
      action: "wait"
    };
  }

  if (error.message?.includes('expired')) {
    return {
      message: "This reset link has expired. Please request a new one.",
      action: "request_new"
    };
  }

  if (error.message?.includes('invalid')) {
    return {
      message: "Invalid reset token. Please request a new reset link.",
      action: "request_new"
    };
  }

  return {
    message: "Something went wrong. Please try again.",
    action: "retry"
  };
}
```

---

## Research Summary

All technical unknowns have been resolved through documentation review and architectural analysis:

1. ✅ **Better-Auth API**: `forgetPassword` and `resetPassword` methods identified with full type signatures
2. ✅ **Password Validation**: Regex-based validation approach defined matching spec requirements
3. ✅ **Token Handling**: `useSearchParams` hook pattern with client-side format validation
4. ✅ **Rate Limiting**: LocalStorage-based throttling (2 requests per 5 min) with graceful fallback
5. ✅ **Email Enumeration**: Generic success messages to prevent attack vector
6. ✅ **Session Invalidation**: Auto-signout after reset using existing `signOut` method
7. ✅ **Error Handling**: Comprehensive error mapping with actionable user messages

**Ready for Phase 1: Design & Contracts**
