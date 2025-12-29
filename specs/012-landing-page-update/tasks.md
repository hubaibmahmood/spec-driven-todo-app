# Tasks: Landing Page Update - AI-Powered Task Management

**Input**: Design documents from `/specs/012-landing-page-update/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are OPTIONAL for this feature (not explicitly requested in spec)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Revision**: Optimized from 30 → 27 tasks (removed redundant research/validation, combined granular tasks, added critical verifications)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/app/`, `frontend/__tests__/`, `frontend/types/`
- Paths reflect Next.js 16.0.9 App Router structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and TypeScript type definitions

**Estimated Time**: ~25 minutes total

- [ ] T001 Create TypeScript type definitions file at frontend/types/landing.ts with Feature, CTAButtonProps, FeaturesSectionProps interfaces per data-model.md (~15 min)
- [ ] T002 [P] Create test directory structure: frontend/__tests__/landing-page/ with placeholder files (LandingPage.test.tsx, landing-cta.test.tsx, landing-responsive.test.tsx) (~10 min)

**Checkpoint**: Type definitions ready, test structure in place

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Estimated Time**: ~15 minutes total

- [ ] T003 Define FEATURES constant array with 4 feature objects (AI Assistant first, then Visual Dashboard, Real-Time Updates, Secure & Private) in frontend/app/LandingPage.tsx with proper TypeScript typing and verify structure matches component-api.md contract (~15 min)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - First-Time Visitor Understanding Value Proposition (Priority: P1) 🎯 MVP

**Goal**: Visitors immediately understand AI-powered task management as the core value proposition within 5 seconds

**Independent Test**: Show landing page to users and ask "What does this app do?" within 10 seconds. Success = 80%+ identify AI assistance as core feature.

**Estimated Time**: ~25 minutes total

### Implementation for User Story 1

- [ ] T004 [US1] Update hero section headline and subheadline in frontend/app/LandingPage.tsx: headline to "Organize your work with AI-powered assistance", subheadline to "Let AI help you manage tasks, prioritize smartly, and reach your goals faster" (~10 min)
- [ ] T005 [US1] Apply gradient styling to "AI-powered assistance" text in headline using text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 classes (~15 min)

**Checkpoint**: At this point, User Story 1 should be fully functional - hero section clearly communicates AI value proposition

---

## Phase 4: User Story 2 - Understanding Key Features and Benefits (Priority: P2)

**Goal**: Visitors understand 4 specific capabilities and their practical benefits

**Independent Test**: Ask visitors to list features after viewing page. Success = visitors name 3-4 features and explain at least one benefit.

**Estimated Time**: ~75 minutes total

### Implementation for User Story 2

- [ ] T006 [US2] Import required icons (MessageSquare, LayoutDashboard, Zap, Shield) from lucide-react and create FeatureCard inline component in frontend/app/LandingPage.tsx with props (feature: Feature) and render structure per component-api.md contract (~20 min)
- [ ] T007 [US2] Verify FeatureCard component renders correctly by temporarily rendering one test feature card with mock data before bulk replacement (~5 min)
- [ ] T008 [US2] Replace existing features section (around line 424-477) with new FeaturesSection component that maps over FEATURES array using FeatureCard (~20 min)
- [ ] T009 [US2] Update grid layout classes from grid-cols-1 md:grid-cols-3 to grid-cols-1 md:grid-cols-2 lg:grid-cols-4 for proper 4-card responsive layout (~8 min)
- [ ] T010 [US2] Add hover animations (group-hover:scale-110 on icon container, hover:shadow-lg on card) and aria-hidden="true" to all feature card icons for accessibility (~12 min)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - visitors see clear value prop AND 4 feature benefits

---

## Phase 5: User Story 3 - Converting to Sign-Up (Priority: P3)

**Goal**: Convinced visitors have clear, accessible paths to sign up from multiple points on the page

**Independent Test**: Track click-through rate on CTA buttons. Success = 90%+ of testers can identify at least 2 CTA locations.

