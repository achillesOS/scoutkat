from app.repositories.supabase_client import get_supabase_client


def _map_signal_row(row: dict) -> dict:
    token_relation = row.get("tokens")
    if isinstance(token_relation, list):
        token_symbol = token_relation[0].get("symbol") if token_relation else row.get("token_symbol", "")
    elif isinstance(token_relation, dict):
        token_symbol = token_relation.get("symbol", row.get("token_symbol", ""))
    else:
        token_symbol = row.get("token_symbol", "")

    return {
        "id": row["id"],
        "token_id": row["token_id"],
        "token_symbol": token_symbol,
        "triggered_at": row["triggered_at"],
        "signal_type": row["signal_type"],
        "signal_score": row["signal_score"],
        "confidence": row["confidence"],
        "status": row["status"],
        "explanation": row.get("explanation_json", {}),
        "invalidation_json": row.get("invalidation_json", {}),
    }


class SignalRepository:
    def list_signals(self) -> list[dict]:
        client = get_supabase_client()
        if client is None:
            return []
        response = (
            client.table("signal_events")
            .select(
                "id,token_id,triggered_at,signal_type,signal_score,confidence,status,"
                "explanation_json,invalidation_json,tokens(symbol)"
            )
            .order("triggered_at", desc=True)
            .limit(50)
            .execute()
        )
        return [_map_signal_row(row) for row in (response.data or [])]

    def get_signal(self, signal_id: str) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None
        response = (
            client.table("signal_events")
            .select(
                "id,token_id,triggered_at,signal_type,signal_score,confidence,status,"
                "explanation_json,invalidation_json,tokens(symbol)"
            )
            .eq("id", signal_id)
            .limit(1)
            .execute()
        )
        if response.data:
            return _map_signal_row(response.data[0])
        return None

    def list_signals_for_token(self, token_id: str) -> list[dict]:
        client = get_supabase_client()
        if client is None:
            return []
        response = (
            client.table("signal_events")
            .select(
                "id,token_id,triggered_at,signal_type,signal_score,confidence,status,"
                "explanation_json,invalidation_json,tokens(symbol)"
            )
            .eq("token_id", token_id)
            .order("triggered_at", desc=True)
            .limit(20)
            .execute()
        )
        return [_map_signal_row(row) for row in (response.data or [])]

    def create_signal_event(self, payload: dict) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None
        response = client.table("signal_events").insert(payload).execute()
        if response.data:
            return self.get_signal(response.data[0]["id"])
        return None
