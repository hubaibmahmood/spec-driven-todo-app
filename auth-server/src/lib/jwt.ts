/**
 * JWT token generation and refresh token utilities for auth-server.
 */

import jwt from 'jsonwebtoken';
import crypto from 'crypto';

/**
 * JWT payload interface.
 */
export interface JWTPayload {
  sub: string;  // user ID
  iat: number;  // issued at (Unix timestamp)
  exp: number;  // expiration (Unix timestamp)
  type: 'access';
}

/**
 * Configuration from environment variables.
 */
const JWT_SECRET = process.env.JWT_SECRET || 'dev-jwt-secret-min-32-chars-change-in-production-please';
const JWT_ALGORITHM = 'HS256';
const JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30;

/**
 * Generate a JWT access token for the given user ID.
 *
 * @param userId - The user's unique identifier
 * @returns A signed JWT access token string
 */
export function generateAccessToken(userId: string): string {
  const now = Math.floor(Date.now() / 1000);
  const expiresAt = now + (JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60);

  const payload: JWTPayload = {
    sub: userId,
    iat: now,
    exp: expiresAt,
    type: 'access'
  };

  return jwt.sign(payload, JWT_SECRET, { algorithm: JWT_ALGORITHM });
}

/**
 * Generate a cryptographically secure refresh token.
 *
 * @returns A URL-safe base64-encoded random string (32 bytes)
 */
export function generateRefreshToken(): string {
  return crypto.randomBytes(32).toString('base64url');
}

/**
 * Hash a refresh token using SHA-256.
 *
 * @param token - The refresh token to hash
 * @returns Hexadecimal string of the SHA-256 hash
 */
export function hashRefreshToken(token: string): string {
  return crypto.createHash('sha256').update(token).digest('hex');
}
