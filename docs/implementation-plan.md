# Scoutkat Implementation Plan

## Phase 1: Working Scaffold

- create repo structure
- create FastAPI app and required endpoints
- create Next.js app with required routes
- add initial scoring config and signal formulas
- add explanation JSON schemas and versioned prompts
- add Supabase schema and seed data

## Phase 2: Market Data

- implement Hyperliquid snapshot ingestion
- persist normalized market and positioning snapshots
- compute rolling z-scores locally
- add Redis freshness keys

## Phase 3: Social Data

- implement Grok query planner
- only refresh social when stale or shortlisted
- validate and repair JSON outputs
- store raw Grok payloads

## Phase 4: Signal Productization

- improve confidence heuristics
- dedupe alerts with cooldown windows
- add user-specific watchlist persistence
- send Telegram alerts

## Phase 5: Production Readiness

- auth integration
- background job telemetry
- rate limiting and retries
- deploy frontend/backend/redis/supabase

