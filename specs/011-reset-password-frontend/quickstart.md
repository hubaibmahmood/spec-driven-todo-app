# Quickstart Guide: Reset Password Frontend Integration

**Feature**: 011-reset-password-frontend
**Date**: 2025-12-27
**Audience**: Developers implementing this feature

## Overview

This guide provides a step-by-step walkthrough for implementing the password reset frontend feature. Follow this guide to add forgot password and reset password pages to the Next.js todo application.

**Estimated Time**: 4-6 hours (including testing)

---

## Prerequisites

Before starting implementation:

- [ ] Better-auth server (spec 004-auth-server) is deployed and operational
- [ ] Better-auth client SDK (v1.4.6+) is installed in frontend project
- [ ] You have reviewed the spec.md, plan.md, and research.md documents
- [ ] Development environment is set up with Node.js 20+ and npm/pnpm
- [ ] You can run the frontend locally with `npm run dev`

**Verify Prerequisites**:

```bash
# Check better-auth client version
cd frontend
npm list better-auth

# Should show: better-auth@1.4.6 or higher

# Verify auth client is configured
cat lib/auth-client.ts
# Should contain: import { createAuthClient } from "better-auth/react"
```

---

## Implementation Roadmap

This feature is implemented in **3 phases**:

1. **Phase 1: Validation Utilities** (~1 hour)
   - Password validation functions
   - Rate limiting utilities
   - Unit tests

2. **Phase 2: UI Components** (~2-3 hours)
   - Forgot password page
   - Reset password page
   - Login page enhancement
   - Component tests

3. **Phase 3: Integration Testing** (~1-2 hours)
   - E2E tests with Playwright
   - Manual testing
   - Bug fixes

---

## Phase 1: Validation Utilities

### Step 1.1: Create Password Validation Module

**File**: `frontend/lib/validation/password.ts`

```typescript
/**
 * Password validation utilities for password reset flow
 */

export interface PasswordValidation {
  isValid: boolean;
  errors: string[];
}

/**
 * Validates password against security requirements:
 * - Minimum 8 characters
 * - At least one uppercase letter
 * - At least one lowercase letter
 * - At least one number
 * - At least one special character
 */
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

/**
 * Checks if password and confirmation match
 */
export function validatePasswordMatch(
  password: string,
  confirmPassword: string
): boolean {
  return password === confirmPassword && password.length > 0;
}
```

**Create directory**:
```bash
mkdir -p frontend/lib/validation
```

### Step 1.2: Create Rate Limiting Module

**File**: `frontend/lib/validation/rate-limit.ts`

```typescript
/**
 * Client-side rate limiting for password reset requests
 * Limits: 2 requests per email per 5 minutes
 */

interface RateLimitEntry {
  email: string;
  attempts: number;
  firstAttemptAt: number; // Unix timestamp (ms)
}

const RATE_LIMIT_KEY = 'password_reset_rate_limit';
const MAX_ATTEMPTS = 2;
const WINDOW_MS = 5 * 60 * 1000; // 5 minutes

export interface RateLimitCheck {
  allowed: boolean;
  remainingTime?: number; // Seconds until next attempt allowed
}

/**
 * Checks if email is rate limited
 * Returns { allowed: true } if request is allowed
 * Returns { allowed: false, remainingTime: X } if rate limited
 */
export function checkRateLimit(email: string): RateLimitCheck {
  // Server-side only (SSR guard)
  if (typeof window === 'undefined') {
    return { allowed: true };
  }

  try {
    const stored = localStorage.getItem(RATE_LIMIT_KEY);
    const entries: RateLimitEntry[] = stored ? JSON.parse(stored) : [];

    const now = Date.now();
    const entry = entries.find(e => e.email === email);

    if (!entry) {
      return { allowed: true };
    }

    const timeElapsed = now - entry.firstAttemptAt;

    // Window expired, allow request
    if (timeElapsed > WINDOW_MS) {
      return { allowed: true };
    }

    // Rate limit exceeded
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

/**
 * Records a password reset attempt for rate limiting
 */
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

    // Clean old entries (garbage collection)
    const cleanedEntries = entries.filter(
      e => now - e.firstAttemptAt <= WINDOW_MS
    );

    localStorage.setItem(RATE_LIMIT_KEY, JSON.stringify(cleanedEntries));
  } catch (error) {
    console.error('Failed to record rate limit attempt:', error);
  }
}
```

