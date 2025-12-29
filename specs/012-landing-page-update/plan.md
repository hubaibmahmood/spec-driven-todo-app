# Implementation Plan: Landing Page Update - AI-Powered Task Management

**Branch**: `012-landing-page-update` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-landing-page-update/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Update the existing landing page to prominently showcase AI-powered task management as the core value proposition, with improved messaging, a features section highlighting 4 key capabilities (AI Assistant, Visual Dashboard, Real-Time Updates, Secure & Private), enhanced dashboard preview mockup, and multiple clear CTAs for conversion. The implementation will update the existing Next.js landing page component with server-side rendering (SSR), responsive design (320px-1920px), accessibility compliance (WCAG 2.1 AA), automatic redirection for authenticated users, and progressive image loading with skeleton placeholders.

## Technical Context

**Language/Version**: TypeScript 5.x with React 19.2.1 and Next.js 16.0.9
**Primary Dependencies**: lucide-react 0.560.0 (icons), better-auth 1.4.6 (authentication/session detection), Next.js Link component (routing)
**Storage**: N/A (static content; authentication session managed by better-auth)
**Testing**: Jest 30.2.0 + React Testing Library 16.3.1 (unit/integration), Playwright 1.57.0 (E2E), Lighthouse (accessibility/performance audits)
**Target Platform**: Web browsers (Desktop: Chrome/Firefox/Safari/Edge, Mobile: iOS Safari/Chrome, Tablet), SSR-enabled (Next.js App Router)
**Project Type**: Web application (frontend-only change - updating existing landing page component)
**Performance Goals**: Initial page load <2s on 4G/broadband, Time to Interactive (TTI) <3s, First Contentful Paint (FCP) <1.5s
**Constraints**: SSR required (no JavaScript dependency), Lighthouse accessibility score ≥90, No horizontal scrolling on mobile (≥320px width), Consistent indigo branding
**Scale/Scope**: Single page component update (~500-700 lines), 4 feature cards, 3+ CTA locations, 1 dashboard preview mockup section

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development (NON-NEGOTIABLE)

**Status**: ✅ COMPLIANT

- Landing page update is a frontend component modification
- Tests required: Component rendering, CTA button functionality, responsive layout, accessibility, authenticated user redirection
- Test-first workflow applies: Write tests for hero section, features section, CTAs, and responsive behavior before implementation
- Jest + React Testing Library for component tests, Playwright for E2E user flows, Lighthouse for accessibility/performance

### II. Clean Code & Simplicity

**Status**: ✅ COMPLIANT

- Feature updates existing LandingPage.tsx component (already ~537 lines)
- Changes focus on content updates (copy, feature descriptions, AI messaging) rather than complex logic
- Type safety maintained with TypeScript 5.x
- No premature optimization - progressive image loading is a specific requirement (FR-012)
- Modern Next.js 16.0.9 patterns (App Router, server components where applicable)

### III. Proper Project Structure

**Status**: ✅ COMPLIANT

- Changes contained within frontend/app/ directory structure:
  - `frontend/app/page.tsx` (root landing page wrapper)
  - `frontend/app/LandingPage.tsx` (main component to update)
  - Tests in `frontend/__tests__/landing-page/`
- Clear separation: presentational component (LandingPage.tsx) vs. routing (page.tsx)
- Authentication logic already isolated in middleware.ts and auth-client.ts

### IV. In-Memory Data Storage

**Status**: ✅ COMPLIANT (N/A)

- Landing page is a static/presentational component with no data persistence
- Session detection uses existing better-auth client (no new storage requirements)
- No CRUD operations or data layer needed for this feature

### V. Command-Line Interface Excellence

**Status**: ✅ COMPLIANT (N/A)

- This is a web UI feature, not a CLI feature
- N/A for landing page implementation

### VI. UV Package Manager Integration

**Status**: ✅ COMPLIANT (N/A - Frontend Feature)

- Frontend uses npm/pnpm for dependency management (package.json at frontend/package.json)
- UV is for Python projects; this is a TypeScript/React project
- N/A for this feature

### VII. Modern Python APIs

**Status**: ✅ COMPLIANT (N/A - Frontend Feature)

- No Python code involved in this frontend-only feature
- N/A for this feature

**GATE RESULT**: ✅ **PASSED** - All applicable constitution principles are satisfied. Feature is frontend-only component update with no violations or complexity requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/012-landing-page-update/
├── spec.md              # Feature requirements and user stories
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command - UI component structure)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command - Component API contracts)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── page.tsx                    # Root landing page (wrapper) - UPDATE
│   ├── LandingPage.tsx             # Main landing page component - UPDATE (primary change)
│   ├── layout.tsx                  # Root layout (existing, no changes)
│   └── (auth)/                     # Auth pages (existing, no changes)
│       ├── login/page.tsx
│       └── register/page.tsx
│
├── lib/
│   └── auth-client.ts              # better-auth client (existing, READ for session detection pattern)
│
├── middleware.ts                   # Next.js middleware for auth (existing, READ for redirect logic)
│
├── __tests__/
│   └── landing-page/               # NEW test directory
│       ├── LandingPage.test.tsx    # Component unit tests
│       ├── landing-cta.test.tsx    # CTA functionality tests
│       ├── landing-responsive.test.tsx  # Responsive layout tests
│       └── landing-e2e.spec.ts     # Playwright E2E tests
│
└── package.json                    # Dependencies (existing, no changes expected)
```

**Structure Decision**: Web application (frontend-only). This feature modifies the existing Next.js frontend landing page component. The primary change is updating `frontend/app/LandingPage.tsx` with new content, messaging, and features section. Tests will be added in a new `__tests__/landing-page/` directory. No backend changes, no new dependencies, and no changes to routing or authentication logic (except reading existing patterns for authenticated user redirection).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - This section intentionally left empty. All constitution checks passed without requiring complexity justification.
