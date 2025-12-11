# Implementation Plan: Next.js Dashboard Migration

**Branch**: `005-nextjs-dashboard-migration` | **Date**: 2025-12-12 | **Spec**: [Feature Spec](./spec.md)
**Input**: Feature specification from `/specs/005-nextjs-dashboard-migration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Migrate the existing React/Vite dashboard to **Next.js 16 (App Router)**. The new frontend will reside in a `frontend` directory, integrating with the existing `auth-server` (better-auth) and `backend` (FastAPI) microservices. Key goals include pixel-perfect UI replication using Tailwind CSS, robust server-side data fetching, and secure session management via HttpOnly cookies.

## Technical Context

**Language/Version**: TypeScript 5.0+
**Primary Dependencies**: Next.js 16.0.8, React 19, Tailwind CSS 3.4, Lucide React, Recharts, Better-Auth (Client)
**Storage**: N/A (Stateless Frontend)
**Testing**: Jest, React Testing Library
**Target Platform**: Web (Modern Browsers)
**Project Type**: Web application (Frontend)
**Performance Goals**: LCP < 2.5s, INP < 200ms
**Constraints**: Pixel-perfect replication of existing design.
**Scale/Scope**: ~5 main views (Login, Register, Dashboard, Mobile Menu).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Test-First Development**: Will write tests for components/utilities before implementation.
- [x] **Clean Code & Simplicity**: strict ESLint rules, small functional components.
- [x] **Proper Project Structure**: Standard Next.js App Router structure.
- [x] **In-Memory Data Storage**: Frontend state via URL Params and React State.
- [x] **Command-Line Interface Excellence**: N/A (Web UI).
- [x] **UV Package Manager Integration**: N/A (Node.js project uses `npm`).

## Project Structure

### Documentation (this feature)

```text
specs/005-nextjs-dashboard-migration/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api-client.md    # API Interface definition
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── layout.tsx
│   └── globals.css
├── components/
│   ├── ui/
│   ├── dashboard/
│   └── todo/
├── lib/
│   ├── api.ts
│   └── utils.ts
├── types/
│   └── index.ts
└── __tests__/
    ├── components/
    └── lib/
```

**Structure Decision**: Selected "Option 2: Web application" pattern, creating a dedicated `frontend` directory to sit alongside existing `backend` and `auth-server` services.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | | |