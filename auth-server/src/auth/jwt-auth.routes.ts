import { Request, Response } from 'express';
import { prisma } from '../database/client.js';
import { betterAuth } from 'better-auth';
import { getAuthConfig } from './auth.config.js';
import { generateAccessToken, generateRefreshToken, hashRefreshToken } from '../lib/jwt.js';

// Lazy initialize auth instance
let _authInstance: ReturnType<typeof betterAuth> | null = null;

function getAuthInstance() {
  if (!_authInstance) {
    _authInstance = betterAuth(getAuthConfig());
  }
  return _authInstance;
}

/**
 * POST /api/auth/jwt/sign-in
 * Enhanced login endpoint that issues JWT access token + refresh token
 */
export const jwtSignIn = async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      res.status(400).json({
        error: 'Bad Request',
        message: 'Email and password are required',
      });
      return;
    }

    // Use better-auth to authenticate the user
    const auth = getAuthInstance();

    // Call better-auth's sign-in endpoint internally
    const signInResult = await auth.api.signInEmail({
      body: {
        email,
        password,
      },
    });

    if (!signInResult || !signInResult.session || !signInResult.user) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Invalid email or password',
      });
      return;
    }

    const { session, user } = signInResult;

    // Generate JWT access token (30 minutes)
    const accessToken = generateAccessToken(user.id);

    // Generate refresh token (7 days)
    const refreshToken = generateRefreshToken();
    const hashedRefreshToken = hashRefreshToken(refreshToken);

    // Store hashed refresh token in database
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days
    const ipAddress = req.ip || req.headers['x-forwarded-for'] as string || '';
    const userAgent = req.headers['user-agent'] || '';

    await prisma.session.create({
      data: {
        userId: user.id,
        token: hashedRefreshToken,
        expiresAt: expiresAt,
        ipAddress: ipAddress,
        userAgent: userAgent,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    });

    // Set httpOnly cookie for refresh token (secure, SameSite=Strict)
    res.cookie('refresh_token', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days in milliseconds
      path: '/',
    });

    // Return access token and user info in response body
    res.json({
      accessToken: accessToken,
      user: {
        id: user.id,
        email: user.email,
        name: user.name || null,
        image: user.image || null,
        emailVerified: user.emailVerified || false,
      },
    });
  } catch (error) {
    console.error('Error in JWT sign-in:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'An error occurred during sign-in',
    });
  }
};

/**
 * POST /api/auth/jwt/sign-up
 * Enhanced signup endpoint that issues JWT access token + refresh token
 */
export const jwtSignUp = async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, password, name } = req.body;

    if (!email || !password) {
      res.status(400).json({
        error: 'Bad Request',
        message: 'Email and password are required',
      });
      return;
    }

    // Use better-auth to register the user
    const auth = getAuthInstance();

    // Call better-auth's sign-up endpoint internally
    const signUpResult = await auth.api.signUpEmail({
      body: {
        email,
        password,
        name: name || undefined,
      },
    });

    if (!signUpResult || !signUpResult.user) {
      res.status(400).json({
        error: 'Bad Request',
        message: 'User registration failed. Email may already be in use.',
      });
      return;
    }

    const { user } = signUpResult;

    // Generate JWT access token (30 minutes)
    const accessToken = generateAccessToken(user.id);

    // Generate refresh token (7 days)
    const refreshToken = generateRefreshToken();
    const hashedRefreshToken = hashRefreshToken(refreshToken);

    // Store hashed refresh token in database
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days
    const ipAddress = req.ip || req.headers['x-forwarded-for'] as string || '';
    const userAgent = req.headers['user-agent'] || '';

    await prisma.session.create({
      data: {
        userId: user.id,
        token: hashedRefreshToken,
        expiresAt: expiresAt,
        ipAddress: ipAddress,
        userAgent: userAgent,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    });

    // Set httpOnly cookie for refresh token (secure, SameSite=Strict)
    res.cookie('refresh_token', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days in milliseconds
      path: '/',
    });

    // Return access token and user info in response body
    res.json({
      accessToken: accessToken,
      user: {
        id: user.id,
        email: user.email,
        name: user.name || null,
        image: user.image || null,
        emailVerified: user.emailVerified || false,
      },
      message: 'Registration successful. Please check your email to verify your account.',
    });
  } catch (error) {
    console.error('Error in JWT sign-up:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'An error occurred during registration',
    });
  }
};
