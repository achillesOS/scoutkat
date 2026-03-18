from functools import lru_cache

from app.core.config import get_settings
from app.providers.grok_provider import DisabledGrokProvider, GrokProvider, GrokXProvider
from app.providers.hyperliquid_provider import HyperliquidHttpProvider, HyperliquidProvider, UnavailableHyperliquidProvider
from app.providers.hyperliquid_trade_provider import HyperliquidTradeProvider
from app.providers.telegram_provider import NoopTelegramProvider, TelegramBotProvider, TelegramProvider
from app.providers.base import TradeExecutionProvider
from app.repositories.hourly_digest_repository import HourlyDigestRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.score_repository import ScoreRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.signal_repository import SignalRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.trade_repository import TradeRepository
from app.repositories.user_repository import UserRepository
from app.repositories.watchlist_repository import WatchlistRepository
from app.repositories.x_attention_repository import XAttentionRepository
from app.services.cache_service import CacheService, NullCacheService, RedisCacheService
from app.services.hourly_digest_service import HourlyDigestService
from app.services.market_ingestion_service import MarketIngestionService
from app.services.notification_service import NotificationService
from app.services.scoring_pipeline_service import ScoringPipelineService
from app.services.signal_pipeline_service import SignalPipelineService
from app.services.signal_service import SignalService
from app.services.token_service import TokenService
from app.services.trade_executor_service import TradeExecutorService
from app.services.user_service import UserService
from app.services.watchlist_service import WatchlistService


@lru_cache
def get_hyperliquid_provider() -> HyperliquidProvider:
    return HyperliquidHttpProvider() if get_settings().hyperliquid_api_url else UnavailableHyperliquidProvider()


@lru_cache
def get_grok_provider() -> GrokProvider:
    settings = get_settings()
    return GrokXProvider(get_cache_service()) if settings.grok_api_url and settings.grok_api_key else DisabledGrokProvider()


@lru_cache
def get_telegram_provider() -> TelegramProvider:
    return TelegramBotProvider() if get_settings().telegram_bot_token else NoopTelegramProvider()


@lru_cache
def get_trade_execution_provider() -> TradeExecutionProvider:
    return HyperliquidTradeProvider()


@lru_cache
def get_token_repository() -> TokenRepository:
    return TokenRepository()


@lru_cache
def get_signal_repository() -> SignalRepository:
    return SignalRepository()


@lru_cache
def get_watchlist_repository() -> WatchlistRepository:
    return WatchlistRepository()


@lru_cache
def get_snapshot_repository() -> SnapshotRepository:
    return SnapshotRepository()


@lru_cache
def get_x_attention_repository() -> XAttentionRepository:
    return XAttentionRepository()


@lru_cache
def get_score_repository() -> ScoreRepository:
    return ScoreRepository()


@lru_cache
def get_user_repository() -> UserRepository:
    return UserRepository()


@lru_cache
def get_notification_repository() -> NotificationRepository:
    return NotificationRepository()


@lru_cache
def get_hourly_digest_repository() -> HourlyDigestRepository:
    return HourlyDigestRepository()


@lru_cache
def get_trade_repository() -> TradeRepository:
    return TradeRepository()


@lru_cache
def get_cache_service() -> CacheService:
    settings = get_settings()
    return RedisCacheService() if settings.redis_url else NullCacheService()


@lru_cache
def get_token_service() -> TokenService:
    return TokenService(
        token_repository=get_token_repository(),
        signal_repository=get_signal_repository(),
        snapshot_repository=get_snapshot_repository(),
        x_attention_repository=get_x_attention_repository(),
        score_repository=get_score_repository(),
        watchlist_repository=get_watchlist_repository(),
    )


@lru_cache
def get_signal_service() -> SignalService:
    return SignalService(
        signal_repository=get_signal_repository(),
        token_repository=get_token_repository(),
        grok_provider=get_grok_provider(),
        telegram_provider=get_telegram_provider(),
    )


@lru_cache
def get_signal_pipeline_service() -> SignalPipelineService:
    return SignalPipelineService(
        hyperliquid_provider=get_hyperliquid_provider(),
        grok_provider=get_grok_provider(),
    )


@lru_cache
def get_market_ingestion_service() -> MarketIngestionService:
    return MarketIngestionService(
        token_repository=get_token_repository(),
        snapshot_repository=get_snapshot_repository(),
        hyperliquid_provider=get_hyperliquid_provider(),
    )


@lru_cache
def get_notification_service() -> NotificationService:
    return NotificationService(
        telegram_provider=get_telegram_provider(),
        notification_repository=get_notification_repository(),
        user_repository=get_user_repository(),
    )


@lru_cache
def get_scoring_pipeline_service() -> ScoringPipelineService:
    return ScoringPipelineService(
        token_repository=get_token_repository(),
        watchlist_repository=get_watchlist_repository(),
        snapshot_repository=get_snapshot_repository(),
        x_attention_repository=get_x_attention_repository(),
        score_repository=get_score_repository(),
        signal_repository=get_signal_repository(),
        grok_provider=get_grok_provider(),
        cache_service=get_cache_service(),
        notification_service=get_notification_service(),
    )


@lru_cache
def get_hourly_digest_service() -> HourlyDigestService:
    return HourlyDigestService(
        token_repository=get_token_repository(),
        hourly_digest_repository=get_hourly_digest_repository(),
        snapshot_repository=get_snapshot_repository(),
        score_repository=get_score_repository(),
        market_ingestion_service=get_market_ingestion_service(),
        scoring_pipeline_service=get_scoring_pipeline_service(),
        notification_service=get_notification_service(),
    )


@lru_cache
def get_trade_executor_service() -> TradeExecutorService:
    return TradeExecutorService(
        token_repository=get_token_repository(),
        hourly_digest_repository=get_hourly_digest_repository(),
        trade_repository=get_trade_repository(),
        trade_provider=get_trade_execution_provider(),
    )


@lru_cache
def get_watchlist_service() -> WatchlistService:
    return WatchlistService(
        watchlist_repository=get_watchlist_repository(),
        token_repository=get_token_repository(),
    )


@lru_cache
def get_user_service() -> UserService:
    return UserService(
        user_repository=get_user_repository(),
        token_repository=get_token_repository(),
        watchlist_repository=get_watchlist_repository(),
    )
