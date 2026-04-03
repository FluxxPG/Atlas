# Deployment Notes

## Frontend

- Deploy `apps/web` to Vercel
- Configure `NEXT_PUBLIC_API_URL` to the public FastAPI base URL
- Configure `NEXT_PUBLIC_WS_URL` to the public WebSocket endpoint
- `vercel.json` is ready for monorepo builds from the workspace root

## API

- Deploy the FastAPI service from `infra/docker/api.Dockerfile`
- Set `DATABASE_URL`, `SYNC_DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, and CORS settings
- Expose `/health` for platform health checks
- Expose `/ready` for dependency-aware readiness checks
- Expose `/metrics` for Prometheus scraping
- Configure `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `OPENAI_API_KEY`, `HOSTED_EMBEDDING_MODEL`, and `HOSTED_RERANK_MODEL` for production AI and billing
- Configure `SERPAPI_API_KEY`, `HUNTER_API_KEY`, and `PEOPLEDATALABS_API_KEY` for real discovery and enrichment vendors

## Worker

- Deploy the worker from `infra/docker/worker.Dockerfile`
- Reuse the same database and Redis environment as the API
- Run at least one always-on worker process for crawl and rebuild jobs
- Configure `DISCOVERY_PROVIDER=hybrid` for SerpAPI plus public web fallback
- Run multiple worker replicas for parallel crawl throughput

## Database

- Use Supabase PostgreSQL with pgvector enabled
- Apply `supabase/migrations/001_init.sql`
- Apply `supabase/migrations/002_enterprise.sql`
- Apply `supabase/migrations/003_commercial_ops.sql`
- Schedule recurring seed and rebuild calls using a platform cron or job runner

## Recommended production add-ons

- Managed Redis or Upstash
- Structured logs and metrics
- Secret rotation
- Sentry or equivalent error monitoring
- CI/CD validation for `npm run build:web`, `npm run test:python`, and API readiness smoke
- Prometheus scraping via `/metrics`
- Optional observability stack through `docker-compose.observability.yml`
- Railway deployment can use `railway.toml` for the API container
