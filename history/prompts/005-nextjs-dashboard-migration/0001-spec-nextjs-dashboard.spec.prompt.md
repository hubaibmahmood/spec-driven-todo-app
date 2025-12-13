---
id: 0001
title: spec-nextjs-dashboard
stage: spec
date: 2025-12-12
surface: cli
model: gemini-2.0-flash-exp
feature: 005-nextjs-dashboard-migration
branch: 005-nextjs-dashboard-migration
user: mac
command: /sp.specify
labels: [migration, nextjs, spec]
links:
  spec: specs/005-nextjs-dashboard-migration/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - specs/005-nextjs-dashboard-migration/spec.md
  - specs/005-nextjs-dashboard-migration/checklists/requirements.md
tests:
  - N/A
---

## Prompt

create specification for creating the exact same signin/signup forms and dashboard that is implemented in @todo-app-login&dashboard/** using Next.js 16+ (App Router) instead of react, TypeScript and Tailwind CSS. Also: ## Patterns - Use server components by default - Client components only when needed (interactivity) - API calls go through /lib/api.ts ## Component Structure - /components - Reusable UI components - /app - Pages and layouts ## API Client All backend calls should use the api client: import { api } from ' @/lib/api' const tasks = await api.getTasks() ## Styling - Use Tailwind CSS classes - No inline styles - Follow existing component patterns

## Response snapshot

Created specification for Next.js dashboard migration (Feature 005).
- Analyzed existing React implementation.
- Defined user scenarios (Auth, Dashboard, CRUD, AI).
- Established technical requirements (Next.js 16, App Router, Server Components).
- Created spec file: `specs/005-nextjs-dashboard-migration/spec.md`
- Validated with checklist: `specs/005-nextjs-dashboard-migration/checklists/requirements.md`

## Outcome

- ✅ Impact: Established clear requirements for migrating the React dashboard to Next.js 16.
- 🧪 Tests: N/A (Spec phase)
- 📁 Files: Created spec.md and requirements.md
- 🔁 Next prompts: /sp.plan
- 🧠 Reflection: The request was a technical migration, so standard "no implementation details" rules for specs were adapted to treat the target stack as the business requirement.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
