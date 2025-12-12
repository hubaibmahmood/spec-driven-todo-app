# Tasks: Next.js Dashboard Migration

**Feature**: `005-nextjs-dashboard-migration`
**Status**: Pending
**Spec**: [Feature Spec](./spec.md)

## Phase 1: Setup
*Goal: Initialize the Next.js project and configure core dependencies.*

- [x] T001 Initialize Next.js project (App Router) in `frontend/`
- [x] T002 Install dependencies (Tailwind, Lucide, Recharts) in `frontend/package.json`
- [x] T003 Configure Tailwind CSS and global styles in `frontend/tailwind.config.ts` and `frontend/app/globals.css`
- [x] T004 Create TypeScript interfaces in `frontend/types/index.ts`
- [x] T005 [P] Implement base HTTP client (fetch wrapper with error handling) in `frontend/lib/http-client.ts`
- [x] T006 [P] Configure API service modules (Auth & Todo endpoints) in `frontend/lib/api.ts`

## Phase 2: Foundational
*Goal: Build the shared layout structure and navigation.*

- [x] T007 [P] Create Sidebar component UI in `frontend/components/dashboard/Sidebar.tsx`
- [x] T008 [P] Create Header/Topbar component UI in `frontend/components/dashboard/Header.tsx`
- [x] T009 Implement Root Layout with Sidebar/Header in `frontend/app/layout.tsx`

## Phase 3: User Story 1 (Authentication)
*Goal: Users can sign up and log in.*

- [x] T010 [US1] Create Login page UI in `frontend/app/(auth)/login/page.tsx`
- [x] T011 [US1] Create Register page UI in `frontend/app/(auth)/register/page.tsx`
- [x] T012 [US1] Implement Login form submission logic in `frontend/app/(auth)/login/page.tsx`
- [x] T013 [US1] Implement Register form submission logic in `frontend/app/(auth)/register/page.tsx`
- [x] T014 [US1] Implement Next.js Middleware for route protection in `frontend/middleware.ts`

## Phase 4: User Story 2 (Dashboard & Overview)
*Goal: Users can view their dashboard stats and task list.*

- [x] T015 [US2] Create DashboardStats component structure in `frontend/components/dashboard/DashboardStats.tsx`
- [x] T016 [US2] Implement Recharts integration in `frontend/components/dashboard/DashboardStats.tsx`
- [x] T017 [US2] Create TodoItem component UI in `frontend/components/todo/TodoItem.tsx`
- [x] T018 [US2] Create TaskList component UI in `frontend/components/dashboard/TaskList.tsx`
- [x] T019 [US2] Implement Dashboard page data fetching in `frontend/app/(dashboard)/page.tsx`

## Phase 5: User Story 3 (Task Management)
*Goal: Users can create, update, and delete tasks.*

- [x] T020 [US3] Create AddTodoModal component UI in `frontend/components/todo/AddTodoModal.tsx`
- [x] T021 [US3] Implement Add/Edit task logic in `frontend/components/todo/AddTodoModal.tsx`
- [x] T022 [US3] Implement TodoItem interactions (Toggle, Delete) in `frontend/components/todo/TodoItem.tsx`

## Phase 6: User Story 4 (Search & Filter)
*Goal: Users can filter tasks by status and search by text.*

- [x] T023 [US4] Create FilterBar component UI in `frontend/components/dashboard/FilterBar.tsx`
- [x] T024 [US4] Integrate FilterBar with URL search params in `frontend/components/dashboard/FilterBar.tsx`
- [x] T025 [US4] Update Dashboard page to filter tasks based on params in `frontend/app/(dashboard)/page.tsx`

## Phase 7: Polish
*Goal: Ensure quality and visual consistency.*

- [x] T026 Fix any hydration errors or console warnings in `frontend/`
- [x] T027 Verify pixel-perfect design against reference in `todo-app-login&dashboard/`
- [x] T028 Optimize production build in `frontend/next.config.ts`

## Dependencies

- **US1**: T001-T009 must be complete.
- **US2**: Depends on US1 (need auth to view dashboard).
- **US3**: Depends on US2 (need list to add/edit).
- **US4**: Depends on US2 (need list to filter).

## Parallel Execution Opportunities

- **T007 & T008**: Sidebar and Header are independent.
- **T010 & T011**: Login and Register UIs are independent.
- **T015 & T017**: Stats and TodoItem components are independent.
- **T020 & T023**: Add Modal and FilterBar are independent.

## Implementation Strategy

1. **Setup**: Initialize project, styling, and robust API layer.
2. **Auth MVP**: Get users logged in and protected (US1 + Middleware).
3. **Dashboard Read**: Show data (US2).
4. **Dashboard Write**: Manipulate data (US3).
5. **Refine**: Add search/filter (US4).