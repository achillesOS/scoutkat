alter table public.tokens enable row level security;
alter table public.x_attention_snapshots enable row level security;
alter table public.hl_market_snapshots enable row level security;
alter table public.hl_positioning_snapshots enable row level security;
alter table public.score_snapshots enable row level security;
alter table public.signal_events enable row level security;
alter table public.users enable row level security;
alter table public.watchlists enable row level security;
alter table public.notification_logs enable row level security;
alter table public.user_preferences enable row level security;

drop policy if exists "public read tokens" on public.tokens;
create policy "public read tokens"
on public.tokens
for select
to anon, authenticated
using (is_active = true);

drop policy if exists "public read active signals" on public.signal_events;
create policy "public read active signals"
on public.signal_events
for select
to anon, authenticated
using (status = 'active');

drop policy if exists "users read own profile" on public.users;
create policy "users read own profile"
on public.users
for select
to authenticated
using (lower(email) = lower(coalesce(auth.jwt() ->> 'email', '')));

drop policy if exists "users read own watchlist" on public.watchlists;
create policy "users read own watchlist"
on public.watchlists
for select
to authenticated
using (
  exists (
    select 1
    from public.users
    where public.users.id = watchlists.user_id
      and lower(public.users.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
  )
);

drop policy if exists "users read own preferences" on public.user_preferences;
create policy "users read own preferences"
on public.user_preferences
for select
to authenticated
using (
  exists (
    select 1
    from public.users
    where public.users.id = user_preferences.user_id
      and lower(public.users.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
  )
);
