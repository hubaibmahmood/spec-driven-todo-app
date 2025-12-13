import { Request, Response, NextFunction } from 'express';

/**
 * Standardized error response interface
 */
interface ErrorResponse {
  error: string;
  message: string;
  statusCode: number;
  timestamp: string;
  path?: string;
  details?: unknown;
}

/**
 * Custom error class for application errors
 */
export class AppError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'AppError';
    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * Global error handler middleware
 *
 * Catches all errors and returns standardized error responses
 */
export function errorHandler(
  err: Error | AppError,
  req: Request,
  res: Response,
  next: NextFunction
): void {
  const isProduction = process.env.NODE_ENV === 'production';

  // Default error values
  let statusCode = 500;
  let message = 'Internal server error';
  let details: unknown = undefined;

  // Handle custom AppError
  if (err instanceof AppError) {
    statusCode = err.statusCode;
    message = err.message;
    details = err.details;
  }
  // Handle known error types
  else if (err.name === 'ValidationError') {
    statusCode = 400;
    message = 'Validation error';
    details = err.message;
  }
  else if (err.name === 'UnauthorizedError') {
    statusCode = 401;
    message = 'Unauthorized';
  }
  else if (err.name === 'ForbiddenError') {
    statusCode = 403;
    message = 'Forbidden';
  }
  else if (err.name === 'NotFoundError') {
    statusCode = 404;
    message = 'Resource not found';
  }
  // Handle generic errors
  else if (!isProduction) {
    message = err.message || message;
    details = {
      stack: err.stack,
      name: err.name,
    };
  }

  // Log error (in production, this would go to a logging service)
  console.error('[Error Handler]', {
    statusCode,
    message,
    path: req.path,
    method: req.method,
    timestamp: new Date().toISOString(),
    error: isProduction ? undefined : err.stack,
  });

  // Construct error response
  const errorResponse: ErrorResponse = {
    error: err.name || 'Error',
    message,
    statusCode,
    timestamp: new Date().toISOString(),
    path: req.path,
  };

  // Only include details in development or for AppErrors
  if (details !== undefined && (!isProduction || err instanceof AppError)) {
    errorResponse.details = details;
  }

  // Send error response
  res.status(statusCode).json(errorResponse);
}

/**
 * 404 Not Found handler middleware
 *
 * Should be placed after all routes to catch unmatched requests
 */
export function notFoundHandler(
  req: Request,
  res: Response,
  next: NextFunction
): void {
  const error = new AppError(
    404,
    `Cannot ${req.method} ${req.path}`,
    {
      method: req.method,
      path: req.path,
    }
  );
  next(error);
}

/**
 * Async handler wrapper to catch errors in async route handlers
 *
 * Usage:
 *   app.get('/route', asyncHandler(async (req, res) => {
 *     const data = await someAsyncOperation();
 *     res.json(data);
 *   }));
 */
export function asyncHandler(
  fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
) {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}
