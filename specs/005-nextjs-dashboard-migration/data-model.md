# Data Model: Next.js Dashboard

**Feature**: `005-nextjs-dashboard-migration`
**Date**: 2025-12-12

## Entities

### User
*Represents the authenticated user.*

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier (UUID) |
| email | string | User's email address |
| name | string? | Full name (optional) |
| image | string? | Avatar URL (optional) |
| emailVerified | boolean | Whether email is verified |

### Task
*Represents a todo item.*

| Field | Type | Description |
|-------|------|-------------|
| id | number | Unique identifier |
| title | string | Task summary |
| description | string? | Detailed description |
| completed | boolean | Completion status |
| user_id | string | Owner ID |
| created_at | string | ISO timestamp |
| updated_at | string | ISO timestamp |

### Session
*Represents an active user session.*

| Field | Type | Description |
|-------|------|-------------|
| id | string | Session ID |
| expiresAt | string | Expiration timestamp |
| userAgent | string? | Client user agent |
| ipAddress | string? | Client IP address |

## TypeScript Interfaces

```typescript
// types/index.ts

export interface User {
  id: string;
  email: string;
  name?: string | null;
  image?: string | null;
  emailVerified: boolean;
}

export interface Task {
  id: number;
  title: string;
  description?: string | null;
  completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
  // Note: Priority and Tags are in spec but not yet in backend schema. 
  // We will handle them as client-side mocks or pending backend updates 
  // if strictly required by UI, but for now we map to backend reality.
  // UPDATE: Spec FR-004 says "replicate visual design". 
  // If design has Priority/Tags, we might need to mock them or ask for backend update.
  // For migration, we'll map strictly to backend for functional parts 
  // and potentially hide/mock missing UI elements to avoid broken UI.
}

export interface TaskCreatePayload {
  title: string;
  description?: string;
}

export interface TaskUpdatePayload {
  title?: string;
  description?: string;
  completed?: boolean;
}

export interface AuthResponse {
  user: User;
  session: Session;
}
```

## State Management

### URL Search Params
Used for filtering task lists on the Dashboard.

| Param | Values | Description |
|-------|--------|-------------|
| filter | `all` (default), `active`, `completed` | Filter tasks by status |
| search | string | Search term for title/description |
