# Tasks: Reset Password Frontend Integration

**Input**: Design documents from `/specs/011-reset-password-frontend/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT included (not requested in feature specification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Task Sizing**: All tasks sized for **15-30 minutes** of focused work

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/` for Next.js application
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Validation utilities and type definitions used by all user stories

**Estimated Time**: ~1.5 hours

- [ ] T001 [P] Create `lib/validation/` directory and implement email validation helper function in `frontend/lib/validation/password.ts`
- [ ] T002 [P] Define TypeScript interfaces (PasswordValidation, RateLimitCheck) in `frontend/lib/validation/password.ts`
- [ ] T003 [P] Implement password validation function with 5 regex rules (length, uppercase, lowercase, number, special char) in `frontend/lib/validation/password.ts`
- [ ] T004 [P] Implement rate limiting utilities with localStorage (checkRateLimit, recordAttempt) in `frontend/lib/validation/rate-limit.ts`
- [ ] T005 [P] Implement token format validator function with regex pattern in `frontend/lib/validation/password.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Estimated Time**: ~30 minutes

- [ ] T006 Verify better-auth client SDK configuration in `frontend/lib/auth-client.ts` and create auth route directories `app/(auth)/forgot-password/` and `app/(auth)/reset-password/`
- [ ] T007 [P] Define shared TypeScript form state interfaces (ForgotPasswordFormState, ResetPasswordFormState) in `frontend/lib/types/password-reset.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Forgot Password Request (Priority: P1) 🎯 MVP

**Goal**: Users can request a password reset email through a dedicated forgot password page

**Independent Test**: Navigate to `/forgot-password`, enter a registered email, submit, and see confirmation message that reset email was sent

**Estimated Time**: ~2 hours

### UI Components for User Story 1

- [ ] T008 [US1] Create forgot password page component shell with basic layout, heading, description, and "Back to Login" link in `frontend/app/(auth)/forgot-password/page.tsx`
- [ ] T009 [US1] Add email input field with Mail icon, placeholder, and Tailwind styling in `frontend/app/(auth)/forgot-password/page.tsx`
- [ ] T010 [US1] Implement form state management with useState hooks (email, isLoading, error, successMessage, rateLimitRemaining) in `frontend/app/(auth)/forgot-password/page.tsx`
- [ ] T011 [US1] Add client-side email format validation on form submit using email regex in `frontend/app/(auth)/forgot-password/page.tsx`
- [ ] T012 [US1] Integrate rate limit check before API call using checkRateLimit and record attempts on success using recordAttempt in `frontend/app/(auth)/forgot-password/page.tsx`
- [ ] T013 [US1] Implement authClient.forgetPassword API integration with onRequest, onSuccess, and onError callbacks in `frontend/app/(auth)/forgot-password/page.tsx`
- [ ] T014 [US1] Implement success message and error message display system with styled alert boxes (green for success, red for errors) in `frontend/app/(auth)/forgot-password/page.tsx`
- [ ] T015 [US1] Implement loading state with Loader2 spinner icon and disabled button during API submission in `frontend/app/(auth)/forgot-password/page.tsx`

**Checkpoint**: At this point, User Story 1 should be fully functional - users can request password reset emails

---

## Phase 4: User Story 2 - Password Reset Completion (Priority: P2)

**Goal**: Users can click reset link from email and set a new password on a secure page

**Independent Test**: Click a valid reset link, enter and confirm a new password, submit, and successfully log in with new credentials

**Estimated Time**: ~3 hours

### URL Handling and Token Validation for User Story 2

- [ ] T016 [US2] Create reset password page component shell with basic layout, heading, description, and "Back to Login" link in `frontend/app/(auth)/reset-password/page.tsx`
- [ ] T017 [US2] Extract token from URL query params using useSearchParams hook in useEffect in `frontend/app/(auth)/reset-password/page.tsx`
- [ ] T018 [US2] Implement client-side token format validation using regex and display error with link to request new reset in `frontend/app/(auth)/reset-password/page.tsx`
- [ ] T019 [US2] Add missing token error handling with error message display and auto-redirect to `/forgot-password` after 3 seconds in `frontend/app/(auth)/reset-password/page.tsx`