**Estimated Time**: ~85 minutes total

### Implementation for User Story 3

- [ ] T011 [P] [US3] Add authenticated user redirect logic to LandingPage component: import useSession and useRouter, add useEffect hook that redirects to /dashboard if session exists per research.md implementation pattern (~15 min)
- [ ] T012 [P] [US3] Create CTAButton inline component (or extract to frontend/components/CTAButton.tsx) with TypeScript props interface (href, variant, location, children) and implement primary/secondary variant styling per component-api.md contract (~25 min)
- [ ] T013 [US3] Implement handleCTAClick function within CTAButton that calls window.gtag for analytics tracking (event_category="Landing Page", event_label=location) with graceful degradation check: typeof window !== 'undefined' && window.gtag (~12 min)
- [ ] T014 [US3] Update all "Get Started" buttons (navigation, hero, bottom) to use CTAButton component with correct location prop values: "nav", "hero", "bottom" (~15 min)
- [ ] T015 [US3] Update CTA button copy to include "for Free" where appropriate: "Get Started for Free" per FR-010 requirement (~5 min)
- [ ] T016 [US3] Visually verify all 3 CTA buttons are visible in their locations (nav bar, hero section, bottom section), styled correctly (primary indigo vs secondary white), and navigate to /register on click (~8 min)
- [ ] T017 [US3] Test authenticated user redirect: manually create better-auth.session_token cookie in DevTools, navigate to "/", verify automatic redirect to "/dashboard" (~10 min)

**Checkpoint**: All user stories should now be independently functional - complete landing page with value prop, features, and working CTAs

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Accessibility, performance, and final validation across all user stories

**Estimated Time**: ~95 minutes total

- [ ] T018 [P] Add loading state handling in LandingPage component: if isPending return minimal loading div, if session return null per research.md pattern (~8 min)
- [ ] T019 [P] Verify proper heading hierarchy using browser accessibility inspector: h1 once (hero headline), h2 for section titles (features section), h3 for feature card titles - no skipped levels (~8 min)
- [ ] T020 [P] Check color contrast compliance using WebAIM Contrast Checker tool: ensure all body text has ≥4.5:1 ratio, darken slate-400 to slate-500/600 if needed (~12 min)
- [ ] T021 Run Lighthouse accessibility audit in Chrome DevTools (Desktop + Mobile modes), document all findings with scores and specific issues flagged (~12 min)
- [ ] T022 Fix Lighthouse accessibility issues identified in T021: add missing alt text, improve contrast, correct heading order, add ARIA labels where needed until score ≥90 (~20 min)
- [ ] T023 Test keyboard navigation: Tab through all interactive elements (nav CTAs, hero CTAs, bottom CTA, feature cards if interactive), verify Enter key activates links, verify visible focus indicators on all focusable elements (~10 min)
- [ ] T024 Verify dashboard preview mockup section still renders correctly and hasn't been affected by layout changes (check window controls, sidebar, stats grid, task list) (~5 min)
- [ ] T025 Verify mobile responsive layout at critical breakpoints: test at 320px (iPhone SE), 375px (iPhone 12), 768px (iPad), 1024px (desktop) - ensure no horizontal scrolling, feature cards stack properly, dashboard preview scales (~12 min)
- [ ] T026 End-to-end user flow test: load landing page → scroll to features section → read feature descriptions → click primary CTA → verify navigation to /register page - complete flow works smoothly (~8 min)
- [ ] T027 Run npm run build in frontend directory and verify production build completes successfully with no TypeScript errors, ESLint warnings, or build failures (~10 min)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001 types needed for T003) - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 (different content sections)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2 (adds CTAs and auth logic)

### Within Each User Story

- Tasks marked [P] within a story can run in parallel
- Content updates before layout/styling updates
- Core functionality before responsive/accessibility validation
- Build verification tasks before testing tasks

### Parallel Opportunities