### Step 1.3: Write Unit Tests

**File**: `frontend/__tests__/lib/validation/password.test.ts`

```typescript
import { validatePassword, validatePasswordMatch } from '@/lib/validation/password';

describe('validatePassword', () => {
  it('validates strong password', () => {
    const result = validatePassword('StrongPass123!');
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  it('rejects password too short', () => {
    const result = validatePassword('Short1!');
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must be at least 8 characters');
  });

  it('rejects password without uppercase', () => {
    const result = validatePassword('lowercase123!');
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must contain at least one uppercase letter');
  });

  it('rejects password without lowercase', () => {
    const result = validatePassword('UPPERCASE123!');
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must contain at least one lowercase letter');
  });

  it('rejects password without number', () => {
    const result = validatePassword('NoNumbers!');
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must contain at least one number');
  });

  it('rejects password without special character', () => {
    const result = validatePassword('NoSpecial123');
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must contain at least one special character');
  });
});

describe('validatePasswordMatch', () => {
  it('returns true for matching passwords', () => {
    expect(validatePasswordMatch('password', 'password')).toBe(true);
  });

  it('returns false for non-matching passwords', () => {
    expect(validatePasswordMatch('password1', 'password2')).toBe(false);
  });

  it('returns false for empty passwords', () => {
    expect(validatePasswordMatch('', '')).toBe(false);
  });
});
```

**File**: `frontend/__tests__/lib/validation/rate-limit.test.ts`

```typescript
import { checkRateLimit, recordAttempt } from '@/lib/validation/rate-limit';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    clear: () => { store = {}; }
  };
})();

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('Rate Limiting', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  it('allows first attempt', () => {
    const result = checkRateLimit('test@example.com');
    expect(result.allowed).toBe(true);
  });

  it('allows second attempt', () => {
    recordAttempt('test@example.com');
    recordAttempt('test@example.com');
    const result = checkRateLimit('test@example.com');
    expect(result.allowed).toBe(true);
  });

  it('blocks third attempt', () => {
    recordAttempt('test@example.com');
    recordAttempt('test@example.com');
    recordAttempt('test@example.com'); // This exceeds limit
    const result = checkRateLimit('test@example.com');
    expect(result.allowed).toBe(false);
    expect(result.remainingTime).toBeGreaterThan(0);
  });

  it('allows attempt after window expires', () => {
    const email = 'test@example.com';
    recordAttempt(email);
    recordAttempt(email);

    // Simulate time passing by manipulating stored data
    const stored = JSON.parse(localStorageMock.getItem('password_reset_rate_limit')!);
    stored[0].firstAttemptAt = Date.now() - (6 * 60 * 1000); // 6 minutes ago
    localStorageMock.setItem('password_reset_rate_limit', JSON.stringify(stored));

    const result = checkRateLimit(email);
    expect(result.allowed).toBe(true);
  });
});
```

**Run tests**:
```bash
cd frontend
npm test -- password.test.ts
npm test -- rate-limit.test.ts
```

---

## Phase 2: UI Components

### Step 2.1: Create Forgot Password Page

**File**: `frontend/app/(auth)/forgot-password/page.tsx`

<details>
<summary>Click to expand full component code</summary>

```typescript
"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, ArrowRight, Loader2 } from "lucide-react";
import { authClient } from "@/lib/auth-client";
import { checkRateLimit, recordAttempt } from "@/lib/validation/rate-limit";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    // Check rate limit
    const rateCheck = checkRateLimit(email);
    if (!rateCheck.allowed) {
      setError(
        `Too many attempts. Please check your email or wait ${rateCheck.remainingTime} seconds before trying again.`
      );
      setIsLoading(false);
      return;
    }

    await authClient.forgetPassword(
      {
        email,
        redirectTo: `${window.location.origin}/reset-password`,
      },
      {
        onSuccess: () => {
          setIsLoading(false);
          setSuccessMessage(
            "If an account with that email exists, we've sent a password reset link. Please check your inbox and spam folder."
          );
          setEmail(""); // Clear form
          recordAttempt(email); // Track attempt
        },
        onError: (ctx) => {
          setIsLoading(false);

          if (ctx.error.status === 429) {
            setError("Too many attempts. Please check your email or wait 5 minutes before trying again.");
          } else if (ctx.error.status === 503) {
            setError("Email service is temporarily unavailable. Please try again later.");
          } else {
            setError("Something went wrong. Please try again.");
          }
        },
      }
    );
  };

  return (
    <div className="p-8 pt-0">
      <h2 className="text-2xl font-bold text-slate-900 text-center mb-2">
        Forgot Password?
      </h2>
      <p className="text-slate-500 text-center mb-8 text-sm">
        Enter your email address and we&apos;ll send you a reset link
      </p>

      {successMessage && (
        <div className="mb-4 p-3 text-sm text-green-600 bg-green-50 rounded-lg border border-green-200">
          {successMessage}
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 text-sm text-red-500 bg-red-50 rounded-lg border border-red-200">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Email Address
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-colors"
              placeholder="john@example.com"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg transition-all shadow-sm shadow-indigo-200 mt-6 disabled:opacity-70 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Sending...
            </>
          ) : (
            <>
              Send Reset Link
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </form>

      <div className="mt-6 text-center">
        <Link
          href="/login"
          className="text-sm text-indigo-600 hover:text-indigo-500 transition-colors"
        >
          ← Back to Login
        </Link>
      </div>
    </div>
  );
}
```

