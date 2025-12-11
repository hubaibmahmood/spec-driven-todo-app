---
id: 0003
title: Generate auth server tasks
stage: tasks
date: 2025-12-11
surface: agent
model: claude-sonnet-4-5
feature: 004-auth-server
branch: 004-auth-server
user: mac
command: /sp.tasks
labels: ["task-generation", "better-auth", "fastapi", "authentication", "microservices"]
links:
  spec: specs/004-auth-server/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-auth-server/tasks.md
tests:
---

## Prompt

use better-auth-fastapi-agent and better-auth-setup skills to implement this. Also, sized right (15-30 minutes, not hours or minutes)

## Response snapshot

**REVISED** after discovering Feature 003 (FastAPI REST API) already implements complete backend with Neon PostgreSQL, Task CRUD endpoints, and session authentication (Phase 10 complete).

Generated focused task breakdown (81 tasks across 9 phases) for implementing Node.js better-auth authentication server that integrates with EXISTING FastAPI backend:

- **Phase 1: Setup** (8 tasks) - Auth server infrastructure initialization
- **Phase 2: Foundational** (17 tasks) - Prisma schema (compatible with existing UserSession model) and core auth config
- **Phase 3: User Story 1** (8 tasks) - Email/password registration and authentication
- **Phase 4: FastAPI Integration** (7 tasks) - Integration with existing backend (NO backend setup)
- **Phase 5: User Story 3** (7 tasks) - Password reset and account recovery
- **Phase 6: OAuth Integration** (7 tasks) - Google OAuth2 sign-in
- **Phase 7: Session Management** (9 tasks) - Multi-device session tracking and revocation
- **Phase 8: Deployment** (7 tasks) - Vercel configuration for auth server
- **Phase 9: Polish** (11 tasks) - Error handling, logging, security, end-to-end validation

Each task sized for 15-30 minutes. MVP scope: Phases 1-4 (40 tasks, ~10-12 hours). Full feature: All 9 phases (~25-30 hours).

Key architectural decisions reflected in tasks:
- Microservices architecture (separate Node.js auth server + Python FastAPI backend)
- Shared Neon PostgreSQL database with Prisma (auth server) and SQLAlchemy (FastAPI)
- Database lookup session validation strategy for real-time revocation
- Better-auth library for Node.js authentication with Prisma adapter
- Resend for email verification and password reset

Tasks follow strict checklist format with IDs, [P] parallelization markers, and [Story] labels for traceability.

## Outcome

- ✅ Impact: **FINAL REVISION** - Complete task breakdown with NO duplication from Feature 003, Google OAuth moved to optional Phase 9
- 🧪 Tests: No test files created (tasks.md is planning artifact)
- 📁 Files: Created specs/004-auth-server/tasks.md with 86 tasks (72 for MVP without OAuth, 14 optional OAuth tasks)
- 🔁 Next prompts: /sp.implement to execute tasks, or start with MVP (Phases 1-8, ~20-22 hours) skipping OAuth (Phase 9)
- 🧠 Reflection: **Three major revisions**: (1) Original 92 tasks, (2) Eliminated 11 duplicate FastAPI setup tasks after discovering Feature 003 completion → 81 tasks, (3) Reorganized Google OAuth to Phase 9 (optional) for flexible MVP delivery → Final 86 tasks (72 MVP + 14 OAuth). Task sizing 15-30 minutes maintained. Clear separation enables deploying production-ready auth without OAuth commitment.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Format validation PASS (all tasks follow [ID] [P?] [Story] format), Size validation PASS (15-30 min scope), Story organization PASS (independent testable increments)
- Prompt variant (if applicable): base
- Next experiment (smallest change to try): Consider adding time estimates per phase for better planning visibility
