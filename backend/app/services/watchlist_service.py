from app.repositories.token_repository import TokenRepository
from app.repositories.watchlist_repository import WatchlistRepository


class WatchlistService:
    def __init__(
        self,
        watchlist_repository: WatchlistRepository,
        token_repository: TokenRepository,
    ) -> None:
        self.watchlist_repository = watchlist_repository
        self.token_repository = token_repository

    def get_watchlist(self) -> list[dict]:
        token_ids = self.watchlist_repository.list_token_ids()
        return [
            token
            for token_id in token_ids
            if (token := self.token_repository.get_by_id(token_id)) is not None
        ]

    def add(self, token_id: str) -> list[dict]:
        self.watchlist_repository.add(token_id)
        return self.get_watchlist()

    def remove(self, token_id: str) -> list[dict]:
        self.watchlist_repository.remove(token_id)
        return self.get_watchlist()

