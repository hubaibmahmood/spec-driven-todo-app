# Implementation Plan: Reset Password Frontend Integration

**Branch**: `011-reset-password-frontend` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-reset-password-frontend/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement password reset frontend integration for the Next.js todo application, providing users with a complete self-service password recovery flow. This includes a forgot password page for requesting reset emails and a reset password page for completing the password change using tokens. The implementation leverages the existing better-auth server (spec 004) and better-auth React client (v1.4.6), adding two new public routes (`/forgot-password` and `/reset-password`) with email validation, token handling, password strength validation, loading states, and comprehensive error handling.

## Technical Context

**Language/Version**: TypeScript 5.x with React 19.2.1 and Next.js 16.0.9
**Primary Dependencies**: better-auth v1.4.6 (React client), lucide-react v0.560.0 (icons), date-fns v4.1.0 (date formatting)
**Storage**: N/A (frontend only; backend uses Neon PostgreSQL via better-auth server from spec 004)
**Testing**: Jest 30.2.0 with @testing-library/react 16.3.1, @testing-library/user-event 14.6.1, Playwright 1.57.0 (E2E)
**Target Platform**: Web browsers (modern browsers supporting ES2020+), responsive design for mobile and desktop
**Project Type**: Web (Next.js frontend with App Router)
**Performance Goals**: Page load <2 seconds, API responses <200ms p95, form validation <100ms (real-time)
**Constraints**: Public routes (unauthenticated access required), client-side token validation, no email enumeration, rate limiting (2 requests per 5 minutes)
**Scale/Scope**: 2 new pages (forgot-password, reset-password), 2 API client calls (forgetPassword, resetPassword), ~400 lines of TypeScript/TSX code

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Frontend-Specific Constitution Evaluation

The project constitution is primarily focused on Python CLI development with TDD. Since this feature is frontend TypeScript/React development, we evaluate the **spirit** of the constitution principles:

| Constitution Principle | Applicability | This Feature's Approach | Status |
|------------------------|---------------|-------------------------|--------|
| **I. Test-First Development** | Adapted | Component tests with @testing-library/react, E2E tests with Playwright. Tests written for each component before implementation (following existing pattern in `__tests__/` directory) | ✅ PASS |
| **II. Clean Code & Simplicity** | Fully Applicable | TypeScript with strict types, single-purpose components, descriptive naming, no over-engineering. Modern React patterns (hooks, functional components). No deprecated APIs | ✅ PASS |
| **III. Proper Project Structure** | Adapted | Next.js App Router structure: pages in `app/(auth)/`, reusable logic in `lib/`, tests in `__tests__/`. Clear separation: UI components, API client calls, validation logic | ✅ PASS |
| **IV. In-Memory Data Storage** | N/A | Frontend feature; backend storage handled by better-auth server (spec 004) | N/A |
| **V. CLI Excellence** | N/A | Web UI feature, not CLI | N/A |
| **VI. UV Package Manager** | N/A | Uses npm/pnpm (Node.js ecosystem) | N/A |

### Quality Gates

- [ ] **Pre-Implementation**: User stories defined with testable acceptance criteria (✅ Complete in spec.md)
- [ ] **Code Quality**: TypeScript strict mode enabled, ESLint passing, no console errors
- [ ] **Testing**: Component tests for validation logic, E2E tests for full password reset flow
- [ ] **Simplicity**: No unnecessary abstractions; uses existing patterns from login/register pages
- [ ] **No Over-Engineering**: Minimal code to meet requirements; leverages better-auth client SDK

### Constitution Compliance Summary

**GATE STATUS: ✅ PASS**

This feature adheres to the constitution's core values (test-first, clean code, proper structure, simplicity) adapted for frontend development. No complexity justifications needed.

## Project Structure

### Documentation (this feature)

```text
specs/011-reset-password-frontend/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── (auth)/
│   │   ├── layout.tsx                    # Existing auth layout
│   │   ├── login/page.tsx                # Existing - add "Forgot Password?" link
│   │   ├── register/page.tsx             # Existing
│   │   ├── forgot-password/
│   │   │   └── page.tsx                  # NEW - Request password reset
│   │   └── reset-password/
│   │       └── page.tsx                  # NEW - Complete password reset
│   └── api/
│       └── auth/
│           └── [...all]/route.ts         # Existing better-auth proxy
├── lib/
│   ├── auth-client.ts                    # Existing - exports authClient
│   └── validation/
│       └── password.ts                   # NEW - Password validation utilities
└── __tests__/
    ├── app/
    │   └── (auth)/
    │       ├── forgot-password.test.tsx  # NEW - Component tests
    │       └── reset-password.test.tsx   # NEW - Component tests
    └── e2e/
        └── password-reset.spec.ts        # NEW - E2E Playwright tests
```

**Structure Decision**:

This feature follows the existing Next.js App Router architecture with `(auth)` route group for authentication pages. New pages are added alongside existing login/register pages, maintaining consistency with current patterns. Validation utilities are extracted to `lib/validation/` for reusability and testability. Tests follow the existing structure in `__tests__/` with both component-level and E2E coverage.

## Complexity Tracking

**No complexity violations detected.** This feature maintains simplicity by:
- Reusing existing better-auth client SDK (no custom auth logic)
- Following established patterns from login/register pages
- Minimal new code (~400 lines total across 2 pages and validation utilities)
- No new dependencies required
