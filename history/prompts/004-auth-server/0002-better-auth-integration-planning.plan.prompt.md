---
id: 0002
title: better-auth integration planning
stage: plan
date: 2025-12-10
surface: agent
model: claude-sonnet-4-5
feature: 004-auth-server
branch: 004-auth-server
user: developer
command: /sp.plan
labels: ["planning", "architecture", "better-auth", "fastapi", "authentication", "microservices"]
links:
  spec: specs/004-auth-server/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-auth-server/plan.md
  - specs/004-auth-server/research.md
  - specs/004-auth-server/data-model.md
  - specs/004-auth-server/contracts/auth-api.openapi.yaml
  - specs/004-auth-server/contracts/fastapi-integration.md
  - specs/004-auth-server/quickstart.md
  - CLAUDE.md (updated with Node.js + Neon PostgreSQL technologies)
tests:
  - Integration tests planned for auth flows
  - Database schema validation planned
---

## Prompt

Execute the implementation planning workflow for feature 004-auth-server using the better-auth-fastapi-agent and better-auth-setup skill as suggested. The feature requires implementing a Node.js authentication server using better-auth library that integrates with FastAPI backend through a shared PostgreSQL database.

User input: "is running… use the better-auth-fastapi-agent and better-auth-setup if they can be helpful in this phase"

## Response snapshot

Successfully completed comprehensive implementation planning for better-auth + FastAPI integration:

**Phase 0 (Research) - Completed:**
- Researched better-auth integration patterns with FastAPI microservices architecture
- Resolved 7 critical research questions:
  1. Integration architecture (separate Node.js auth server + FastAPI backend)
  2. Session validation strategy (database lookup for real-time revocation)
  3. Schema coordination between Prisma and Alembic
  4. ESM module system requirements
  5. CORS configuration for cross-origin authentication
  6. Email service selection (Resend)
  7. Vercel deployment patterns
- Generated comprehensive research.md with decisions, rationales, and alternatives

**Phase 1 (Design & Contracts) - Completed:**
- Defined complete data model with 4 entities (User, Session, Account, VerificationToken)
- Created detailed Prisma and SQLAlchemy schemas with critical type mappings
- Generated OpenAPI 3.1 specification for auth endpoints (15+ endpoints)
- Documented FastAPI integration contract with:
  - Token flow diagrams
  - Authentication dependency patterns
  - Database schema sync guarantees
  - Error handling standards
  - Performance budgets
  - Security requirements
- Created comprehensive quickstart guide with step-by-step setup (6 major steps)

**Technical Context Filled:**
- Auth Server: Node.js 20+, TypeScript 5.x, better-auth, Express, Prisma
- FastAPI Backend: Python 3.12+, FastAPI, SQLAlchemy 2.0, Alembic
- Shared Infrastructure: Neon Serverless PostgreSQL with connection pooling

**Constitution Check - Completed:**
- Evaluated all 6 constitution principles
- Documented 4 justified violations:
  1. Microservices architecture (requires Node.js for better-auth)
  2. Persistent storage (authentication requires database)
  3. TDD suspension (infrastructure setup follows library patterns)
  4. Shared database (simpler than separate databases with sync)
- All violations justified with clear rationales and mitigation strategies

**Artifacts Generated:**
1. plan.md - Complete implementation plan with technical context
2. research.md - 7 research questions resolved with decisions
3. data-model.md - Entity definitions, schemas, validation rules
4. contracts/auth-api.openapi.yaml - OpenAPI spec for auth endpoints
5. contracts/fastapi-integration.md - FastAPI integration contract
6. quickstart.md - Step-by-step setup guide (6 steps, 30-45 min)

**Agent Context Updated:**
- Added Node.js 20+ with TypeScript 5.x to technology stack
- Added Neon Serverless PostgreSQL to database technologies

## Outcome

- ✅ Impact: Complete architectural plan for better-auth + FastAPI integration ready for implementation. All research questions resolved, data model defined, API contracts documented, and setup guide created.
- 🧪 Tests: Integration tests planned for auth flows, database schema validation, and protected endpoint access. Test fixtures documented for valid/expired sessions.
- 📁 Files: 7 files created/modified (plan.md, research.md, data-model.md, 2 contract files, quickstart.md, CLAUDE.md)
- 🔁 Next prompts: Run `/sp.tasks` to generate actionable task breakdown for implementation phase. Use better-auth-fastapi-agent for code generation when implementing.
- 🧠 Reflection: Successfully leveraged better-auth-fastapi-agent knowledge to create comprehensive planning artifacts. Research phase resolved all unknowns. Design phase produced complete data model and API contracts. Ready for implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Planning workflow executed successfully with all phases completed.
- Graders run and results (PASS/FAIL): Constitution Check PASS (all violations justified), Schema sync validation PLANNED, Integration tests PLANNED
- Prompt variant (if applicable): Used better-auth-fastapi-agent knowledge and security-best-practices skill as suggested
- Next experiment (smallest change to try): Generate tasks.md with `/sp.tasks` command to create implementation task breakdown
