from app.core.config import get_settings
from app.repositories.supabase_client import get_supabase_client


class UserRepository:
    def get_or_create_default_user_id(self) -> str | None:
        record = self.get_or_create_default_user()
        return record["id"] if record else None

    def get_or_create_default_user(self) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None

        settings = get_settings()
        existing = (
            client.table("users")
            .select("id,email,telegram_chat_id")
            .eq("email", settings.default_user_email)
            .limit(1)
            .execute()
        )
        if existing.data:
            return existing.data[0]

        created = client.table("users").insert({"email": settings.default_user_email}).execute()
        if created.data:
            return created.data[0]
        return None
