from app.repositories.signal_repository import SignalRepository
from app.repositories.token_repository import TokenRepository


class TokenService:
    def __init__(self, token_repository: TokenRepository, signal_repository: SignalRepository) -> None:
        self.token_repository = token_repository
        self.signal_repository = signal_repository

    def list_tokens(self) -> list[dict]:
        return self.token_repository.list_tokens()

    def get_token_detail(self, symbol: str) -> dict | None:
        token = self.token_repository.get_by_symbol(symbol)
        if not token:
            return None
        token["recent_signals"] = self.signal_repository.list_signals_for_token(token["id"])
        return token

