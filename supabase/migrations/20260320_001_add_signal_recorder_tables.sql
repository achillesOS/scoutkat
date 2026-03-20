create table if not exists public.signal_outcome_snapshots (
  id uuid primary key default gen_random_uuid(),
  signal_event_id uuid not null references public.signal_events(id) on delete cascade,
  token_id uuid not null references public.tokens(id) on delete cascade,
  symbol text not null,
  signal_type text not null,
  triggered_at timestamptz not null,
  horizon_minutes integer not null,
  entry_price numeric not null,
  exit_price numeric not null,
  raw_return_pct numeric not null,
  directional_return_pct numeric not null,
  max_favorable_excursion_pct numeric not null,
  max_adverse_excursion_pct numeric not null,
  outcome_label text not null,
  evaluated_at timestamptz not null default now(),
  unique(signal_event_id, horizon_minutes)
);

create table if not exists public.signal_optimizer_snapshots (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  signal_type text not null,
  horizon_minutes integer not null,
  sample_size integer not null,
  win_rate numeric not null,
  avg_directional_return_pct numeric not null,
  median_directional_return_pct numeric not null,
  recommended_min_score numeric not null,
  recommended_min_confidence numeric not null,
  recommendation_reason text not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_signal_outcomes_symbol_horizon on public.signal_outcome_snapshots(symbol, horizon_minutes, triggered_at desc);
create index if not exists idx_signal_optimizer_symbol_signal on public.signal_optimizer_snapshots(symbol, signal_type, horizon_minutes, created_at desc);
