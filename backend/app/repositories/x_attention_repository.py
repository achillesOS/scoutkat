from app.repositories.supabase_client import get_supabase_client


class XAttentionRepository:
    def latest_snapshot(self, token_id: str) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None
        response = (
            client.table("x_attention_snapshots")
            .select("*")
            .eq("token_id", token_id)
            .order("timestamp", desc=True)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    def insert_snapshot(self, payload: dict) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return payload
        response = client.table("x_attention_snapshots").insert(payload).execute()
        return response.data[0] if response.data else None

    def recent_snapshots(self, token_id: str, limit: int = 24) -> list[dict]:
        client = get_supabase_client()
        if client is None:
            return []
        response = (
            client.table("x_attention_snapshots")
            .select("*")
            .eq("token_id", token_id)
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )
        return list(response.data or [])

    def snapshots_since(self, token_id: str, since_iso: str, limit: int = 240) -> list[dict]:
        client = get_supabase_client()
        if client is None:
            return []
        response = (
            client.table("x_attention_snapshots")
            .select("*")
            .eq("token_id", token_id)
            .gte("timestamp", since_iso)
            .order("timestamp", desc=False)
            .limit(limit)
            .execute()
        )
        return list(response.data or [])
