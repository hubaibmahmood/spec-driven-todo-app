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
