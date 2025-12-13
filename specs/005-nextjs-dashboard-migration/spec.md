# Feature Specification: Next.js Dashboard Migration

**Feature Branch**: `005-nextjs-dashboard-migration`
**Created**: 2025-12-12
**Status**: Draft
**Input**: User description: "create specification for creating the exact same signin/signup forms and dashboard that is implemented in @todo-app-login&dashboard/** using Next.js 16+ (App Router) instead of react, TypeScript and Tailwind CSS..."

## Clarifications

### Session 2025-12-12
- Q: State management for filters/search? → A: URL Search Params (Option A).
- Q: How will user authentication sessions be managed? → A: By `@auth-server` microservice using `better-auth`.
- Q: What is the preferred implementation strategy for the `@/lib/api.ts` client to interact with the backend services (both todo and auth)? → A: New Client using Fetch (Option A).
- Q: How should the existing AI integrations (`geminiService.ts`) be handled in the Next.js application, especially considering the security implications of API keys and the preference for Server Components? → A: API Routes (Option A).
- Q: How should environment variables, particularly API keys and backend URLs, be managed within the Next.js application to ensure security and proper access in both server and client contexts? → A: Server-only and Client-exposed with `NEXT_PUBLIC_` (Option A).

## User Scenarios & Testing

<!--
  Prioritized user journeys for the Next.js migration.
-->

### User Story 1 - User Authentication (Priority: P1)

Users must be able to securely sign up and log in to access their dashboard, using the existing UI design.

**Why this priority**: Access to the application is the prerequisite for all other functionality.

**Independent Test**: Can be tested by navigating to the login page, entering credentials, and verifying redirection to the dashboard.

**Acceptance Scenarios**:

1. **Given** a guest user, **When** they visit the root URL, **Then** they are redirected to the login page (or dashboard if session exists).
2. **Given** a user on the login page, **When** they toggle "Sign up", **Then** the form fields update to include "Full Name".
3. **Given** valid credentials, **When** the user submits the form, **Then** they are redirected to the dashboard.

---

### User Story 2 - Dashboard & Task Overview (Priority: P1)

Users see a dashboard with statistical summaries and a list of their tasks, replicating the existing visual layout.

**Why this priority**: Core value proposition; provides immediate visibility into work.

**Independent Test**: Verify the dashboard loads with correct layout, sidebar, stats cards, and task list.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they load the dashboard, **Then** they see the Sidebar, Header, Stats Cards, and Task List.
2. **Given** tasks exist, **When** viewing the stats area, **Then** the "Total", "Completion Rate", "High Priority", and "Pending" cards display correct calculated values.
3. **Given** the mobile view, **When** the menu button is clicked, **Then** the sidebar toggles visibility.

---

### User Story 3 - Task Management (CRUD) (Priority: P1)

Users can create, edit, delete, and toggle the status of tasks.

**Why this priority**: Fundamental interaction with the Todo application.

**Independent Test**: Perform the full lifecycle of a task (Create -> Read -> Update -> Delete) and verify persistence.

**Acceptance Scenarios**:

1. **Given** the dashboard, **When** "New Task" is clicked, **Then** the Add/Edit modal opens.
2. **Given** the modal, **When** a task is saved, **Then** the list updates to include the new task.
3. **Given** a task, **When** its checkbox is clicked, **Then** its status toggles between Todo and Completed.
4. **Given** a task, **When** "Delete" is selected from the menu, **Then** the task is removed from the list.

---

### User Story 4 - Search and Filter (Priority: P2)

Users can filter tasks by status (All, Active, Completed) and search by text.

**Why this priority**: Usability requirement for managing large lists.

**Independent Test**: Apply filters and search terms, verifying the list reflects the criteria.

**Acceptance Scenarios**:

1. **Given** a list of mixed tasks, **When** "Completed" filter is applied, **Then** only completed tasks are shown.
2. **Given** a search term, **When** typed into the search box, **Then** only tasks matching the title or tags are displayed.

---

### User Story 5 - AI Enhancements (Priority: P3 - Deferred)

Users can use AI to enhance task descriptions and break down tasks into subtasks.

**Why this priority**: Differentiator feature providing "smart" capabilities, but can be deferred.

**Independent Test**: Trigger "Enhance" in the modal or "AI Breakdown" on a task item.

