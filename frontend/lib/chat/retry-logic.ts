// Network retry logic with exponential backoff
// Spec: 009-frontend-chat-integration - Phase 9 (T106-T107)

export interface RetryOptions {
  maxRetries?: number;
  initialDelay?: number;
  maxDelay?: number;
  backoffMultiplier?: number;
}

export interface RetryState {
  attempt: number;
  nextDelay: number;
  isRetrying: boolean;
}

const DEFAULT_OPTIONS: Required<RetryOptions> = {
  maxRetries: 3,
  initialDelay: 1000, // 1 second
  maxDelay: 8000, // 8 seconds
  backoffMultiplier: 2,
};

/**
 * Execute a fetch request with exponential backoff retry logic
 * @param fetchFn - Function that returns a fetch promise
 * @param options - Retry configuration options
 * @returns Promise that resolves with the fetch response
 * @throws Error if all retries are exhausted
 */
export async function fetchWithRetry<T>(
  fetchFn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  let lastError: Error | null = null;
  let delay = opts.initialDelay;

  for (let attempt = 0; attempt <= opts.maxRetries; attempt++) {
    try {
      return await fetchFn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error');

      // Don't retry for authentication errors (401) or client errors (4xx)
      if (error instanceof Error && error.message.includes('401')) {
        throw error;
      }

      // Don't retry if this was the last attempt
      if (attempt === opts.maxRetries) {
        break;
      }

      // Wait before retrying (exponential backoff)
      await sleep(delay);

      // Calculate next delay with exponential backoff, capped at maxDelay
      delay = Math.min(delay * opts.backoffMultiplier, opts.maxDelay);
    }
  }

  // All retries exhausted
  throw new Error(
    `Network request failed after ${opts.maxRetries} retries: ${lastError?.message || 'Unknown error'}`
  );
}

/**
 * Calculate the next retry delay using exponential backoff
 * @param attempt - Current retry attempt number (0-indexed)
 * @param options - Retry configuration options
 * @returns Delay in milliseconds before next retry
 */
export function calculateRetryDelay(attempt: number, options: RetryOptions = {}): number {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const delay = opts.initialDelay * Math.pow(opts.backoffMultiplier, attempt);
  return Math.min(delay, opts.maxDelay);
}

/**
 * Sleep for a specified duration
 * @param ms - Milliseconds to sleep
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Check if an error is retryable (network errors, 5xx server errors)
 * @param error - Error to check
 * @returns true if the error is retryable
 */
export function isRetryableError(error: Error): boolean {
  const message = error.message.toLowerCase();

  // Retry network errors
  if (
    message.includes('network') ||
    message.includes('fetch') ||
    message.includes('timeout') ||
    message.includes('connection')
  ) {
    return true;
  }

  // Retry server errors (5xx)
  if (message.includes('500') || message.includes('502') || message.includes('503')) {
    return true;
  }

  // Don't retry authentication or client errors
  if (message.includes('401') || message.includes('403') || message.includes('400')) {
    return false;
  }

  return false;
}
