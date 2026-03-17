insert into public.tokens (symbol, name, market_type, is_active)
values
  ('BTC', 'Bitcoin', 'perp', true),
  ('ETH', 'Ethereum', 'perp', true),
  ('SOL', 'Solana', 'perp', true),
  ('HYPE', 'Hyperliquid', 'perp', true),
  ('XRP', 'XRP', 'perp', true),
  ('DOGE', 'Dogecoin', 'perp', true),
  ('BNB', 'BNB', 'perp', true),
  ('SUI', 'Sui', 'perp', true),
  ('ADA', 'Cardano', 'perp', true),
  ('AVAX', 'Avalanche', 'perp', true),
  ('LINK', 'Chainlink', 'perp', true)
on conflict (symbol) do nothing;
