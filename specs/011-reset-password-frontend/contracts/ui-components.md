# UI Component Contracts: Password Reset Pages

**Feature**: 011-reset-password-frontend
**Date**: 2025-12-27
**Framework**: Next.js 16 App Router + React 19

## Overview

This document defines the component contracts (props, state, behavior) for the password reset UI components. These contracts serve as the specification for implementation and testing.

---

## Component 1: ForgotPasswordPage

### Location

`frontend/app/(auth)/forgot-password/page.tsx`

### Component Type

Next.js Server Component wrapper with Client Component form

### Purpose

Allows users to request a password reset email by providing their email address.

### Props

```typescript
// No props - Next.js page component
export default function ForgotPasswordPage() {}
```

### State

```typescript
const [email, setEmail] = useState<string>("");
const [isLoading, setIsLoading] = useState<boolean>(false);
const [error, setError] = useState<string | null>(null);
const [successMessage, setSuccessMessage] = useState<string | null>(null);
const [rateLimitRemaining, setRateLimitRemaining] = useState<number | null>(null);
```

### Behavior

#### Initial Load
- Render email input form
- No loading state
- No error messages
- Check rate limit for previously submitted emails (from localStorage)

#### User Interactions

1. **Email Input Change**:
   ```typescript
   onChange={(e) => setEmail(e.target.value)}
   ```
   - Clear error message
   - Clear success message
   - Update email state

2. **Form Submit**:
   ```typescript
   onSubmit={(e) => {
     e.preventDefault();
     handleForgotPassword();
   }}
   ```
   - Validate email format (client-side)
   - Check rate limit
   - If allowed: Submit to better-auth API
   - If rate limited: Show error with remaining time

3. **Back to Login Link**:
   ```typescript
   onClick={() => router.push('/login')}
   ```
   - Navigate to `/login` page

### Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| Email | Required | "Please enter your email address" |
| Email | Valid format | "Please enter a valid email address" |
| Rate Limit | Max 2 per 5 min | "Too many attempts. Please wait {X} seconds and check your email." |

### API Integration

```typescript
await authClient.forgetPassword({
  email,
  redirectTo: `${window.location.origin}/reset-password`
}, {
  onRequest: (ctx) => {
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);
  },
  onSuccess: (ctx) => {
    setIsLoading(false);
    setSuccessMessage(
      "If an account with that email exists, we've sent a password reset link. " +
      "Please check your inbox and spam folder."
    );
    setEmail(""); // Clear form
    recordRateLimitAttempt(email); // Track attempt
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
  }
});
```

### Layout Structure

```tsx
<div className="max-w-md mx-auto p-8">
  <h1>Forgot Password</h1>
  <p>Enter your email address and we'll send you a reset link.</p>

  {/* Success Message */}
  {successMessage && (
    <div className="success-message">
      {successMessage}
    </div>
  )}

  {/* Error Message */}
  {error && (
    <div className="error-message">
      {error}
    </div>
  )}

  {/* Form */}
  <form onSubmit={handleSubmit}>
    <div>
      <label>Email Address</label>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="john@example.com"
        required
      />
    </div>

    <button
      type="submit"
      disabled={isLoading || rateLimitRemaining !== null}
    >
      {isLoading ? (
        <>
          <Loader2 className="animate-spin" />
          Sending...
        </>
      ) : (
        "Send Reset Link"
      )}
    </button>
  </form>

  {/* Back to Login */}
  <Link href="/login">Back to Login</Link>
</div>
```

### Accessibility

- Form has proper `<label>` elements with `htmlFor`
- Error messages have `role="alert"` and `aria-live="polite"`
- Submit button has `aria-busy` during loading
- Input has `aria-invalid` when validation fails
- Success message has `role="status"`

### Test Cases

1. **Valid Email Submission**:
   - Enter valid email → Submit → See success message
   - Verify `forgetPassword` called with correct email

2. **Invalid Email Format**:
   - Enter "notanemail" → Submit → See validation error
   - Verify API not called

3. **Rate Limit Enforcement**:
   - Submit 2 requests quickly → 3rd attempt shows rate limit error
   - Verify error message shows remaining time

4. **Network Error Handling**:
   - Simulate network failure → See "check your connection" error
   - Retry button available

5. **Loading State**:
   - Submit form → Button shows "Sending..." with spinner
   - Form inputs disabled during loading

---

## Component 2: ResetPasswordPage

### Location

`frontend/app/(auth)/reset-password/page.tsx`

### Component Type

Client Component (uses `useSearchParams`)

### Purpose

Allows users to complete password reset by entering a new password using the token from their email.

### Props

```typescript
// No props - Next.js page component
export default function ResetPasswordPage() {}
```

### State