**Acceptance Scenarios**:

1. **Given** a draft title in the modal, **When** "Enhance" is clicked, **Then** the title, description, and tags are updated with AI-generated content.
2. **Given** an existing task, **When** "AI Breakdown" is clicked, **Then** subtasks are generated and added to the task.

### Edge Cases

- **API Unavailability**: How does the system handle failures when fetching tasks or stats? (Should display an error state or toast notification).
- **Empty States**: How does the dashboard look for a new user with zero tasks? (Should match the "No tasks found" design).
- **Mobile Sidebar Interaction**: Does the sidebar close when clicking the overlay or navigating? (Must ensure overlay click dismisses the menu).
- **Session Expiry**: What happens if the auth token expires while on the dashboard? (Should redirect to login on next action/refresh).

## Requirements

### Functional Requirements

- **FR-001**: The application MUST be built using Next.js 16+ with the App Router architecture.
- **FR-002**: The application MUST use Server Components by default; Client Components (`"use client"`) MUST be restricted to interactive elements (forms, modals, toggle buttons).
- **FR-003**: All backend data fetching and mutations MUST flow through a unified API client at `@/lib/api.ts`.
- **FR-004**: The UI MUST replicate the visual design of the existing `todo-app-login&dashboard` (Tailwind CSS classes, spacing, colors, icons).
- **FR-005**: The application MUST NOT use inline styles; all styling must use Tailwind utility classes.
- **FR-006**: The application MUST integrate with the `@auth-server` microservice for all authentication (login, signup, session management).
- **FR-007**: The application MUST implement the `Layout` component with responsive sidebar behavior.
- **FR-008**: The application MUST implement the `DashboardStats` component using `recharts` (or equivalent compatible with Next.js SSR/CSR), utilizing dynamic imports with `ssr: false` for client-side rendering.
- **FR-009**: The application MUST implement `TodoItem` and `AddTodoModal` components with full interactivity.
- **FR-010**: The application MUST integrate AI services via Next.js API Routes (`app/api/ai/...`) to proxy requests to the Gemini API, maintaining server-side security for API keys. (P3 - Deferred)
- **FR-011**: The application MUST manage filter and search state via URL search parameters (`?filter=...&search=...`) to support Server Component data fetching and shareable URLs.

### Technical Constraints & Patterns

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: `lucide-react`
- **Authentication**: Via `@auth-server` microservice (Express.js + better-auth)
- **Data Fetching**:
    - Usage: `import { api } from '@/lib/api'`
    - Pattern: `const tasks = await api.getTasks()`
    - Implementation: A new API client in `@/lib/api.ts` will be created using native `fetch` with appropriate headers/cookies.
- **Directory Structure**:
    - `/app`: Pages (`page.tsx`, `layout.tsx`, `loading.tsx`)
    - `/components`: Reusable UI components
    - `/lib`: Utilities and API client (`api.ts`)
    - `/types`: TypeScript definitions
- **Environment Variables**: Sensitive keys (e.g., API keys) MUST be server-only (stored in `.env`). Public/client-exposed variables (e.g., public API URLs) MUST be prefixed with `NEXT_PUBLIC_`.

### Key Entities

- **Todo**: Represents a task (id, title, description, priority, status, dueDate, createdAt, tags).
- **SubTask**: A breakdown item of a Todo (id, title, completed).
- **User**: The authenticated user (name, email).

## Success Criteria

### Measurable Outcomes

- **SC-001**: The application successfully builds (`npm run build`) without errors.
- **SC-002**: All 5 User Stories are verifiable manually in the browser.
- **SC-003**: The visual layout matches the reference `todo-app-login&dashboard` pixel-for-pixel (within reasonable margin).
- **SC-004**: No "Hydration failed" errors appear in the console during navigation.
- **SC-005**: All API calls utilize the `@/lib/api` abstraction layer.

## Assumptions

- The `api.getTasks()` and similar methods in `lib/api.ts` will initially return mock data or connect to the existing backend if available, but the *interface* is the strict requirement.
- "Exact same" implies replicating the *behavior* and *look*, adapted to the Next.js routing model (e.g., using `next/navigation` for redirects).
- The `recharts` library requires client-side rendering; appropriate "use client" directives or dynamic imports will be handled.