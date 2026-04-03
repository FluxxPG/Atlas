# Architecture Overview

## Pipeline

1. Discovery jobs enter Redis-backed queues.
2. Worker nodes crawl targets asynchronously with Playwright and HTTP fallbacks.
3. Enrichment extracts structured facts, contact data, social handles, and technologies.
4. Signal and scoring engines compute business intelligence events and ranked opportunities.
5. The knowledge graph links organizations, technologies, markets, and intent signals.
6. Embeddings are generated for hybrid keyword + vector search in PostgreSQL via pgvector.
7. FastAPI exposes REST and WebSocket interfaces for the Next.js dashboard and admin console.

## Core bounded contexts

- Identity and access
- Company intelligence
- Crawl orchestration
- Signal analytics
- Opportunity generation
- Search and embeddings
- Realtime notifications
- Platform administration

## Scalability notes

- Stateless API and worker services
- Queue-driven fan-out
- Partition-friendly schema with JSONB extensions
- Background recomputation jobs for trends and aggregates
- WebSocket broadcast layer backed by Redis pub/sub