- **Setup tasks**: T001 and T002 can run in parallel (different files)
- **User Story 2 tasks**: T006 (component creation) can run in parallel with reading existing code patterns
- **User Story 3 tasks**: T011 (auth redirect) and T012 (CTAButton component) can run in parallel (different concerns)
- **Polish tasks**: T018, T019, T020 can run in parallel (different validation checks)
- **All User Stories (Phase 3-5)** can be worked on in parallel by different team members after Phase 2 completes

---

## Parallel Example: User Story 3

```bash
# Launch parallel tasks for User Story 3:
Task T011: "Add authenticated user redirect logic with useSession and useRouter"
Task T012: "Create CTAButton component with TypeScript interface and variant styling"

# Then sequential tasks (depend on T011, T012):
Task T013: "Implement handleCTAClick function with analytics tracking"
Task T014: "Update all Get Started buttons to use CTAButton component"
# etc.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (~25 min)
2. Complete Phase 2: Foundational (~15 min)
3. Complete Phase 3: User Story 1 (~25 min)
4. **STOP and VALIDATE**: View landing page, verify hero section communicates AI value proposition clearly
5. Deploy/demo if ready

**Total MVP Time**: ~65 minutes (just over 1 hour)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (~40 min)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! ~65 min total)
3. Add User Story 2 → Test independently → Deploy/Demo (~140 min total)
4. Add User Story 3 → Test independently → Deploy/Demo (~225 min total)
5. Add Polish → Final validation → Deploy/Demo (~320 min total / ~5.3 hours)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With 3 developers:

1. Team completes Setup + Foundational together (~40 min)
2. Once Foundational is done:
   - Developer A: User Story 1 (Hero section updates) ~25 min
   - Developer B: User Story 2 (Features section updates) ~75 min
   - Developer C: User Story 3 (CTA and auth logic) ~85 min
3. Team reconvenes for Phase 6: Polish together (~95 min)

**Total Team Time**: ~135 minutes (~2.25 hours with parallel execution)

---

## Task Sizing Summary

| Phase | Total Tasks | Estimated Time | Average per Task |
|-------|-------------|----------------|------------------|
| Phase 1: Setup | 2 | ~25 min | ~13 min |
| Phase 2: Foundational | 1 | ~15 min | ~15 min |
| Phase 3: User Story 1 | 2 | ~25 min | ~13 min |
| Phase 4: User Story 2 | 5 | ~75 min | ~15 min |
| Phase 5: User Story 3 | 7 | ~85 min | ~12 min |
| Phase 6: Polish | 10 | ~95 min | ~10 min |
| **Total** | **27 tasks** | **~320 min (~5.3 hours)** | **~12 min avg** |

**Optimization Summary**:
- **Removed 4 tasks**: T003, T004 (implicit research), T009, T016 (redundant validations)
- **Combined 5 task pairs**: Hero content (T006+T007), Icons+Component (T010+T011), Click handler (T019+T020), FeatureCard styling (T014+T015)
- **Split 1 task**: Lighthouse audit (T027) → Run audit + Fix issues separately
- **Added 4 tasks**: FeatureCard verification (T007), CTA visual verification (T016), Dashboard preview regression check (T024), End-to-end flow test (T026)
- **Net result**: 30 → 27 tasks, better focused, eliminated redundancy

**Task Sizing Validation**:
- All tasks sized for 5-25 minute completion
- Average: ~12 minutes per task
- No tasks exceed 25 minutes
- Eliminates trivial 2-3 minute tasks through combination
- Each task delivers testable, committable progress

---

## Revision History

| Version | Date | Changes | Task Count |
|---------|------|---------|------------|
| 1.0 | 2025-12-29 | Initial task generation | 30 tasks |
| 1.1 | 2025-12-29 | Optimized: removed redundancy, combined granular tasks, added critical verifications | 27 tasks |

---

## Notes

- [P] tasks = different files or independent sections, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group of parallel tasks
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tasks sized for 5-25 minute completion time (avg 12 min)
- Research tasks (reading code) are implicit - not separate tasks
- Validation tasks are consolidated to avoid redundant checks
