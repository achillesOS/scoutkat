from datetime import datetime, timedelta, timezone

from app.repositories.supabase_client import get_supabase_client


class ScoreRepository:
    def insert_score_snapshot(self, payload: dict) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return payload
        response = client.table("score_snapshots").insert(payload).execute()
        return response.data[0] if response.data else None

    def latest_score_snapshot(self, token_id: str) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None
        response = (
            client.table("score_snapshots")
            .select("*")
            .eq("token_id", token_id)
            .order("timestamp", desc=True)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    def recent_score_snapshots(self, token_id: str, limit: int = 24) -> list[dict]:
        client = get_supabase_client()
        if client is None:
            return []
        response = (
            client.table("score_snapshots")
            .select("*")
            .eq("token_id", token_id)
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )
        return list(response.data or [])


def cooldown_cutoff_iso(minutes: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes)).isoformat()
