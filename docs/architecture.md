# Scoutkat Architecture

## Principles

- Single backend service
- Single frontend app
- Explicit service boundaries without microservices
- Config-first weights and thresholds
- Provider outputs stored raw for debugging
- Grok called only for shortlisted tokens

## Backend Flow

1. Fetch Hyperliquid market snapshots
2. Fetch Hyperliquid positioning snapshots
3. Shortlist tokens for social refresh
4. Fetch Grok/X summaries for shortlisted tokens
5. Compute normalized component scores
6. Detect signal events
7. Generate explanation JSON
8. Send Telegram alerts with cooldown checks

## Runtime Components

- FastAPI: HTTP API
- APScheduler: recurring jobs
- Supabase/Postgres: system of record
- Redis: shortlist + freshness + alert cooldown cache
- Telegram Bot: notification channel

