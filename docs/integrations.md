# External Integrations

## Discovery

- `DISCOVERY_PROVIDER=hybrid` enables a hybrid discovery path that prefers SerpAPI when `SERPAPI_API_KEY` is set and falls back to the public web connector when it is not.
- `DISCOVERY_PROVIDER=serpapi` forces Google-backed search discovery through SerpAPI.
- `DISCOVERY_PROVIDER=public_web` forces the DuckDuckGo HTML connector only.

## Enrichment

- `HUNTER_API_KEY` enables verified domain-level email enrichment and contact hints.
- `PEOPLEDATALABS_API_KEY` enables company enrichment for descriptions, social profiles, employee hints, and technology attributes when available.
- The worker merges third-party enrichment with local crawler extraction instead of replacing local findings.

## AI Ranking

- `OPENAI_API_KEY` + `HOSTED_EMBEDDING_MODEL` enables hosted embedding generation for pgvector search.
- `OPENAI_API_KEY` + `HOSTED_RERANK_MODEL` enables hosted reranking for natural-language search results using the Responses API.
- If hosted AI credentials are not set, AtlasBI falls back to deterministic local embeddings and heuristic reranking.

## Billing

- `STRIPE_SECRET_KEY` enables checkout session creation for subscription upgrades.
- `STRIPE_WEBHOOK_SECRET` enables webhook signature verification for checkout and invoice events.
- `STRIPE_PUBLIC_KEY` is reserved for future client-side card collection surfaces.
