from __future__ import annotations

from datetime import datetime, timezone

from app.repositories.supabase_client import get_supabase_client


class HourlyDigestRepository:
    def create_run(self, payload: dict) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return payload
        response = client.table("hourly_digest_runs").insert(payload).execute()
        return response.data[0] if response.data else None

    def update_run_status(self, run_id: str, delivery_status: str) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return {"id": run_id, "delivery_status": delivery_status}
        response = (
            client.table("hourly_digest_runs")
            .update({"delivery_status": delivery_status})
            .eq("id", run_id)
            .execute()
        )
        return response.data[0] if response.data else None

    def insert_rows(self, payload: list[dict]) -> list[dict]:
        client = get_supabase_client()
        if client is None:
            return payload
        if not payload:
            return []
        response = client.table("hourly_digest_rows").insert(payload).execute()
        return list(response.data or [])

    def recent_rows_for_symbol(self, symbol: str, limit: int = 6) -> list[dict]:
        client = get_supabase_client()
        if client is None:
            return []
        response = (
            client.table("hourly_digest_rows")
            .select("*,hourly_digest_runs!inner(scheduled_for)")
            .eq("symbol", symbol.upper())
            .order("market_timestamp", desc=True)
            .limit(limit)
            .execute()
        )
        return list(response.data or [])

    def latest_run_within_window(self, grace_minutes: int) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None
        cutoff = (datetime.now(timezone.utc).astimezone(timezone.utc)).isoformat()
        response = (
            client.table("hourly_digest_runs")
            .select("*")
            .lte("scheduled_for", cutoff)
            .in_("delivery_status", ["sent", "skipped_no_change"])
            .order("scheduled_for", desc=True)
            .order("generated_at", desc=True)
            .limit(10)
            .execute()
        )
        if not response.data:
            return None
        for run in response.data:
            scheduled_for = _parse_datetime(run["scheduled_for"])
            age_minutes = (datetime.now(timezone.utc) - scheduled_for).total_seconds() / 60
            if age_minutes > grace_minutes:
                continue
            if self.rows_for_run(str(run["id"])):
                return run
        return None

    def rows_for_run(self, run_id: str) -> list[dict]:
        client = get_supabase_client()
        if client is None:
            return []
        response = (
            client.table("hourly_digest_rows")
            .select("*")
            .eq("run_id", run_id)
            .order("symbol")
            .execute()
        )
        return list(response.data or [])

    def latest_sent_run(self) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None
        response = (
            client.table("hourly_digest_runs")
            .select("*")
            .eq("delivery_status", "sent")
            .order("scheduled_for", desc=True)
            .order("generated_at", desc=True)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
