alter table public.hl_market_snapshots
add column if not exists raw_hl_json jsonb not null default '{}'::jsonb;

alter table public.hl_positioning_snapshots
add column if not exists raw_hl_json jsonb not null default '{}'::jsonb;
