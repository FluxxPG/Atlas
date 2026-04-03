# Global Intelligence Platform

Production-style monorepo for a globally scalable AI Business Intelligence SaaS platform with:

- `apps/web`: Next.js 14 App Router frontend
- `apps/api`: FastAPI async backend
- `apps/worker`: Python async worker runtime for crawling and enrichment
- `supabase/migrations`: PostgreSQL + pgvector schema
- `infra`: Docker, Redis, cron, deployment helpers

## Core capabilities

- AI search over company intelligence using pgvector
- Distributed crawl, enrichment, scoring, and signal pipelines
- Opportunity generation and buyer-intent detection
- Knowledge graph relationships between companies, industries, and technologies
- Realtime dashboards over WebSockets
- Admin controls for jobs, logs, configs, and users

## Local development

1. Copy `.env.example` to `.env`.
2. Provision PostgreSQL + Redis locally or via Supabase/managed Redis.
3. Start the API with `./scripts/run-api.ps1`.
4. Start the worker with `./scripts/run-worker.ps1`.
5. Start the frontend with `npm run dev:web`.
6. Seed demo data with `./scripts/seed-demo.ps1`.

## Verification

- Frontend build: `npm run build:web`
- Python tests: `npm run test:python`
- API smoke: `python -c "from app.main import app; print(app.title)"` from `apps/api`
- Worker smoke: `python -c "from worker.main import main; print(callable(main))"` from `apps/worker`

## Services

- Frontend: `http://localhost:3000`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Redis: `localhost:6379`

## Deployment targets

- Web: Vercel
- API/Worker: Railway or self-hosted Docker
- Database: Supabase PostgreSQL with pgvector

## Advanced feature coverage

- JWT auth plus registration/bootstrap admin flow
- RBAC guardrails for admin routes
- Queue-based crawl seeding for India
- Scoring, signal, intent, graph, and opportunity engines
- Saved leads and export APIs
- Dynamic company intelligence pages and advanced search filters
- Realtime WebSocket event distribution with Redis pub/sub fallback tolerance