</details>

**Create the page**:
```bash
mkdir -p frontend/app/\(auth\)/forgot-password
```

### Step 2.2: Create Reset Password Page

**File**: `frontend/app/(auth)/reset-password/page.tsx`

<details>
<summary>Click to expand full component code (large)</summary>

```typescript
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Lock, Eye, EyeOff, Loader2, ArrowRight } from "lucide-react";
import { authClient } from "@/lib/auth-client";
import { validatePassword, type PasswordValidation } from "@/lib/validation/password";

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [token, setToken] = useState<string | null>(null);
  const [tokenError, setTokenError] = useState<string | null>(null);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [passwordValidation, setPasswordValidation] = useState<PasswordValidation | null>(null);
  const [passwordsMatch, setPasswordsMatch] = useState(true);

  useEffect(() => {
    const tokenParam = searchParams.get('token');

    if (!tokenParam) {
      setTokenError('No reset token provided. Redirecting to forgot password...');
      setTimeout(() => router.push('/forgot-password'), 3000);
      return;
    }

    // Validate token format (client-side)
    if (!/^[A-Za-z0-9_-]{32,}$/.test(tokenParam)) {
      setTokenError('Invalid reset link. Please request a new password reset.');
      return;
    }

    setToken(tokenParam);
  }, [searchParams, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!passwordValidation?.isValid) {
      setError("Please fix password validation errors");
      return;
    }

    if (!passwordsMatch) {
      setError("Passwords do not match");
      return;
    }

    setIsLoading(true);
    setError(null);

    await authClient.resetPassword(
      {
        newPassword,
        token: token!,
      },
      {
        onSuccess: async () => {
          setIsLoading(false);

          // Check if user is logged in
          const session = await authClient.getSession();
          if (session) {
            // Sign out to invalidate all sessions
            await authClient.signOut();
          }

          // Redirect to login with success message
          router.push('/login?reset=success');
        },
        onError: (ctx) => {
          setIsLoading(false);

          if (ctx.error.message?.includes('expired')) {
            setError('This reset link has expired. Reset links are valid for 1 hour.');
          } else if (ctx.error.message?.includes('invalid') || ctx.error.message?.includes('not found')) {
            setError('This reset link is invalid. Please request a new password reset.');
          } else if (ctx.error.message?.includes('password')) {
            setError('Password does not meet security requirements.');
          } else {
            setError('Failed to reset password. Please try again.');
          }
        },
      }
    );
  };

  return (
    <div className="p-8 pt-0">
      <h2 className="text-2xl font-bold text-slate-900 text-center mb-2">
        Reset Password
      </h2>
      <p className="text-slate-500 text-center mb-8 text-sm">
        Enter your new password below
      </p>

      {tokenError && (
        <div className="mb-4 p-3 text-sm text-red-500 bg-red-50 rounded-lg border border-red-200">
          {tokenError}
          {!tokenError.includes('Redirecting') && (
            <div className="mt-2">
              <Link href="/forgot-password" className="font-medium underline">
                Request New Reset Link
              </Link>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 text-sm text-red-500 bg-red-50 rounded-lg border border-red-200">
          {error}
          {(error.includes('expired') || error.includes('invalid')) && (
            <div className="mt-2">
              <Link href="/forgot-password" className="font-medium underline">
                Request New Reset Link
              </Link>
            </div>
          )}
        </div>
      )}

      {token && !tokenError && (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              New Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type={showPassword ? "text" : "password"}
                required
                value={newPassword}
                onChange={(e) => {
                  setNewPassword(e.target.value);
                  setPasswordValidation(validatePassword(e.target.value));
                  setError(null);
                }}
                className="w-full pl-10 pr-10 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-colors"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 focus:outline-none"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>

            {passwordValidation && !passwordValidation.isValid && newPassword.length > 0 && (
              <ul className="mt-2 space-y-1">
                {passwordValidation.errors.map((err, i) => (
                  <li key={i} className="text-xs text-red-500">• {err}</li>
                ))}
              </ul>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Confirm Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type={showConfirmPassword ? "text" : "password"}
                required
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  setPasswordsMatch(e.target.value === newPassword);
                  setError(null);
                }}
                className="w-full pl-10 pr-10 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-colors"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 focus:outline-none"
              >
                {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>

            {!passwordsMatch && confirmPassword.length > 0 && (
              <p className="mt-2 text-xs text-red-500">Passwords do not match</p>
            )}
          </div>

          <button
            type="submit"
            disabled={
              isLoading ||
              !passwordValidation?.isValid ||
              !passwordsMatch ||
              confirmPassword.length === 0
            }
            className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg transition-all shadow-sm shadow-indigo-200 mt-6 disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Resetting Password...
              </>
            ) : (
              <>
                Reset Password
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </form>
      )}

      <div className="mt-6 text-center">
        <Link
          href="/login"
          className="text-sm text-indigo-600 hover:text-indigo-500 transition-colors"
        >
          ← Back to Login
        </Link>
      </div>
    </div>
  );
}
```