### Password Input and Validation for User Story 2

- [ ] T020 [US2] Implement form state management with useState hooks (token, tokenError, newPassword, confirmPassword, showPassword, showConfirmPassword, isLoading, error, passwordValidation, passwordsMatch) in `frontend/app/(auth)/reset-password/page.tsx`
- [ ] T021 [US2] Add new password input field with Lock icon, password masking, and Eye/EyeOff toggle button in `frontend/app/(auth)/reset-password/page.tsx`
- [ ] T022 [US2] Add confirm password input field with Lock icon, password masking, and Eye/EyeOff toggle button in `frontend/app/(auth)/reset-password/page.tsx`
- [ ] T023 [US2] Implement real-time password validation on input change using validatePassword utility with dynamic error list display in `frontend/app/(auth)/reset-password/page.tsx`
- [ ] T024 [US2] Implement password match validation on confirm password input change with mismatch error display in `frontend/app/(auth)/reset-password/page.tsx`

### API Integration and Completion for User Story 2

- [ ] T025 [US2] Implement authClient.resetPassword API integration with token and newPassword parameters in `frontend/app/(auth)/reset-password/page.tsx`
- [ ] T026 [US2] Handle successful reset: check for existing session using getSession, sign out if logged in, and redirect to `/login?reset=success` in `frontend/app/(auth)/reset-password/page.tsx`
- [ ] T027 [US2] Implement comprehensive API error handling for expired token, invalid token, and password validation errors with user-friendly messages in `frontend/app/(auth)/reset-password/page.tsx`
- [ ] T028 [US2] Implement loading state with Loader2 spinner and conditionally disabled submit button based on validation state (passwordValidation.isValid, passwordsMatch) in `frontend/app/(auth)/reset-password/page.tsx`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - complete password reset flow functional

---

## Phase 5: User Story 3 - User Guidance and Error Handling (Priority: P3)

**Goal**: Users receive clear guidance, helpful error messages, and seamless navigation throughout password reset

**Independent Test**: Trigger various error conditions and verify users receive helpful messages with clear next steps

**Estimated Time**: ~1 hour

### Login Page Enhancements for User Story 3

- [ ] T029 [US3] Add "Forgot Password?" link below password input, import useSearchParams, and add successMessage state in `frontend/app/(auth)/login/page.tsx`
- [ ] T030 [US3] Implement useEffect to check for `?reset=success` query param and display success message banner with green styling in `frontend/app/(auth)/login/page.tsx`

### Accessibility and Polish for User Story 3

- [ ] T031 [US3] Add comprehensive accessibility attributes (aria-labels to password toggles, role="alert" to errors, aria-busy to buttons) across both password reset pages
- [ ] T032 [US3] Verify mobile responsive design and test form layouts on various viewport sizes (320px, 768px, 1024px)

**Checkpoint**: All user stories should now be independently functional with excellent UX

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

**Estimated Time**: ~1 hour

- [ ] T033 [P] Validate error handling, loading states, and rate limiting behavior across both pages with various network conditions
- [ ] T034 [P] Validate security features (email enumeration prevention, auto-redirect, token validation) and UX edge cases (malformed tokens, expired links)
- [ ] T035 [P] Run complete manual testing checklist from `specs/011-reset-password-frontend/quickstart.md`
- [ ] T036 [P] Verify integration with existing better-auth server from spec 004 and test end-to-end reset flow with actual email delivery

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 can proceed after Phase 2
  - User Story 2 can proceed after Phase 2 (independent of US1)
  - User Story 3 depends on US1 and US2 being complete
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 (but delivers value after US1)
- **User Story 3 (P3)**: Depends on US1 and US2 being complete (enhances both pages)

### Within Each User Story

**User Story 1 Flow**:
1. T008 (shell) → FIRST
2. T009, T010 (input + state) → Can run together after T008
3. T011, T012, T013 (validation + API) → Sequential after state setup
4. T014, T015 (messages + loading) → Can run together after API