```typescript
const [token, setToken] = useState<string | null>(null);
const [tokenError, setTokenError] = useState<string | null>(null);
const [newPassword, setNewPassword] = useState<string>("");
const [confirmPassword, setConfirmPassword] = useState<string>("");
const [showPassword, setShowPassword] = useState<boolean>(false);
const [showConfirmPassword, setShowConfirmPassword] = useState<boolean>(false);
const [isLoading, setIsLoading] = useState<boolean>(false);
const [error, setError] = useState<string | null>(null);
const [passwordValidation, setPasswordValidation] = useState<PasswordValidation | null>(null);
const [passwordsMatch, setPasswordsMatch] = useState<boolean>(true);
```

### Behavior

#### Initial Load

```typescript
useEffect(() => {
  const searchParams = useSearchParams();
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
}, []);
```

#### User Interactions

1. **New Password Input Change**:
   ```typescript
   onChange={(e) => {
     setNewPassword(e.target.value);
     setPasswordValidation(validatePassword(e.target.value));
     setError(null);
   }}
   ```
   - Real-time password validation
   - Update validation state
   - Clear error message

2. **Confirm Password Input Change**:
   ```typescript
   onChange={(e) => {
     setConfirmPassword(e.target.value);
     setPasswordsMatch(e.target.value === newPassword);
     setError(null);
   }}
   ```
   - Check if passwords match
   - Update match state
   - Clear error message

3. **Toggle Password Visibility**:
   ```typescript
   onClick={() => setShowPassword(!showPassword)}
   onClick={() => setShowConfirmPassword(!showConfirmPassword)}
   ```
   - Toggle between `text` and `password` input type

4. **Form Submit**:
   ```typescript
   onSubmit={(e) => {
     e.preventDefault();
     handleResetPassword();
   }}
   ```
   - Validate password strength
   - Validate passwords match
   - Submit to better-auth API

### Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| New Password | Required | "Please enter a new password" |
| New Password | Min 8 chars | "Password must be at least 8 characters" |
| New Password | Uppercase | "Password must contain at least one uppercase letter" |
| New Password | Lowercase | "Password must contain at least one lowercase letter" |
| New Password | Number | "Password must contain at least one number" |
| New Password | Special char | "Password must contain at least one special character" |
| Confirm Password | Matches new | "Passwords do not match" |
| Token | Present | "No reset token provided" |
| Token | Valid format | "Invalid reset link format" |

### API Integration

```typescript
await authClient.resetPassword({
  newPassword,
  token: token!
}, {
  onRequest: (ctx) => {
    setIsLoading(true);
    setError(null);
  },
  onSuccess: async (ctx) => {
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
  }
});
```

### Layout Structure

```tsx
<div className="max-w-md mx-auto p-8">
  <h1>Reset Password</h1>
  <p>Enter your new password below.</p>

  {/* Token Error */}
  {tokenError && (
    <div className="error-message">
      {tokenError}
      {!tokenError.includes('Redirecting') && (
        <Link href="/forgot-password">Request New Reset Link</Link>
      )}
    </div>
  )}

  {/* API Error */}
  {error && (
    <div className="error-message">
      {error}
      {(error.includes('expired') || error.includes('invalid')) && (
        <Link href="/forgot-password">Request New Reset Link</Link>
      )}
    </div>
  )}

  {/* Form (only show if token is valid) */}
  {token && !tokenError && (
    <form onSubmit={handleSubmit}>
      {/* New Password */}
      <div>
        <label>New Password</label>
        <div className="relative">
          <input
            type={showPassword ? "text" : "password"}
            value={newPassword}
            onChange={(e) => {
              setNewPassword(e.target.value);
              setPasswordValidation(validatePassword(e.target.value));
            }}
            required
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? <EyeOff /> : <Eye />}
          </button>
        </div>

        {/* Real-time validation feedback */}
        {passwordValidation && !passwordValidation.isValid && (
          <ul className="validation-errors">
            {passwordValidation.errors.map((err, i) => (
              <li key={i}>{err}</li>
            ))}
          </ul>
        )}
      </div>

      {/* Confirm Password */}
      <div>
        <label>Confirm Password</label>
        <div className="relative">
          <input
            type={showConfirmPassword ? "text" : "password"}
            value={confirmPassword}
            onChange={(e) => {
              setConfirmPassword(e.target.value);
              setPasswordsMatch(e.target.value === newPassword);
            }}
            required
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
          >
            {showConfirmPassword ? <EyeOff /> : <Eye />}
          </button>
        </div>

        {!passwordsMatch && confirmPassword.length > 0 && (
          <p className="validation-error">Passwords do not match</p>
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
      >
        {isLoading ? (
          <>
            <Loader2 className="animate-spin" />
            Resetting Password...
          </>
        ) : (
          "Reset Password"
        )}
      </button>
    </form>
  )}

  {/* Back to Login */}
  <Link href="/login">Back to Login</Link>
</div>
```

