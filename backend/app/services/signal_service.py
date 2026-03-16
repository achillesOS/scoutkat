from app.core.config import get_settings
from app.providers.base import GrokProvider, TelegramProvider
from app.repositories.signal_repository import SignalRepository
from app.repositories.token_repository import TokenRepository
from app.schemas.signal import ExplanationCard
from app.services.explanation_service import ExplanationService
from app.services.signal_detection_service import SignalDetectionService


class SignalService:
    def __init__(
        self,
        signal_repository: SignalRepository,
        token_repository: TokenRepository,
        grok_provider: GrokProvider,
        telegram_provider: TelegramProvider,
    ) -> None:
        settings = get_settings()
        self.signal_repository = signal_repository
        self.token_repository = token_repository
        self.grok_provider = grok_provider
        self.telegram_provider = telegram_provider
        self.explanation_service = ExplanationService(
            prompt_path=settings.explanation_prompt_path,
            schema_path=settings.explanation_schema_path,
        )
        self.signal_detection_service = SignalDetectionService()

    def list_signals(self) -> list[dict]:
        return self.signal_repository.list_signals()

    def get_signal(self, signal_id: str) -> dict | None:
        return self.signal_repository.get_signal(signal_id)

    def validate_explanation(self, payload: dict) -> ExplanationCard:
        validated = self.explanation_service.validate_output(payload)
        return ExplanationCard.model_validate(validated.model_dump())