**User Story 2 Flow**:
1. T016 (shell) → FIRST
2. T017, T018, T019 (token handling) → Sequential after shell
3. T020 (state) → After token handling
4. T021, T022 (password inputs) → Can run together after state
5. T023, T024 (validation) → Can run together after inputs
6. T025, T026, T027, T028 (API integration) → Sequential after validation

**User Story 3 Flow**:
1. T029, T030 (login page) → Sequential (T030 depends on T029)
2. T031, T032 (accessibility) → Can run in parallel

### Parallel Opportunities

**Phase 1**: All 5 tasks (T001-T005) can run in parallel - different utility functions

**Phase 2**: T006 and T007 can run in parallel

**US1**:
- T009 + T010 can run together
- T014 + T015 can run together

**US2**:
- T021 + T022 can run together (similar input fields)
- T023 + T024 can run together (different validation concerns)

**US3**:
- T031 + T032 can run together

**Phase 6**: All 4 tasks (T033-T036) can run in parallel - different validation areas

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (~1.5 hours)
2. Complete Phase 2: Foundational (~30 min)
3. Complete Phase 3: User Story 1 (~2 hours)
4. **STOP and VALIDATE**: Test forgot password flow independently
5. Deploy/demo if ready

**Delivery**: Users can request password reset emails
**Total MVP Time**: ~4 hours

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (~2 hours)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! ~2 hours)
3. Add User Story 2 → Test independently → Deploy/Demo (~3 hours)
4. Add User Story 3 → Test independently → Deploy/Demo (~1 hour)
5. Polish phase → Final validation (~1 hour)

**Total Estimated Time**: ~9 hours for complete feature

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (~2 hours)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T008-T015)
   - **Developer B**: User Story 2 (T016-T028)
3. **Developer C** (or A/B after completion): User Story 3 (T029-T032)
4. **Team**: Polish phase together (T033-T036)

---

## Task Sizing Verification

All tasks are sized for **15-30 minutes** of focused work:

### ✅ Properly Sized Examples

- **T001**: Create directory + email helper (20 min) - simple utility
- **T003**: Password validation with 5 rules (25 min) - moderate complexity
- **T010**: Form state with 5 useState hooks (20 min) - straightforward React
- **T013**: API integration with 3 callbacks (30 min) - requires careful error handling
- **T023**: Real-time validation with dynamic display (25 min) - validation + UI update
- **T026**: Success handler with session check + signout (30 min) - multiple API calls
- **T031**: Accessibility attributes across pages (25 min) - systematic updates

### ❌ Avoided Pitfalls

- **NOT**: "Implement entire forgot password page" (hours)
- **NOT**: "Add semicolon to line 42" (seconds)
- **NOT**: "Build complete password reset system" (days)

### 🎯 Task Consolidation Applied

- Combined micro-tasks (<10 min): Directory creation + email helper
- Combined repetitive tasks: Error handlers, message displays, navigation links
- Split mega-tasks: Page implementation → 7-13 focused tasks per page
- Added missing tasks: TypeScript interfaces, token validator
- Removed duplicate tasks: "Back to Login" link consolidated

---

## Revised Summary

**Total Tasks**: 36 (down from 58)
**Phases**: 6
**User Stories**: 3
**Estimated Time**: ~9 hours
**MVP Time**: ~4 hours (Phases 1-3)
**Parallel Opportunities**: 17 tasks can run in parallel

**Task Distribution**:
- Phase 1 (Setup): 5 tasks (~1.5 hours)
- Phase 2 (Foundational): 2 tasks (~30 min)
- Phase 3 (US1): 8 tasks (~2 hours)
- Phase 4 (US2): 13 tasks (~3 hours)
- Phase 5 (US3): 4 tasks (~1 hour)
- Phase 6 (Polish): 4 tasks (~1 hour)

---

## Notes

- [P] tasks = different files or independent concerns, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are exact and match the project structure from plan.md
- No tests included (not requested in spec.md)
- Tasks consolidated based on sizing analysis to eliminate micro-tasks
- Added TypeScript type definition tasks (T002, T007) from data-model.md
- Added token validator task (T005) from research.md
