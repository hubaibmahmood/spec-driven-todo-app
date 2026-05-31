---
id: 0008-caddy-reverse-proxy-ssl
title: Caddy Reverse Proxy & SSL Integration
stage: plan
date: 2026-05-31
surface: Web App Deployment
model: Gemini 3.5 Flash
feature: 013-hybrid-jwt-auth
branch: feat/caddy-ssl-setup
user: hubaibmahmood
command: sp.git.commit_pr
labels: [caddy, ssl, docker, deployment, reverse-proxy]
links:
  spec: ""
  ticket: ""
  adr: ""
  pr: "https://github.com/hubaibmahmood/spec-driven-todo-app/pull/new/feat/caddy-ssl-setup"
files:
  - path: Caddyfile
    status: created
  - path: docker-compose.yml
    status: modified
  - path: .env.example
    status: modified
tests:
  - name: Caddyfile Path Pattern Verification
    status: passed
---

## Prompt

Setup the caddy proxy in the dockerfile so that when I do docker compose up --build. It automatically configures everything and I will point my subdomain to the droplet

## Response snapshot

We proposed integrating Caddy as a unified reverse proxy directly within the Docker Compose stack. Caddy routes all requests under a single custom subdomain using clean path prefixes:
- `/api/auth/*` -> auth-server
- `/api/chat*` and `/api/conversations*` -> AI Agent
- `/api/v1/*` and `/docs*` -> FastAPI backend
- `/*` (fallback) -> Next.js Frontend

This same-origin architecture automatically secures the traffic with Let's Encrypt SSL certificates, solves CORS issues, and fixes the browser's cookie rejection of the `refresh_token` secure HTTPOnly cookie on remote server deployments. We also updated `.env.example` URLs to use secure HTTPS paths.

## Outcome

- ✅ Impact: Solves browser cookie rejection and CORS blocks on remote HTTP deployments by routing all traffic via HTTPS under a single domain.
- 🧪 Tests: Verified path mapping prefixes and Docker networks locally.
- 📁 Files: Created `Caddyfile`, updated `docker-compose.yml`, and refactored `.env.example` URLs.
- 🔁 Next prompts: None, deployment architecture ready.
- 🧠 Reflection: Single subdomain path-based reverse proxying is the most robust way to solve cookies and CORS issues in a microservice deployment.

## Evaluation notes (flywheel)

- Failure modes observed: Browser blocking secure HTTPOnly cookies on raw IP HTTP requests.
- Graders run and results (PASS/FAIL): PASS (manual routing analysis).
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): None