</details>

**Create the page**:
```bash
mkdir -p frontend/app/\(auth\)/reset-password
```

### Step 2.3: Update Login Page

**File**: `frontend/app/(auth)/login/page.tsx` (existing file - modify)

Add these changes:

1. **Import useSearchParams**:
```typescript
import { useSearchParams } from "next/navigation";
```

2. **Add state for success message**:
```typescript
const [successMessage, setSuccessMessage] = useState<string | null>(null);
const searchParams = useSearchParams();
```

3. **Check for reset success in useEffect**:
```typescript
useEffect(() => {
  if (searchParams.get('reset') === 'success') {
    setSuccessMessage('Your password has been reset successfully. Please log in with your new password.');
  }
}, [searchParams]);
```

4. **Add success message display (before error)**:
```tsx
{successMessage && (
  <div className="mb-4 p-3 text-sm text-green-600 bg-green-50 rounded-lg border border-green-200 text-center">
    {successMessage}
  </div>
)}
```

5. **Add forgot password link (after password input)**:
```tsx
<div className="text-right -mt-2 mb-4">
  <Link
    href="/forgot-password"
    className="text-sm text-indigo-600 hover:text-indigo-500 transition-colors"
  >
    Forgot Password?
  </Link>
</div>
```

---

## Phase 3: Testing

### Step 3.1: Component Tests

Create test files for each page component.

**File**: `frontend/__tests__/app/(auth)/forgot-password.test.tsx`

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ForgotPasswordPage from '@/app/(auth)/forgot-password/page';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock auth client
jest.mock('@/lib/auth-client', () => ({
  authClient: {
    forgetPassword: jest.fn(),
  },
}));

