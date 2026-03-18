# Telegram Trading Branch Notes

This branch isolates the Telegram hourly divergence channel and the upcoming trade executor work so Render can target it independently from the main product line.

## Scope

- Keep the Telegram hourly digest as an independent channel.
- Keep product API behavior and the existing 10-minute cycle separate.
- Add trading automation only as a separate executor/worker.

## Current Telegram Channel

- Hourly digest symbols: `BTC,ETH,SOL,HYPE,BNB`
- Delivery target: Telegram channel via `TELEGRAM_BOT_TOKEN` and `TELEGRAM_DEFAULT_CHAT_ID`
- Production scheduling: Render cron, not local APScheduler

## Trading Design Constraints

- The trading system must consume the hourly digest result, not parse Telegram text.
- The digest is hourly and may arrive 1-2 minutes late.
- The executor must tolerate late arrivals and should not assume exact top-of-hour delivery.
- Trading decisions should use the latest completed digest within a grace window instead of requiring exact timestamps.

## Recommended Execution Model

- Separate worker/service, not part of the API web service
- Runs hourly after the digest cron or polls for the latest digest row
- Only trades `live` signals
- Ignores `fallback` and `unavailable`
- Uses a dedicated Hyperliquid agent wallet with limited capital
- Supports per-symbol leverage overrides via `TRADE_LEVERAGE_MAP`
- Supports per-symbol notional overrides via `TRADE_NOTIONAL_USD_MAP`

## Latency Rule

- Treat a digest as valid if it arrives within a small grace window after the expected hour.
- Recommended grace window for execution logic: `10 minutes`
- Do not skip a digest solely because it was not emitted exactly at `HH:00`

## First Executor Shape

- Render cron target: `scoutkat-trade-executor-sg`
- Default run time: `10` minutes after each hour
- Default confirmation rule: `2` consecutive live hourly digests with the same tradable signal
- Default hold window: `6` hours
