# API Client Contract

**Client**: `@/lib/api.ts`
**Services**: `backend` (FastAPI), `auth-server` (Express)

## Interface Definition

The `api` object exported from `@/lib/api` must satisfy the following interface:

```typescript
interface ApiClient {
  // Auth
  getCurrentUser(): Promise<User | null>;
  
  // Tasks
  getTasks(): Promise<Task[]>;
  createTask(data: TaskCreatePayload): Promise<Task>;
  updateTask(id: number, data: TaskUpdatePayload): Promise<Task>;
  deleteTask(id: number): Promise<void>;
  
  // AI (Deferred)
  enhanceTask(title: string): Promise<{ title: string; description: string; tags: string[] }>;
}
```

## Implementation Details

- **Base URLs**:
  - Backend: `process.env.BACKEND_URL` (e.g., `http://localhost:8000`)
  - Auth: `process.env.AUTH_URL` (e.g., `http://localhost:4000`)

- **Authentication**:
  - The client must automatically attach the session cookie to requests.
  - In **Server Components**, this requires reading `cookies()` from `next/headers` and setting the `Cookie` header.
  - In **Client Components**, the browser handles this automatically for same-origin (or correctly CORS-configured) requests. Since we are SSR-ing, we primarily focus on the Server Component path.
  - **Strategy**: The `api` methods should detect the environment or accept an optional config object to pass headers. Ideally, we implement a `fetch` wrapper that handles this.

## Error Handling

- **401 Unauthorized**: Redirect to `/login`.
- **Network Error**: Throw `Error` with message "Failed to connect to server".
- **Validation Error**: Throw `Error` with details from response body.