describe('ForgotPasswordPage', () => {
  it('renders form correctly', () => {
    render(<ForgotPasswordPage />);
    expect(screen.getByText('Forgot Password?')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('john@example.com')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send reset link/i })).toBeInTheDocument();
  });

  it('submits form with valid email', async () => {
    const { authClient } = require('@/lib/auth-client');
    authClient.forgetPassword.mockImplementation((req, options) => {
      options.onSuccess();
    });

    render(<ForgotPasswordPage />);

    await userEvent.type(screen.getByPlaceholderText('john@example.com'), 'test@example.com');
    fireEvent.click(screen.getByRole('button', { name: /send reset link/i }));

    await waitFor(() => {
      expect(screen.getByText(/if an account with that email exists/i)).toBeInTheDocument();
    });
  });

  // Add more tests...
});
```

**Run component tests**:
```bash
npm test -- forgot-password.test.tsx
```

### Step 3.2: E2E Tests

**File**: `frontend/__tests__/e2e/password-reset.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Password Reset Flow', () => {
  test('complete password reset flow', async ({ page }) => {
    // Navigate to login
    await page.goto('/login');

    // Click forgot password link
    await page.click('text=Forgot Password?');
    await expect(page).toHaveURL('/forgot-password');

    // Submit email
    await page.fill('input[type=email]', 'test@example.com');
    await page.click('button:has-text("Send Reset Link")');

    // Verify success message
    await expect(page.locator('text=If an account with that email exists')).toBeVisible();

    // TODO: Manual step - get token from email
    // For now, test token validation

    // Navigate to reset password without token
    await page.goto('/reset-password');
    await expect(page.locator('text=No reset token provided')).toBeVisible();

    // Navigate with invalid token
    await page.goto('/reset-password?token=invalid');
    await expect(page.locator('text=Invalid reset link')).toBeVisible();
  });
});
```

**Run E2E tests**:
```bash
npx playwright test password-reset.spec.ts
```

### Step 3.3: Manual Testing Checklist

- [ ] **Forgot Password Page**:
  - [ ] Load `/forgot-password` - page renders correctly
  - [ ] Submit with valid email - see success message
  - [ ] Submit with invalid email format - see validation error
  - [ ] Submit 3 times quickly - 3rd attempt shows rate limit error
  - [ ] Click "Back to Login" - navigate to `/login`

- [ ] **Reset Password Page**:
  - [ ] Load `/reset-password` (no token) - see error and auto-redirect
  - [ ] Load with malformed token - see "invalid format" error
  - [ ] Load with valid token - form renders
  - [ ] Enter weak password - see validation errors in real-time
  - [ ] Enter strong password - validation passes
  - [ ] Enter non-matching confirmation - see "do not match" error
  - [ ] Submit with valid password - redirect to login with success message

- [ ] **Login Page**:
  - [ ] See "Forgot Password?" link
  - [ ] Click link - navigate to `/forgot-password`
  - [ ] Load `/login?reset=success` - see success message

---

## Deployment Checklist

Before deploying to production:

- [ ] All unit tests passing (`npm test`)
- [ ] All E2E tests passing (`npx playwright test`)
- [ ] Manual testing completed
- [ ] Better-auth server configured with Resend API key
- [ ] Email templates reviewed and approved
- [ ] Frontend environment variables set (NEXT_PUBLIC_AUTH_URL)
- [ ] CORS configured in better-auth server
- [ ] Rate limiting tested with actual emails
- [ ] Error messages reviewed for clarity
- [ ] Mobile responsive design tested

---

## Troubleshooting

### Issue: "forgetPassword is not a function"

**Cause**: better-auth client not properly configured

**Solution**:
```bash
# Reinstall better-auth
npm install better-auth@latest

# Verify export in lib/auth-client.ts
export const { signIn, signUp, signOut, useSession } = authClient;
# Should be:
export const authClient = createAuthClient({ ... });
```

### Issue: Emails not sending

**Cause**: Resend API key not configured or invalid

**Solution**:
1. Check better-auth server env: `RESEND_API_KEY=re_xxxxx`
2. Verify Resend domain is verified
3. Check better-auth server logs for email errors

### Issue: Rate limiting not working

**Cause**: localStorage not available or browser privacy mode

**Solution**:
- Rate limiting gracefully falls back to server-side enforcement
- Verify in browser DevTools → Application → LocalStorage
- Check for `password_reset_rate_limit` key

### Issue: Token validation fails

**Cause**: Token format changed or server issue

**Solution**:
1. Check better-auth server version matches client
2. Verify token in URL matches pattern: `/^[A-Za-z0-9_-]{32,}$/`
3. Test with fresh reset request

---

## Next Steps

After completing implementation:

1. **Run `/sp.tasks`** command to generate task breakdown for implementation
2. **Follow TDD workflow**: Write tests first, then implement
3. **Create ADR** if architectural decisions were made during implementation
4. **Update documentation** if implementation differs from plan
5. **Create PR** with comprehensive description and screenshots

---

## Resources

- [Better-Auth Documentation](https://better-auth.com/docs)
- [Next.js App Router](https://nextjs.org/docs/app)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev/)

---

## Support

If you encounter issues not covered in this guide:

1. Review spec.md for requirements clarification
2. Check research.md for technical decisions
3. Review contracts/ for API details
4. Consult the team or raise a question in the planning phase
