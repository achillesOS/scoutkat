from app.repositories.fixtures import WATCHLIST_TOKEN_IDS
from app.repositories.supabase_client import get_supabase_client
from app.repositories.user_repository import UserRepository


class WatchlistRepository:
    def __init__(self) -> None:
        self.user_repository = UserRepository()

    def list_token_ids(self, user_id: str = "demo-user") -> list[str]:
        client = get_supabase_client()
        if client is not None:
            resolved_user_id = self.user_repository.get_or_create_default_user_id()
            if not resolved_user_id:
                return []
            response = (
                client.table("watchlists")
                .select("token_id")
                .eq("user_id", resolved_user_id)
                .execute()
            )
            if response.data is not None:
                return [row["token_id"] for row in response.data]
        return WATCHLIST_TOKEN_IDS

    def add(self, token_id: str, user_id: str = "demo-user") -> list[str]:
        client = get_supabase_client()
        if client is not None:
            resolved_user_id = self.user_repository.get_or_create_default_user_id()
            if not resolved_user_id:
                return []
            (
                client.table("watchlists")
                .upsert({"user_id": resolved_user_id, "token_id": token_id}, on_conflict="user_id,token_id")
                .execute()
            )
            return self.list_token_ids(user_id=resolved_user_id)
        if token_id not in WATCHLIST_TOKEN_IDS:
            WATCHLIST_TOKEN_IDS.append(token_id)
        return WATCHLIST_TOKEN_IDS

    def remove(self, token_id: str, user_id: str = "demo-user") -> list[str]:
        client = get_supabase_client()
        if client is not None:
            resolved_user_id = self.user_repository.get_or_create_default_user_id()
            if not resolved_user_id:
                return []
            (
                client.table("watchlists")
                .delete()
                .eq("user_id", resolved_user_id)
                .eq("token_id", token_id)
                .execute()
            )
            return self.list_token_ids(user_id=resolved_user_id)
        if token_id in WATCHLIST_TOKEN_IDS:
            WATCHLIST_TOKEN_IDS.remove(token_id)
        return WATCHLIST_TOKEN_IDS
