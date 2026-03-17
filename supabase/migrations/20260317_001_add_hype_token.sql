insert into public.tokens (symbol, name, market_type, is_active)
values ('HYPE', 'Hyperliquid', 'perp', true)
on conflict (symbol) do update set
  name = excluded.name,
  market_type = excluded.market_type,
  is_active = excluded.is_active;
