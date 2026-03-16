from datetime import datetime, timezone

from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.repositories.watchlist_repository import WatchlistRepository


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: TokenRepository,
        watchlist_repository: WatchlistRepository,
    ) -> None:
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.watchlist_repository = watchlist_repository

    def get_profile(self, email: str) -> dict | None:
        return self.user_repository.get_profile(email)

    def save_onboarding(self, email: str, tracked_symbols: list[str], alert_preference: str) -> dict | None:
        tokens = self.token_repository.get_by_symbols(tracked_symbols)
        token_ids = [token["id"] for token in tokens]
        saved = self.user_repository.save_onboarding(email, token_ids, alert_preference)
        if saved is None:
            return None
        self.watchlist_repository.replace(token_ids, email)
        profile = self.user_repository.get_profile(email)
        if profile and profile.get("onboarding_completed_at") is None:
            profile["onboarding_completed_at"] = datetime.now(timezone.utc).isoformat()
        return profile
