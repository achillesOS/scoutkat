create table if not exists public.user_preferences (
  user_id uuid primary key references public.users(id) on delete cascade,
  alert_preference text not null default 'balanced',
  onboarding_completed_at timestamptz,
  updated_at timestamptz not null default now()
);

create index if not exists idx_user_preferences_alert on public.user_preferences(alert_preference);