### Accessibility

- Form labels properly associated with inputs
- Password visibility toggle buttons have `aria-label="Toggle password visibility"`
- Validation errors announced with `role="alert"` and `aria-live="assertive"`
- Submit button disabled state communicated with `aria-disabled`
- Loading state communicated with `aria-busy`

### Test Cases

1. **Valid Token and Password**:
   - Load page with valid token → Enter strong password → Confirm password → Submit
   - Verify redirect to login with success message

2. **Missing Token**:
   - Load `/reset-password` (no query param) → See error → Auto-redirect after 3s
   - Verify redirect to `/forgot-password`

3. **Malformed Token**:
   - Load with `?token=abc` → See "invalid format" error
   - Verify link to request new reset

4. **Expired Token**:
   - Submit with expired token → See "expired" error
   - Verify link to request new reset

5. **Password Validation**:
   - Enter "weak" → See all validation errors
   - Enter "StrongPass123!" → All validations pass
   - Verify submit button enabled/disabled accordingly

6. **Password Mismatch**:
   - Enter different passwords in confirm field → See "do not match" error
   - Verify submit button disabled

7. **Password Visibility Toggle**:
   - Click eye icon → Password visible
   - Click again → Password masked

8. **Session Invalidation**:
   - Reset password while logged in → Verify signOut called
   - Verify redirect to login (not dashboard)

---

## Component 3: LoginPage Enhancement

### Location

`frontend/app/(auth)/login/page.tsx` (existing file)

### Changes Required

Add "Forgot Password?" link to existing login form.

### Implementation

```tsx
{/* Existing password input */}
<div>
  <label>Password</label>
  <input type="password" {...} />
</div>

{/* NEW: Forgot Password Link */}
<div className="text-right mb-4">
  <Link
    href="/forgot-password"
    className="text-sm text-indigo-600 hover:text-indigo-500"
  >
    Forgot Password?
  </Link>
</div>

{/* Existing submit button */}
<button type="submit">Sign In</button>
```

### Success Message Display

Show success message after password reset:

```tsx
useEffect(() => {
  const searchParams = useSearchParams();
  if (searchParams.get('reset') === 'success') {
    setSuccessMessage('Your password has been reset successfully. Please log in with your new password.');
  }
}, []);

{/* Success message banner */}
{successMessage && (
  <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
    <p className="text-sm text-green-700">{successMessage}</p>
  </div>
)}
```

### Test Cases

1. **Forgot Password Link Visibility**:
   - Load login page → See "Forgot Password?" link below password field
   - Click link → Navigate to `/forgot-password`

2. **Reset Success Message**:
   - Load `/login?reset=success` → See success message
   - Verify message says "password has been reset successfully"

---

## Shared UI Components

### PasswordStrengthIndicator

**Purpose**: Visual indicator of password strength

```tsx
interface PasswordStrengthIndicatorProps {
  password: string;
  validation: PasswordValidation;
}

export function PasswordStrengthIndicator({ password, validation }: Props) {
  const strength = getStrength(password, validation);

  return (
    <div className="password-strength">
      <div className="strength-bar">
        <div
          className={`strength-fill strength-${strength}`}
          style={{ width: `${(strength / 4) * 100}%` }}
        />
      </div>
      <p className="strength-label">{getLabel(strength)}</p>
    </div>
  );
}

function getStrength(password: string, validation: PasswordValidation): number {
  if (password.length === 0) return 0;
  if (!validation.isValid) return Math.max(1, 4 - validation.errors.length);
  if (password.length >= 12) return 4; // Strong
  return 3; // Good
}

function getLabel(strength: number): string {
  switch (strength) {
    case 0: return '';
    case 1: return 'Weak';
    case 2: return 'Fair';
    case 3: return 'Good';
    case 4: return 'Strong';
    default: return '';
  }
}
```

**Usage**: Optional enhancement (not in MVP scope)

---

## Styling Consistency

### Colors (Tailwind)

- Primary: `indigo-600` (buttons, links)
- Error: `red-500` (error messages, validation errors)
- Success: `green-600` (success messages)
- Loading: `indigo-600` with opacity

### Typography

- Headings: `text-2xl font-bold`
- Body: `text-sm text-slate-600`
- Labels: `text-sm font-medium text-slate-700`
- Errors: `text-sm text-red-500`
- Success: `text-sm text-green-600`

### Spacing

- Page padding: `p-8`
- Form field gap: `space-y-4`
- Button margin: `mt-6`

---

## Notes

- All components use `"use client"` directive (Next.js App Router)
- Icons from `lucide-react` library (existing dependency)
- Consistent with existing login/register page patterns
- Responsive design (mobile-first)
- Loading states prevent duplicate submissions
- Error messages are user-friendly and actionable
