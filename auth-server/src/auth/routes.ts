import { Request, Response } from 'express';
import { prisma } from '../database/client.js';
import { betterAuth } from 'better-auth';
import { getAuthConfig } from './auth.config.js';

// Lazy initialize auth instance for session validation
let _authInstance: ReturnType<typeof betterAuth> | null = null;

function getAuthInstance() {
  if (!_authInstance) {
    _authInstance = betterAuth(getAuthConfig());
  }
  return _authInstance;
}

/**
 * GET /api/auth/me
 * Returns current user profile (id, email, name, image, emailVerified)
 */
export const getCurrentUser = async (req: Request, res: Response): Promise<void> => {
  try {
    // Get session from better-auth using the auth instance
    const auth = getAuthInstance();
    const sessionResult = await auth.api.getSession({
      headers: new Headers(req.headers as Record<string, string>),
    });

    if (!sessionResult || !sessionResult.session) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'No valid session found',
      });
      return;
    }

    const session = sessionResult.session;

    const user = await prisma.user.findUnique({
      where: { id: session.userId },
      select: {
        id: true,
        email: true,
        name: true,
        image: true,
        emailVerified: true,
      },
    });

    if (!user) {
      res.status(404).json({
        error: 'User not found',
        message: 'The authenticated user could not be found',
      });
      return;
    }

    res.json({
      user: {
        id: user.id,
        email: user.email,
        name: user.name || null,
        image: user.image || null,
        emailVerified: user.emailVerified || false,
      },
    });
  } catch (error) {
    console.error('Error getting current user:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'An error occurred while retrieving user information',
    });
  }
};

/**
 * GET /api/auth/sessions
 * Lists all user sessions with device info (id, token excerpt, expiresAt, ipAddress, userAgent, isCurrent flag)
 */
export const getUserSessions = async (req: Request, res: Response): Promise<void> => {
  try {
    // Get session from better-auth using the auth instance
    const auth = getAuthInstance();
    const sessionResult = await auth.api.getSession({
      headers: new Headers(req.headers as Record<string, string>),
    });

    if (!sessionResult || !sessionResult.session) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'No valid session found',
      });
      return;
    }

    const session = sessionResult.session;
    const userId = session.userId;

    // Get all sessions for the user using the Prisma Session model (not user_sessions)
    const sessions = await prisma.session.findMany({
      where: {
        userId: userId,
      },
      orderBy: {
        createdAt: 'desc',
      },
    });

    // Get current session ID to identify the current session
    const currentSessionId = session.id;

    const sessionList = sessions.map((dbSession: any) => ({
      id: dbSession.id,
      tokenExcerpt: dbSession.token?.substring(0, 8) || '',
      expiresAt: dbSession.expiresAt,
      ipAddress: dbSession.ipAddress || null,
      userAgent: dbSession.userAgent || null,
      isCurrent: dbSession.id === currentSessionId,
      createdAt: dbSession.createdAt,
    }));

    res.json({
      sessions: sessionList,
    });
  } catch (error) {
    console.error('Error getting user sessions:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'An error occurred while retrieving user sessions',
    });
  }
};

/**
 * DELETE /api/auth/sessions/:sessionId
 * Revokes a specific session with validation
 */
export const revokeSession = async (req: Request, res: Response): Promise<void> => {
  try {
    // Get session from better-auth using the auth instance
    const auth = getAuthInstance();
    const currentSessionResult = await auth.api.getSession({
      headers: new Headers(req.headers as Record<string, string>),
    });

    if (!currentSessionResult || !currentSessionResult.session) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'No valid session found',
      });
      return;
    }

    const currentSession = currentSessionResult.session;
    const { sessionId } = req.params;
    const currentUserId = currentSession.userId;
    const currentSessionId = currentSession.id;

    // Validate session ID format
    if (!sessionId || typeof sessionId !== 'string') {
      res.status(400).json({
        error: 'Bad Request',
        message: 'Invalid session ID provided',
      });
      return;
    }

    // Prevent revoking the current session
    if (sessionId === currentSessionId) {
      res.status(400).json({
        error: 'Bad Request',
        message: 'Cannot revoke current session. Please log out instead.',
      });
      return;
    }

    // Find the session to revoke
    const sessionToRevoke = await prisma.session.findFirst({
      where: {
        id: sessionId,
        userId: currentUserId,
      },
    });

    if (!sessionToRevoke) {
      res.status(404).json({
        error: 'Session not found',
        message: 'The specified session does not exist',
      });
      return;
    }

    // Delete the session (better-auth handles session revocation by deleting the record)
    await prisma.session.delete({
      where: { id: sessionId },
    });

    res.json({
      message: 'Session revoked successfully',
      sessionId: sessionId,
    });
  } catch (error) {
    console.error('Error revoking session:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: 'An error occurred while revoking the session',
    });
  }
};