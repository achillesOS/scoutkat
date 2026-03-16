# Render Deployment

Scoutkat deploys the backend to Render with two services defined in [render.yaml](/Users/unmercy/Scoutkat/render.yaml):

- `scoutkat-backend`: FastAPI API
- `scoutkat-cycle`: Render Cron job that runs ingestion + scoring every 10 minutes

## Why this layout

- Keep the web API stateless on Render
- Avoid running APScheduler inside the web dyno in production
- Use a dedicated cron entrypoint for repeatable ingestion cycles

## Render setup steps

1. Connect the Git repo to Render.
2. Create services from the Blueprint file:
   - Render supports `render.yaml` Blueprints and monorepo `rootDir` services in the repo root. See [Blueprint YAML Reference](https://render.com/docs/blueprint-spec) and [web services docs](https://render.com/docs/web-services).
3. Fill secret environment variables in the Render dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `REDIS_URL`
   - `GROK_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_DEFAULT_CHAT_ID`
4. Deploy the Blueprint.

## Notes

- The backend web service exposes `/health` for Render health checks.
- The cron job uses `python -m app.jobs.run_cycle`.
- Production sets `ENABLE_SCHEDULER=false` because Render Cron is the scheduler.
- Render Cron schedules use cron expressions. See [Cron jobs](https://render.com/docs/cronjobs).
