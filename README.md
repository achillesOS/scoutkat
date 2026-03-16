# Scoutkat MVP

Scoutkat (哨鼬) is an AI-native crypto signal product that detects divergence between X attention, Hyperliquid market structure, and Hyperliquid perp positioning.

This repo contains the first working scaffold for a solo-developer MVP:

- `frontend/`: Next.js + TypeScript + Tailwind CSS + shadcn-style UI
- `backend/`: FastAPI + APScheduler + provider/service/repository layers
- `supabase/`: SQL migrations and seed data
- `docs/`: architecture, implementation phases, and migration notes
- `render.yaml`: Render Blueprint for backend API and cron job

## Final Repo Structure

```text
.
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── jobs/
│   │   ├── models/
│   │   ├── prompts/
│   │   ├── providers/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── scoring/
│   │   └── services/
│   └── tests/
├── supabase/
│   ├── migrations/
│   └── seed/
└── docs/
```

## MVP Phases

1. Foundation
   - Scaffold frontend/backend
   - Define schema, scoring config, prompt versioning, service interfaces
   - Ship mock-backed dashboard and API
2. Data Ingestion
   - Hyperliquid market + positioning adapters
   - Supabase persistence
   - Redis cache and shortlist heuristics
3. Social Intelligence
   - Grok/X adapter
   - strict JSON extraction
   - retry, timeout, repair, caching
4. Signal Engine
   - rolling normalization
   - signal detection, cooldowns, invalidation tracking
   - explanation generation and Telegram alerts
5. Production Hardening
   - auth, user watchlists, observability, deploy pipelines

## Quick Start

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App defaults to `http://localhost:3000`.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

API defaults to `http://localhost:8000`.

### Environment

Copy the example env files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

## Supabase

Apply the initial schema in order:

1. `supabase/migrations/20260315_001_init.sql`
2. `supabase/migrations/20260316_002_add_raw_hyperliquid_json.sql`
3. `supabase/seed/001_tokens.sql`

## What Works In This Scaffold

- FastAPI app with required MVP endpoints
- Supabase-backed repositories for tokens, watchlists, and signal events
- Hyperliquid ingestion job that persists market and positioning snapshots
- service/repository/provider boundaries
- config-driven scoring engine
- signal detection and explanation schema validation
- APScheduler job wiring
- Next.js pages for watchlist, signals, signal detail, token detail, and my-edge
- Supabase-ready SQL schema and initial major-token seed data

## What Remains Next

- Supabase auth and per-user watchlist persistence
- Redis shortlist hardening and cache observability
- Historical backtesting and signal QA
- Production Grok quota management / secondary fallback provider
- Final Render environment setup and domain cutover

## Deployment

Production deployment is set up as:

- Frontend on Vercel
- Backend API on Render
- Scheduled ingestion/scoring on Render Cron

Deployment docs:

- [vercel-deploy.md](/Users/unmercy/Scoutkat/docs/vercel-deploy.md)
- [render-deploy.md](/Users/unmercy/Scoutkat/docs/render-deploy.md)
- [render.yaml](/Users/unmercy/Scoutkat/render.yaml)
