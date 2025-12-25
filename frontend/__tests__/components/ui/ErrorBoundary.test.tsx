/**
 * Tests for ErrorBoundary component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';

// Component that throws an error for testing
function ThrowError({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error for ErrorBoundary');
  }
  return <div>No error</div>;
}

// Suppress console.error for these tests since we're intentionally throwing errors
const originalError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalError;
});

describe('ErrorBoundary', () => {
  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>Test Content</div>
      </ErrorBoundary>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('renders error UI when a child component throws an error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    // Check for error message
    expect(screen.getByText(/Oops! Something went wrong/i)).toBeInTheDocument();
    expect(screen.getByText(/We encountered an unexpected error/i)).toBeInTheDocument();
  });

  it('displays Try Again button when error occurs', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByRole('button', { name: /Try Again/i })).toBeInTheDocument();
  });

  it('displays Go to Dashboard button when error occurs', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByRole('button', { name: /Go to Dashboard/i })).toBeInTheDocument();
  });

  it('resets error state when Try Again is clicked', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    // Error UI should be visible
    expect(screen.getByText(/Oops! Something went wrong/i)).toBeInTheDocument();

    // Click Try Again button
    const tryAgainButton = screen.getByRole('button', { name: /Try Again/i });
    fireEvent.click(tryAgainButton);

    // Re-render with no error
    rerender(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );

    // Should show normal content now
    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('renders custom fallback when provided', () => {
    const customFallback = <div>Custom Error Message</div>;

    render(
      <ErrorBoundary fallback={customFallback}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Custom Error Message')).toBeInTheDocument();
  });

  it('shows error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    // Should show error details in development
    expect(screen.getByText(/Error:/i)).toBeInTheDocument();
    expect(screen.getByText(/Test error for ErrorBoundary/i)).toBeInTheDocument();

    process.env.NODE_ENV = originalEnv;
  });

  it('hides error details in production mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'production';

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    // Should NOT show detailed error in production
    expect(screen.queryByText(/Error:/i)).not.toBeInTheDocument();

    process.env.NODE_ENV = originalEnv;
  });
});
