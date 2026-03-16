create extension if not exists "pgcrypto";

create table if not exists public.tokens (
  id uuid primary key default gen_random_uuid(),
  symbol text not null unique,
  name text not null,
  market_type text not null default 'perp',
  is_active boolean not null default true
);

create table if not exists public.x_attention_snapshots (
  id uuid primary key default gen_random_uuid(),
  token_id uuid not null references public.tokens(id) on delete cascade,
  timestamp timestamptz not null,
  mentions_1h numeric not null,
  mentions_6h numeric not null,
  unique_authors_1h numeric not null,
  mention_acceleration numeric not null,
  retail_breadth numeric not null,
  expert_presence numeric not null,
  narrative_novelty numeric not null,
  raw_grok_json jsonb not null default '{}'::jsonb
);

create table if not exists public.hl_market_snapshots (
  id uuid primary key default gen_random_uuid(),
  token_id uuid not null references public.tokens(id) on delete cascade,
  timestamp timestamptz not null,
  mark_price numeric not null,
  mid_price numeric not null,
  return_1h numeric not null,
  return_4h numeric not null,
  volume_1h numeric not null,
  volume_24h numeric not null,
  trade_imbalance_15m numeric not null,
  book_imbalance_top5 numeric not null,
  absorption_score numeric not null,
  price_efficiency numeric not null
);

create table if not exists public.hl_positioning_snapshots (
  id uuid primary key default gen_random_uuid(),
  token_id uuid not null references public.tokens(id) on delete cascade,
  timestamp timestamptz not null,
  funding numeric not null,
  funding_zscore numeric not null,
  open_interest numeric not null,
  oi_change_1h numeric not null,
  oi_volume_ratio numeric not null,
  overheat_score numeric not null
);

create table if not exists public.score_snapshots (
  id uuid primary key default gen_random_uuid(),
  token_id uuid not null references public.tokens(id) on delete cascade,
  timestamp timestamptz not null,
  attention_score numeric not null,
  structure_score numeric not null,
  positioning_score numeric not null,
  hidden_accumulation_score numeric not null,
  narrative_ignition_score numeric not null,
  retail_trap_score numeric not null,
  signal_type text not null,
  signal_score numeric not null,
  confidence numeric not null
);

create table if not exists public.signal_events (
  id uuid primary key default gen_random_uuid(),
  token_id uuid not null references public.tokens(id) on delete cascade,
  triggered_at timestamptz not null,
  signal_type text not null,
  signal_score numeric not null,
  confidence numeric not null,
  explanation_json jsonb not null default '{}'::jsonb,
  invalidation_json jsonb not null default '{}'::jsonb,
  status text not null default 'active'
);

create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  telegram_chat_id text,
  created_at timestamptz not null default now()
);

create table if not exists public.watchlists (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  token_id uuid not null references public.tokens(id) on delete cascade,
  unique (user_id, token_id)
);

create table if not exists public.notification_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  signal_event_id uuid not null references public.signal_events(id) on delete cascade,
  channel text not null,
  sent_at timestamptz not null default now(),
  delivery_status text not null
);

create index if not exists idx_tokens_symbol on public.tokens(symbol);
create index if not exists idx_x_attention_token_time on public.x_attention_snapshots(token_id, timestamp desc);
create index if not exists idx_hl_market_token_time on public.hl_market_snapshots(token_id, timestamp desc);
create index if not exists idx_hl_positioning_token_time on public.hl_positioning_snapshots(token_id, timestamp desc);
create index if not exists idx_scores_token_time on public.score_snapshots(token_id, timestamp desc);
create index if not exists idx_signal_events_token_time on public.signal_events(token_id, triggered_at desc);

