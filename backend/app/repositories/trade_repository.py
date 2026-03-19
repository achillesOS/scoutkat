from __future__ import annotations

from app.repositories.supabase_client import get_supabase_client


class TradeRepository:
    def list_open_positions(self) -> list[dict]:
        client = get_supabase_client()
        if client is None:
            return []
        response = (
            client.table("trade_positions")
            .select("*")
            .eq("status", "open")
            .order("opened_at", desc=True)
            .execute()
        )
        return list(response.data or [])

    def latest_open_position_for_symbol(self, symbol: str) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None
        response = (
            client.table("trade_positions")
            .select("*")
            .eq("symbol", symbol.upper())
            .eq("status", "open")
            .order("opened_at", desc=True)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    def open_positions_by_symbols(self, symbols: list[str]) -> list[dict]:
        client = get_supabase_client()
        if client is None:
            return []
        response = (
            client.table("trade_positions")
            .select("*")
            .in_("symbol", [symbol.upper() for symbol in symbols])
            .eq("status", "open")
            .order("opened_at", desc=True)
            .execute()
        )
        return list(response.data or [])

    def create_position(self, payload: dict) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return payload
        response = client.table("trade_positions").insert(payload).execute()
        return response.data[0] if response.data else None

    def close_position(self, position_id: str, payload: dict) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return {"id": position_id} | payload
        response = (
            client.table("trade_positions")
            .update(payload)
            .eq("id", position_id)
            .execute()
        )
        return response.data[0] if response.data else None

    def insert_execution_log(self, payload: dict) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return payload
        response = client.table("trade_execution_logs").insert(payload).execute()
        return response.data[0] if response.data else None
