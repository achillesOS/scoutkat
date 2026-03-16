from collections.abc import Iterable

from app.repositories.supabase_client import get_supabase_client


class TokenRepository:
    def list_tokens(self) -> list[dict]:
        client = get_supabase_client()
        if client is None:
            return []
        response = (
            client.table("tokens")
            .select("id,symbol,name,market_type,is_active")
            .eq("is_active", True)
            .order("symbol")
            .execute()
        )
        return list(response.data or [])

    def get_by_symbol(self, symbol: str) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None
        response = (
            client.table("tokens")
            .select("id,symbol,name,market_type,is_active")
            .eq("symbol", symbol.upper())
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]
        return None

    def get_by_id(self, token_id: str) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None
        response = (
            client.table("tokens")
            .select("id,symbol,name,market_type,is_active")
            .eq("id", token_id)
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]
        return None

    def get_by_symbols(self, symbols: Iterable[str]) -> list[dict]:
        normalized = [symbol.upper() for symbol in symbols]
        client = get_supabase_client()
        if client is None:
            return []
        response = (
            client.table("tokens")
            .select("id,symbol,name,market_type,is_active")
            .in_("symbol", normalized)
            .eq("is_active", True)
            .execute()
        )
        return list(response.data or [])

    def get_by_ids(self, token_ids: Iterable[str]) -> list[dict]:
        normalized = list(token_ids)
        client = get_supabase_client()
        if client is None or not normalized:
            return []
        response = (
            client.table("tokens")
            .select("id,symbol,name,market_type,is_active")
            .in_("id", normalized)
            .eq("is_active", True)
            .execute()
        )
        return list(response.data or [])
