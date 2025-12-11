# Tasks: Next.js Dashboard Migration

**Feature**: `005-nextjs-dashboard-migration`
**Status**: Pending
**Spec**: [Feature Spec](./spec.md)

## Phase 1: Setup
*Goal: Initialize the Next.js project and configure core dependencies.*

- [ ] T001 Initialize Next.js project (App Router) in `frontend/`
- [ ] T002 Install dependencies (Tailwind, Lucide, Recharts) in `frontend/package.json`
- [ ] T003 Configure Tailwind CSS and global styles in `frontend/tailwind.config.ts` and `frontend/app/globals.css`
- [ ] T004 Create TypeScript interfaces in `frontend/types/index.ts`
- [ ] T005 [P] Implement API client with fetch wrapper in `frontend/lib/api.ts`

## Phase 2: Foundational
*Goal: Build the shared layout structure and navigation.*

- [ ] T006 [P] Create Sidebar component UI in `frontend/components/dashboard/Sidebar.tsx`
- [ ] T007 [P] Create Header/Topbar component UI in `frontend/components/dashboard/Header.tsx`
- [ ] T008 Implement Root Layout with Sidebar/Header in `frontend/app/layout.tsx`

## Phase 3: User Story 1 (Authentication)
*Goal: Users can sign up and log in.*

- [ ] T009 [US1] Create Login page UI in `frontend/app/(auth)/login/page.tsx`
- [ ] T010 [US1] Create Register page UI in `frontend/app/(auth)/register/page.tsx`
- [ ] T011 [US1] Implement Login form submission logic in `frontend/app/(auth)/login/page.tsx`
- [ ] T012 [US1] Implement Register form submission logic in `frontend/app/(auth)/register/page.tsx`

## Phase 4: User Story 2 (Dashboard & Overview)
*Goal: Users can view their dashboard stats and task list.*

- [ ] T013 [US2] Create DashboardStats component structure in `frontend/components/dashboard/DashboardStats.tsx`
- [ ] T014 [US2] Implement Recharts integration in `frontend/components/dashboard/DashboardStats.tsx`
- [ ] T015 [US2] Create TodoItem component UI in `frontend/components/todo/TodoItem.tsx`
- [ ] T016 [US2] Create TaskList component UI in `frontend/components/dashboard/TaskList.tsx`
- [ ] T017 [US2] Implement Dashboard page data fetching in `frontend/app/(dashboard)/page.tsx`

## Phase 5: User Story 3 (Task Management)
*Goal: Users can create, update, and delete tasks.*

- [ ] T018 [US3] Create AddTodoModal component UI in `frontend/components/todo/AddTodoModal.tsx`
- [ ] T019 [US3] Implement Add/Edit task logic in `frontend/components/todo/AddTodoModal.tsx`
- [ ] T020 [US3] Implement TodoItem interactions (Toggle, Delete) in `frontend/components/todo/TodoItem.tsx`

## Phase 6: User Story 4 (Search & Filter)
*Goal: Users can filter tasks by status and search by text.*

- [ ] T021 [US4] Create FilterBar component UI in `frontend/components/dashboard/FilterBar.tsx`
- [ ] T022 [US4] Integrate FilterBar with URL search params in `frontend/components/dashboard/FilterBar.tsx`
- [ ] T023 [US4] Update Dashboard page to filter tasks based on params in `frontend/app/(dashboard)/page.tsx`

## Phase 7: Polish
*Goal: Ensure quality and visual consistency.*

- [ ] T024 Fix any hydration errors or console warnings in `frontend/`
- [ ] T025 Verify pixel-perfect design against reference in `todo-app-login&dashboard/`
- [ ] T026 Optimize production build in `frontend/next.config.ts`

## Dependencies

- **US1**: T001-T008 must be complete.
- **US2**: Depends on US1 (need auth to view dashboard).
- **US3**: Depends on US2 (need list to add/edit).
- **US4**: Depends on US2 (need list to filter).

## Parallel Execution Opportunities

- **T006 & T007**: Sidebar and Header are independent.
- **T009 & T010**: Login and Register UIs are independent.
- **T013 & T015**: Stats and TodoItem components are independent.
- **T018 & T021**: Add Modal and FilterBar are independent.

## Implementation Strategy

1. **Setup**: Initialize project and styling.
2. **Auth MVP**: Get users logged in (US1).
3. **Dashboard Read**: Show data (US2).
4. **Dashboard Write**: Manipulate data (US3).
5. **Refine**: Add search/filter (US4).
