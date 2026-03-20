from __future__ import annotations

from app.repositories.supabase_client import get_supabase_client


class SignalRecorderRepository:
    def upsert_outcome_snapshot(self, payload: dict) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return payload
        response = (
            client.table("signal_outcome_snapshots")
            .upsert(payload, on_conflict="signal_event_id,horizon_minutes")
            .execute()
        )
        return response.data[0] if response.data else None

    def list_recent_outcomes(
        self,
        *,
        symbol: str,
        signal_type: str,
        horizon_minutes: int,
        limit: int = 40,
    ) -> list[dict]:
        client = get_supabase_client()
        if client is None:
            return []
        response = (
            client.table("signal_outcome_snapshots")
            .select("*")
            .eq("symbol", symbol.upper())
            .eq("signal_type", signal_type)
            .eq("horizon_minutes", horizon_minutes)
            .order("triggered_at", desc=True)
            .limit(limit)
            .execute()
        )
        return list(response.data or [])

    def insert_optimizer_snapshot(self, payload: dict) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return payload
        response = client.table("signal_optimizer_snapshots").insert(payload).execute()
        return response.data[0] if response.data else None

    def latest_optimizer_snapshot(self, symbol: str, signal_type: str, horizon_minutes: int = 60) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None
        response = (
            client.table("signal_optimizer_snapshots")
            .select("*")
            .eq("symbol", symbol.upper())
            .eq("signal_type", signal_type)
            .eq("horizon_minutes", horizon_minutes)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None
