from app.repositories.supabase_client import get_supabase_client


class NotificationRepository:
    def insert_log(self, payload: dict) -> dict | None:
        client = get_supabase_client()
        if client is None:
            return payload
        response = client.table("notification_logs").insert(payload).execute()
        return response.data[0] if response.data else None

