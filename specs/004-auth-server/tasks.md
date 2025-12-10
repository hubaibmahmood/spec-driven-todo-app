# Tasks: Better Auth Server for FastAPI Integration

**Feature**: 004-auth-server
**Input**: Design documents from `/specs/004-auth-server/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Context**: FastAPI backend already exists (Feature 003 complete through Phase 10). This feature adds Node.js auth server with better-auth library.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Google OAuth integration is Phase 9 (can be skipped for MVP).

**Task Sizing**: Each task is scoped for 15-30 minutes of focused work.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Auth Server Infrastructure)

**Purpose**: Initialize Node.js auth server project structure

- [ ] T001 Create auth-server directory and initialize Node.js project with package.json (type: module, name: auth-server, version: 1.0.0)
- [ ] T002 Install auth server dependencies: better-auth@^1.0.0, express@^4.18.0, cors@^2.8.5, dotenv@^16.3.0, @prisma/client@^5.7.0, resend@^2.0.0
- [ ] T003 [P] Install dev dependencies: typescript@^5.3.0, tsx@^4.7.0, @types/node@^20.10.0, @types/express@^4.17.0, @types/cors@^2.8.0, prisma@^5.7.0
- [ ] T004 [P] Create tsconfig.json with ESM config (module: ESNext, target: ES2022, esModuleInterop: true, moduleResolution: node)
- [ ] T005 Initialize Prisma in auth-server/prisma/ with datasource postgresql
- [ ] T006 Create auth-server/.env.example with DATABASE_URL, NODE_ENV, PORT, JWT_SECRET, CORS_ORIGINS, RESEND_API_KEY, EMAIL_FROM, FRONTEND_URL
- [ ] T007 Create auth-server/src directory structure: auth/, config/, database/, middleware/, utils/
- [ ] T008 Create .gitignore excluding node_modules, dist, .env, *.log, .DS_Store, prisma/*.db

---

## Phase 2: Foundational (Database Schema & Core Auth Config)

**Purpose**: Core database schema and authentication configuration that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema (Prisma)

**Note**: Must be compatible with existing FastAPI backend's UserSession model

- [ ] T009 Initialize Prisma schema in auth-server/prisma/schema.prisma with datasource and generator
- [ ] T010 Define User model in Prisma schema (id String @id @default(cuid()), email String @unique, emailVerified Boolean @default(false), password String?, name String?, image String?, createdAt DateTime @default(now()), updatedAt DateTime @updatedAt)
- [ ] T011 [P] Add Session model compatible with FastAPI UserSession (id String @id @default(cuid()), userId String, token String @unique, expiresAt DateTime, ipAddress String?, userAgent String?, createdAt DateTime @default(now()), updatedAt DateTime @updatedAt) with table name "user_sessions"
- [ ] T012 [P] Add VerificationToken model (id String @id @default(cuid()), identifier String, token String @unique, type String, expiresAt DateTime, createdAt DateTime @default(now()))
- [ ] T013 Add indexes and relations to User and Session models (@map for snake_case columns, @@index on userId/token/expiresAt, CASCADE delete)
- [ ] T014 Push Prisma schema to Neon PostgreSQL using npx prisma db push (tables: users, user_sessions, verification_tokens)
- [ ] T015 Generate Prisma client using npx prisma generate
- [ ] T016 Verify schema compatibility with FastAPI backend (check user_sessions table matches backend/src/models/database.py UserSession model)

### Auth Server Core Configuration

- [ ] T017 [P] Create environment validation in auth-server/src/config/env.ts with required/optional field validation
- [ ] T018 [P] Create Prisma client singleton in auth-server/src/database/client.ts with proper connection pooling
- [ ] T019 Create better-auth base config in auth-server/src/auth/auth.config.ts with Prisma adapter and database connection
- [ ] T020 Configure session settings in auth-server/src/auth/auth.config.ts (expiresIn: 7 days, updateAge: 24 hours, cookieCache enabled with 5-minute maxAge)
- [ ] T021 [P] Create Express app in auth-server/src/app.ts with CORS, JSON parser, and trust proxy middleware
- [ ] T022 [P] Create server entry point in auth-server/src/index.ts with environment loading and server startup
- [ ] T023 Add health check endpoint GET /health in auth-server/src/app.ts returning {status, timestamp, database}
- [ ] T024 Start auth server locally and verify health endpoint responds with database: "connected"

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1) 🎯 MVP

**Goal**: Users can register with email/password, verify email, sign in, and sign out

**Independent Test**: Register new user, verify email, sign in, receive valid session token

### US1: Email/Password Authentication

- [ ] T025 [US1] Configure emailAndPassword plugin in auth-server/src/auth/auth.config.ts with requireEmailVerification: true and minPasswordLength: 8
- [ ] T026 [US1] Configure Resend email service for verification emails (15-minute expiration, custom email template)
- [ ] T027 [US1] Add sendVerificationEmail handler to auth config with Resend API integration
- [ ] T028 [US1] Integrate better-auth routes using toNodeHandler in auth-server/src/app.ts at /api/auth/*
- [ ] T029 [US1] Test signup: POST /api/auth/signup with {email, password, name} returns 201 with user and session
- [ ] T030 [US1] Test email verification: POST /api/auth/verify-email with {token} returns 200 and updates emailVerified
- [ ] T031 [US1] Test signin: POST /api/auth/signin with {email, password} returns 200 with session token
- [ ] T032 [US1] Test signout: POST /api/auth/signout invalidates session and clears cookie

**Checkpoint**: User Story 1 complete - users can register, verify email, sign in, and sign out

---

## Phase 4: FastAPI Integration (No Backend Setup - Only Integration)

**Goal**: Connect existing FastAPI backend with new auth server for session validation

**Note**: FastAPI backend already exists. Only add integration points.

### Integration Tasks

- [ ] T033 [US2] Review existing FastAPI auth dependency in backend/src/api/dependencies.py (get_current_user function)
- [ ] T034 [US2] Update backend/.env.example to document AUTH_SERVER_URL variable for reference
- [ ] T035 [US2] Create integration test in backend/tests/integration/test_better_auth_integration.py (test signup on auth server → signin → extract token → call FastAPI /tasks with token → verify 200)
- [ ] T036 [US2] Test auth server session token works with existing FastAPI /tasks endpoints (GET, POST, PUT, DELETE)
- [ ] T037 [US2] Verify user isolation: User A cannot access User B's tasks using their own valid token (403)
- [ ] T038 [US2] Test token expiration: Expired token from auth server returns 401 on FastAPI endpoints
- [ ] T039 [US2] Document token flow in specs/004-auth-server/contracts/fastapi-integration.md (signup → signin → extract session.token → Authorization: Bearer header → FastAPI validates)

**Checkpoint**: FastAPI integration complete - auth server tokens work with existing backend

---

## Phase 5: User Story 3 - Password Reset and Account Recovery (Priority: P3)

**Goal**: Users can securely reset forgotten passwords through email verification

**Independent Test**: Request password reset, receive email with token, submit new password, sign in with new credentials

### US3: Password Reset Flow

- [ ] T040 [US3] Configure password reset in better-auth config (1-hour token expiration, reset email template)
- [ ] T041 [US3] Add sendResetPasswordEmail handler with Resend integration in auth-server/src/auth/auth.config.ts
- [ ] T042 [US3] Test forgot-password: POST /api/auth/forgot-password with {email} returns 200 (always, prevents email enumeration)
- [ ] T043 [US3] Verify password reset email sent with valid 1-hour token
- [ ] T044 [US3] Test reset-password: POST /api/auth/reset-password with {token, password} returns 200 and updates password
- [ ] T045 [US3] Test password reset token expiration: Expired token returns 400 with TOKEN_EXPIRED error
- [ ] T046 [US3] Test signin with new password succeeds after password reset

**Checkpoint**: Password recovery complete - users can reset forgotten passwords

---

## Phase 6: Session Management (Custom Routes)

**Goal**: Users can view active sessions with device info and revoke individual sessions

**Independent Test**: Sign in from multiple devices, view all sessions, revoke one session, verify it's invalidated

### Custom Auth Routes

- [ ] T047 Create custom routes file in auth-server/src/auth/routes.ts for additional endpoints
- [ ] T048 Implement GET /api/auth/me endpoint returning current user profile (id, email, name, image, emailVerified)
- [ ] T049 Implement GET /api/auth/sessions endpoint listing all user sessions with device info (id, token excerpt, expiresAt, ipAddress, userAgent, isCurrent flag)
- [ ] T050 Implement DELETE /api/auth/sessions/:sessionId endpoint to revoke specific session with validation
- [ ] T051 Add validation: Prevent revoking current session (return 400 with error message)
- [ ] T052 Integrate custom routes in auth-server/src/app.ts BEFORE better-auth catch-all handler
- [ ] T053 Test session listing: GET /api/auth/sessions returns all active sessions with device information
- [ ] T054 Test session revocation: DELETE /api/auth/sessions/:id deletes session from database
- [ ] T055 Verify revoked session token returns 401 on both auth server and FastAPI endpoints

**Checkpoint**: Session management complete - users can view and manage sessions

---

## Phase 7: Deployment Configuration

**Purpose**: Prepare auth server for production deployment

### Vercel Configuration (Auth Server)

- [ ] T056 Create auth-server/vercel.json with single catch-all rewrite to /api/index.js
- [ ] T057 [P] Create Vercel serverless entry point in auth-server/api/index.ts exporting Express app
- [ ] T058 [P] Add vercel-build script to package.json: "prisma generate && tsc"
- [ ] T059 [P] Add build and start scripts: "build": "tsc", "start": "node dist/index.js"

### Environment & Documentation

- [ ] T060 [P] Document deployment process in specs/004-auth-server/quickstart.md (Vercel auth server, existing Render FastAPI backend)
- [ ] T061 [P] Add CORS configuration documentation for production domains in quickstart.md
- [ ] T062 [P] Create deployment checklist in specs/004-auth-server/DEPLOYMENT.md (environment variables, database migration, DNS setup)

**Checkpoint**: Deployment configuration complete - ready for production deployment

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation across all user stories (excluding OAuth)

- [ ] T063 [P] Create error handler middleware in auth-server/src/middleware/errorHandler.ts with standardized error responses
- [ ] T064 [P] Create request logger middleware in auth-server/src/middleware/logger.ts with correlation IDs
- [ ] T065 [P] Implement structured logging utility in auth-server/src/utils/logger.ts using console or Winston
- [ ] T066 Add security headers middleware using helmet in auth-server/src/app.ts
- [ ] T067 [P] Test security headers: Verify helmet adds CSP, HSTS, X-Frame-Options headers
- [ ] T068 Run end-to-end validation: Signup → verify email → signin → call FastAPI /tasks → create task → signout
- [ ] T069 Test password reset flow end-to-end: Request reset → receive email → reset password → signin
- [ ] T070 Test session management flow: Signin from 2 devices → list sessions → revoke one → verify invalidation
- [ ] T071 [P] Add OpenAPI documentation generation for custom routes in auth-server/src/auth/routes.ts
- [ ] T072 Validate all environment variables are documented in .env.example with clear descriptions

**Checkpoint**: Core feature complete and production-ready (without OAuth)

---

## Phase 9: Google OAuth Integration (Optional - Can Skip for MVP)

**Goal**: Users can sign in with Google OAuth2 for streamlined authentication

**Independent Test**: Initiate Google OAuth, complete flow, receive valid session token

**Note**: This phase can be skipped initially. Implement when social login is required.

### OAuth Prerequisites

- [ ] T073 Add OAuth environment variables to auth-server/.env.example (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI)
- [ ] T074 Add Account model for OAuth in Prisma schema (id String @id @default(cuid()), userId String, type String, provider String, providerAccountId String, refreshToken String?, accessToken String?, expiresAt Int?, tokenType String?, scope String?, idToken String?, sessionState String?, createdAt DateTime, updatedAt DateTime)
- [ ] T075 Add indexes and unique constraints to Account model (@@unique([provider, providerAccountId]), @@index([userId]))
- [ ] T076 Push updated schema to database with Account table using npx prisma db push
- [ ] T077 Regenerate Prisma client with Account model using npx prisma generate

### OAuth Configuration

- [ ] T078 Configure Google OAuth provider in auth-server/src/auth/auth.config.ts (clientId, clientSecret, redirectURI from env)
- [ ] T079 Enable account linking for trusted providers (Google) in socialProviders config
- [ ] T080 Add OAuth callback configuration with proper redirect handling

### OAuth Testing

- [ ] T081 Test OAuth initiation: GET /api/auth/oauth/google redirects to Google consent screen
- [ ] T082 Test OAuth callback: Handles code/state params, creates user account, returns session
- [ ] T083 Test account linking: Google email matches existing user → links accounts instead of creating duplicate
- [ ] T084 Verify OAuth user can access FastAPI /tasks endpoints with OAuth-generated token
- [ ] T085 Test OAuth flow end-to-end: OAuth signin → receive session → call FastAPI /tasks endpoint
- [ ] T086 Update deployment documentation in DEPLOYMENT.md with OAuth credentials setup

**Checkpoint**: OAuth integration complete - users can sign in with Google (optional feature)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 5-6)**: All depend on Foundational phase completion
  - Can proceed in parallel if multiple developers
  - Or sequentially in priority order: US1 (P1) → US2 (P2) → US3 (P3)
- **FastAPI Integration (Phase 4)**: Depends on User Story 1 (auth server producing session tokens)
- **Session Management (Phase 6)**: Depends on User Story 1 (session creation)
- **Deployment (Phase 7)**: Depends on core functionality (US1, US2) being complete
- **Polish (Phase 8)**: Depends on all core user stories being complete
- **OAuth (Phase 9)**: OPTIONAL - Can be skipped entirely or implemented last

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **FastAPI Integration (P2)**: Depends on User Story 1 - Requires working auth server
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent but builds on US1 auth infrastructure
- **OAuth (Optional)**: Depends on Foundational (Phase 2) - Completely independent feature

### Within Each User Story

- Environment setup before code implementation
- Configuration before endpoints
- Core implementation before integration tests
- Story validation before moving to next priority

### Parallel Opportunities

- **Phase 1 Setup**: T003 (dev deps) and T004 (tsconfig) can run in parallel with T002
- **Phase 2 Foundational**:
  - T011, T012 (Prisma models) can run in parallel after T010
  - T017, T018 (config files) can run in parallel
  - T021, T022 (Express setup) can run in parallel after T020
- **Phase 4 Integration**: T035-T038 (integration tests) can run in parallel after T033-T034
- **Phase 7 Deployment**: T057, T058, T059 can run in parallel with T056
- **Phase 8 Polish**: T063, T064, T065, T067, T071 can run in parallel
- **Phase 9 OAuth**: T074-T077 (schema updates) can run in parallel, T081-T085 (tests) can run in parallel

---

## Parallel Example: User Story 1

```bash
# After T028 (better-auth routes integrated), launch these tests in parallel:
Task: "Test signup endpoint" (T029)
Task: "Test email verification" (T030)
Task: "Test signin endpoint" (T031)
Task: "Test signout endpoint" (T032)
```

---

## Implementation Strategy

### MVP First (Core Auth without OAuth)

**Phases 1-8 Only (Skip Phase 9 OAuth)**

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T024) - CRITICAL
3. Complete Phase 3: User Story 1 (T025-T032) - Auth server works
4. Complete Phase 4: FastAPI Integration (T033-T039) - End-to-end auth works
5. Complete Phase 5: Password Reset (T040-T046) - Account recovery
6. Complete Phase 6: Session Management (T047-T055) - Multi-device support
7. Complete Phase 7: Deployment (T056-T062) - Production ready
8. Complete Phase 8: Polish (T063-T072) - Production hardening
9. **STOP and VALIDATE**: Full production-ready auth without OAuth
10. Deploy/demo - Complete authentication system!

**Total MVP Time**: ~20-22 hours (72 tasks, no OAuth)

### Full Feature (Including OAuth)

Add Phase 9 after MVP complete:

1. Complete MVP (Phases 1-8) above
2. **Optional**: Complete Phase 9: Google OAuth (T073-T086) - Social login
3. **VALIDATE**: Test OAuth integration end-to-end
4. Deploy/demo - Complete with social login!

**Total Full Feature Time**: ~25-28 hours (86 tasks, with OAuth)

### Incremental Delivery

1. **Foundation** (Phases 1-2) → Auth server structure ready (~6 hours)
2. **Core Auth** (Phase 3) → Email/password auth works (~2.5 hours)
3. **Integration** (Phase 4) → Works with FastAPI backend → **Deploy MVP v1** (~2 hours)
4. **Password Reset** (Phase 5) → Account recovery → Deploy v1.1 (~2 hours)
5. **Session Mgmt** (Phase 6) → Multi-device support → Deploy v1.2 (~3 hours)
6. **Production Ready** (Phases 7-8) → Deployment + Polish → **Deploy v2.0 Production** (~5 hours)
7. **Optional OAuth** (Phase 9) → Social login → Deploy v2.1 (if needed) (~4 hours)

### Parallel Team Strategy

With multiple developers after Foundational phase (T024):

- **Developer A**: User Story 1 (Auth server) - T025-T032
- **Developer B**: FastAPI Integration tests - T033-T039
- **Developer C**: Deployment config preparation - T056-T062

Then converge for testing, polish, and optional OAuth.

---

## Task Size Validation

All tasks are scoped for 15-30 minutes:

- **Setup tasks** (T001-T008): 10-20 minutes each
- **Schema tasks** (T009-T016): 15-25 minutes each
- **Configuration tasks** (T017-T024): 15-20 minutes each
- **Implementation tasks** (T025-T055): 20-30 minutes each
- **Testing tasks** (T029-T032, T035-T038, T042-T046): 15-20 minutes each
- **Deployment tasks** (T056-T062): 15-20 minutes each
- **Polish tasks** (T063-T072): 15-25 minutes each
- **OAuth tasks** (T073-T086): 15-25 minutes each

Total estimated time:
- **MVP without OAuth (Phases 1-8)**: ~20-22 hours (72 tasks)
- **Full Feature with OAuth (All phases)**: ~25-28 hours (86 tasks)

---

## What's Different from Feature 003?

**Feature 003** (FastAPI REST API - COMPLETE):
- ✅ FastAPI backend setup
- ✅ Database connection to Neon PostgreSQL
- ✅ Task CRUD endpoints
- ✅ Session authentication (Phase 10 complete)
- ✅ UserSession model (compatible with better-auth)

**Feature 004** (Auth Server - THIS FEATURE):
- 🆕 Node.js auth server with better-auth
- 🆕 Email/password registration and verification
- 🆕 Password reset flow
- 🆕 Session management (view/revoke sessions)
- 🔗 Integration with existing FastAPI backend (no duplicate setup)
- 🔷 Google OAuth (Phase 9 - Optional/Can skip)

**Key Changes from Original Plan**:
1. **REMOVED**: All FastAPI backend setup tasks - backend already exists
2. **REMOVED**: SQLAlchemy model creation - UserSession model already exists in backend
3. **REMOVED**: Database connection setup for FastAPI - already configured
4. **REMOVED**: get_current_user dependency creation - already implemented in Phase 10 of Feature 003
5. **ADDED**: Schema compatibility validation (T016) to ensure Prisma schema matches existing FastAPI UserSession
6. **ADDED**: Integration testing (T033-T039) to verify auth server works with existing FastAPI endpoints
7. **REORGANIZED**: Moved all Google OAuth tasks to Phase 9 (last phase, optional)
8. **FOCUSED**: Pure auth server implementation with integration points, not duplicate backend setup

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently testable
- **CRITICAL**: FastAPI backend already exists - do NOT recreate it
- **CRITICAL**: UserSession model already exists in backend/src/models/database.py - Prisma schema must match
- **CRITICAL**: Session authentication already implemented in backend - only integration needed
- **IMPORTANT**: Phase 9 (OAuth) is OPTIONAL and can be skipped for MVP
- Use better-auth documentation for auth-server tasks
- Commit after each task or logical group (every 2-3 tasks)
- Stop at any checkpoint to validate story independently
- Environment variables must be set before running tests
- Prisma schema must match existing SQLAlchemy UserSession model exactly
- Deploy MVP without OAuth first (Phases 1-8), add OAuth later if needed
