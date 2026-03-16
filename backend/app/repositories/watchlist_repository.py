from app.repositories.supabase_client import get_supabase_client
from app.repositories.user_repository import UserRepository


class WatchlistRepository:
    def __init__(self) -> None:
        self.user_repository = UserRepository()

    def list_token_ids(self, user_email: str) -> list[str]:
        client = get_supabase_client()
        if client is None:
            return []
        resolved_user_id = self.user_repository.get_or_create_user_id(user_email)
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
        return []

    def replace(self, token_ids: list[str], user_email: str) -> list[str]:
        client = get_supabase_client()
        if client is None:
            return []
        resolved_user_id = self.user_repository.get_or_create_user_id(user_email)
        if not resolved_user_id:
            return []
        client.table("watchlists").delete().eq("user_id", resolved_user_id).execute()
        if token_ids:
            payload = [{"user_id": resolved_user_id, "token_id": token_id} for token_id in token_ids]
            client.table("watchlists").insert(payload).execute()
        return self.list_token_ids(user_email)

    def add(self, token_id: str, user_email: str) -> list[str]:
        client = get_supabase_client()
        if client is None:
            return []
        resolved_user_id = self.user_repository.get_or_create_user_id(user_email)
        if not resolved_user_id:
            return []
        (
            client.table("watchlists")
            .upsert({"user_id": resolved_user_id, "token_id": token_id}, on_conflict="user_id,token_id")
            .execute()
        )
        return self.list_token_ids(user_email)

    def remove(self, token_id: str, user_email: str) -> list[str]:
        client = get_supabase_client()
        if client is None:
            return []
        resolved_user_id = self.user_repository.get_or_create_user_id(user_email)
        if not resolved_user_id:
            return []
        (
            client.table("watchlists")
            .delete()
            .eq("user_id", resolved_user_id)
            .eq("token_id", token_id)
            .execute()
        )
        return self.list_token_ids(user_email)
