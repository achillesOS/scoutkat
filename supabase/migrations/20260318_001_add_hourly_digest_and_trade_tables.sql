create table if not exists public.hourly_digest_runs (
  id uuid primary key default gen_random_uuid(),
  scheduled_for timestamptz not null,
  generated_at timestamptz not null default now(),
  channel text not null default 'telegram',
  delivery_status text not null default 'pending'
);

create table if not exists public.hourly_digest_rows (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references public.hourly_digest_runs(id) on delete cascade,
  token_id uuid references public.tokens(id) on delete set null,
  symbol text not null,
  status text not null,
  signal_type text,
  signal_score numeric,
  confidence numeric,
  price numeric,
  market_timestamp timestamptz,
  why_now text,
  mode text,
  warning text,
  verified boolean not null default false
);

create table if not exists public.trade_positions (
  id uuid primary key default gen_random_uuid(),
  token_id uuid not null references public.tokens(id) on delete cascade,
  symbol text not null,
  side text not null,
  signal_type text not null,
  source_digest_row_id uuid references public.hourly_digest_rows(id) on delete set null,
  entry_price numeric not null,
  entry_notional_usd numeric not null,
  leverage numeric not null,
  status text not null default 'open',
  opened_at timestamptz not null default now(),
  close_reason text,
  closed_at timestamptz
);

create table if not exists public.trade_execution_logs (
  id uuid primary key default gen_random_uuid(),
  position_id uuid references public.trade_positions(id) on delete set null,
  symbol text not null,
  action text not null,
  status text not null,
  provider_order_id text,
  request_json jsonb not null default '{}'::jsonb,
  response_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_hourly_digest_runs_scheduled_for on public.hourly_digest_runs(scheduled_for desc);
create index if not exists idx_hourly_digest_rows_run_symbol on public.hourly_digest_rows(run_id, symbol);
create index if not exists idx_trade_positions_symbol_status on public.trade_positions(symbol, status);
create index if not exists idx_trade_execution_logs_symbol_created on public.trade_execution_logs(symbol, created_at desc);
