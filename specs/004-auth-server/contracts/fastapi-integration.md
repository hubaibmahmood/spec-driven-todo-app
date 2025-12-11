# FastAPI Integration with Better Auth Server

This document outlines how the FastAPI backend integrates with the Node.js Better Auth Server.

## Authentication Flow

1.  **Client (Frontend)**:
    *   Authenticates user via `auth-server` (e.g., `/api/auth/sign-in/email`).
    *   Receives a session token (and user object) in the response.

2.  **Client (Frontend)**:
    *   Attaches the session token to requests destined for the FastAPI backend.
    *   Header: `Authorization: Bearer <session_token>`

3.  **FastAPI Backend**:
    *   Middleware/Dependency: `get_current_user` (in `src/api/dependencies.py`).
    *   Extracts the Bearer token.
    *   Calls `src.services.auth_service.validate_session`.

4.  **Session Validation**:
    *   `validate_session` queries the shared PostgreSQL database table `user_sessions`.
    *   Checks if the token exists, is not expired, and is not revoked.
    *   **Note**: `better-auth` stores tokens in plain text in the database, so no hashing is performed by FastAPI for validation (unlike the initial plan).
    *   If valid, returns the `user_id`.

## Database Schema Compatibility

The integration relies on the `user_sessions` table structure managed by `better-auth`.

### `user_sessions` Table

| Column       | Type                     | Description                                      |
| :----------- | :----------------------- | :----------------------------------------------- |
| `id`         | `String` (cuid)          | Unique session ID                                |
| `token`      | `String`                 | The session token (index, unique)                |
| `userId`     | `String` (cuid)          | Reference to the User ID                         |
| `expiresAt`  | `DateTime`               | Expiration timestamp                             |
| `ipAddress`  | `String` (Optional)      | IP address of the client                         |
| `userAgent`  | `String` (Optional)      | User agent string                                |
| `createdAt`  | `DateTime`               | Creation timestamp                               |
| `updatedAt`  | `DateTime`               | Update timestamp                                 |
| `revoked`    | `Boolean` (custom added) | **Note**: Custom field added to schema if needed |

**Important**: The FastAPI `UserSession` model in `src/models/database.py` MUST match this schema. Specifically, the `token` column maps to the `token` field in Prisma.

## Environment Configuration

*   **Auth Server**:
    *   `DATABASE_URL`: Points to the PostgreSQL database.
    *   `PORT`: 8080 (default).

*   **FastAPI Backend**:
    *   `DATABASE_URL`: Points to the SAME PostgreSQL database.
    *   `AUTH_SERVER_URL`: `http://localhost:8080` (used for integration tests).

## Integration Testing

Integration tests (`backend/tests/integration/test_better_auth_integration.py`) verify this flow by:
1.  Registering a user on the `auth-server`.
2.  Verifying the email (fetching token from DB).
3.  Signing in to obtain a real session token.
4.  (In test env) Replicating that session into the test database (if using SQLite) or connecting to the real DB.
5.  Calling a protected FastAPI endpoint with the token.