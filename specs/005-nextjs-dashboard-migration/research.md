# Research: Next.js Dashboard Migration

**Feature**: `005-nextjs-dashboard-migration`
**Date**: 2025-12-12
**Status**: Completed

## 1. Needs Clarification (Resolved)

### Integration with Auth Microservice
**Question**: How exactly does the Next.js app authenticate with the `auth-server`?
**Findings**:
- The `auth-server` uses `better-auth`.
- `better-auth` client library on the frontend handles cookie management automatically.
- Next.js Server Components can read the session cookie from incoming requests and validate it or pass it to backend services.
- **Decision**: Use `better-auth` client in Next.js. Configure proxy or direct fetch to `auth-server` URL. Since they are microservices, Next.js will need the `AUTH_SERVER_URL` env var.

### Backend Data Fetching
**Question**: How to share auth state with the Python backend?
**Findings**:
- The Python backend expects a token/cookie.
- The `auth-server` issues an HTTP-only cookie.
- Next.js API client (`@/lib/api.ts`) must manually attach the cookie from the incoming request (in Server Components) or the browser (in Client Components) when calling the Python backend.
- **Decision**: In Server Components, use `cookies()` from `next/headers` to extract the session cookie and forward it in the `Cookie` header to the backend.

## 2. Technology Choices

### Framework: Next.js 16 (App Router)
**Rationale**: Required by spec. Provides best performance and DX with Server Components.
**Best Practices**:
- Fetch data in Server Components (`page.tsx`, `layout.tsx`).
- Pass data to Client Components as props.
- Use `loading.tsx` for suspense boundaries.

### State Management: URL Search Params
**Rationale**: Required by spec (FR-011).
**Implementation**:
- Use `useSearchParams` hook in Client Components to read state.
- Use `useRouter` and `usePathname` to update state (pushing new URL).
- Server Components read `searchParams` prop to filter initial data fetch.

### UI Library: Tailwind CSS + Lucide React
**Rationale**: Matches existing design.
**Implementation**:
- Copy Tailwind config (colors, spacing) from `todo-app-login&dashboard`.
- Use `lucide-react` for icons (lightweight, consistent).

### Charts: Recharts
**Rationale**: Standard React charting library.
**Constraint**: Client-side only.
**Solution**: Create a `DashboardStats` component with `"use client"` directive or dynamic import with `ssr: false`.

## 3. Project Structure

**Decision**: Create a new directory `frontend` in the repo root.
**Reasoning**: Clear separation from `backend` and `auth-server`. Matches the "Option 2: Web application" pattern in the plan template.

Structure:
```
frontend/
├── app/
│   ├── (auth)/        # Route group for login/register
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/   # Route group for authenticated area
│   │   ├── layout.tsx # Sidebar/Header layout
│   │   ├── page.tsx   # Dashboard main view
│   │   └── loading.tsx
│   ├── layout.tsx     # Root layout (providers)
│   └── globals.css
├── components/
│   ├── ui/            # Reusable UI atoms (Button, Input)
│   ├── dashboard/     # Dashboard specific (Sidebar, Stats)
│   └── todo/          # Todo specific (List, Item, Modal)
├── lib/
│   ├── api.ts         # Unified API client
│   └── utils.ts       # Helper functions (cn)
├── types/
│   └── index.ts       # Shared interfaces
└── public/
```
