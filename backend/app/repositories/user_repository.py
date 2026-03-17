from datetime import datetime, timezone

from app.repositories.supabase_client import get_supabase_client


class UserRepository:
    def get_or_create_default_user(self) -> dict | None:
        from app.core.config import get_settings

        return self.get_or_create_user(get_settings().default_user_email)

    def get_or_create_user_id(self, email: str) -> str | None:
        record = self.get_or_create_user(email)
        return record["id"] if record else None

    def get_or_create_user(self, email: str) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None

        existing = (
            client.table("users")
            .select("id,email,telegram_chat_id")
            .eq("email", email)
            .limit(1)
            .execute()
        )
        if existing.data:
            return existing.data[0]

        created = client.table("users").insert({"email": email}).execute()
        if created.data:
            return created.data[0]
        return None

    def get_profile(self, email: str) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None
        user = self.get_or_create_user(email)
        if user is None:
            return None

        preferences = (
            client.table("user_preferences")
            .select("alert_preference,onboarding_completed_at")
            .eq("user_id", user["id"])
            .limit(1)
            .execute()
        )
        watchlist = (
            client.table("watchlists")
            .select("tokens(symbol)")
            .eq("user_id", user["id"])
            .execute()
        )
        tracked_symbols = []
        for row in watchlist.data or []:
            token_relation = row.get("tokens")
            if isinstance(token_relation, dict) and token_relation.get("symbol"):
                tracked_symbols.append(token_relation["symbol"])

        preference_row = preferences.data[0] if preferences.data else None
        return {
            "email": user["email"],
            "tracked_symbols": tracked_symbols,
            "alert_preference": preference_row.get("alert_preference") if preference_row else None,
            "onboarding_completed_at": preference_row.get("onboarding_completed_at") if preference_row else None,
        }

    def save_onboarding(self, email: str, tracked_token_ids: list[str], alert_preference: str) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return None
        user = self.get_or_create_user(email)
        if user is None:
            return None

        client.table("user_preferences").upsert(
            {
                "user_id": user["id"],
                "alert_preference": alert_preference,
                "onboarding_completed_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            on_conflict="user_id",
        ).execute()
        return {
            "user_id": user["id"],
            "email": user["email"],
            "tracked_token_ids": tracked_token_ids,
            "alert_preference": alert_preference,
        }
