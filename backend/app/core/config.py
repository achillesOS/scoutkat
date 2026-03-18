from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    hyperliquid_api_url: str = "https://api.hyperliquid.xyz"
    grok_api_url: str | None = None
    grok_api_key: str | None = None
    grok_model: str = "grok-4-1-fast-non-reasoning"
    grok_timeout_seconds: int = 20
    grok_max_retries: int = 3
    grok_cache_bucket_minutes: int = 30
    telegram_bot_token: str | None = None
    telegram_default_chat_id: str | None = None
    social_refresh_minutes: int = 30
    alert_cooldown_minutes: int = 90
    enable_scheduler: bool = Field(default=True)
    default_user_email: str = "demo@scoutkat.local"
    tracked_symbols: str = "BTC,ETH,SOL,HYPE,XRP,DOGE,BNB,SUI,ADA,AVAX,LINK"
    hourly_digest_symbols: str = "BTC,ETH,SOL,HYPE,BNB"
    trade_enabled: bool = False
    trade_executor_symbols: str = "BTC,SOL"
    trade_signal_confirmations: int = 1
    trade_execution_grace_minutes: int = 59
    trade_hold_hours: int = 6
    trade_default_notional_usd: float = 10.0
    trade_notional_usd_map: str = "BTC:10,SOL:10"
    trade_default_leverage: float = 5.0
    trade_leverage_map: str = "BTC:10,SOL:5"
    trade_margin_mode: str = "isolated"
    trade_max_open_positions: int = 2
    trade_stop_loss_pct: float = 0.015
    hl_master_wallet_address: str | None = None
    hl_agent_private_key: str | None = None

    @property
    def scoring_weights_path(self) -> Path:
        return BASE_DIR / "app" / "scoring" / "weights.json"

    @property
    def thresholds_path(self) -> Path:
        return BASE_DIR / "app" / "scoring" / "thresholds.json"

    @property
    def explanation_schema_path(self) -> Path:
        return (
            BASE_DIR / "app" / "prompts" / "explanations" / "v1" / "schema.json"
        )

    @property
    def explanation_prompt_path(self) -> Path:
        return BASE_DIR / "app" / "prompts" / "explanations" / "v1" / "system.txt"

    @property
    def grok_system_prompt_path(self) -> Path:
        return BASE_DIR / "app" / "prompts" / "grok_system.txt"

    @property
    def grok_user_prompt_path(self) -> Path:
        return BASE_DIR / "app" / "prompts" / "grok_user.txt"

    @property
    def tracked_symbol_list(self) -> list[str]:
        return [symbol.strip().upper() for symbol in self.tracked_symbols.split(",") if symbol.strip()]

    @property
    def hourly_digest_symbol_list(self) -> list[str]:
        return [symbol.strip().upper() for symbol in self.hourly_digest_symbols.split(",") if symbol.strip()]

    @property
    def trade_executor_symbol_list(self) -> list[str]:
        return [symbol.strip().upper() for symbol in self.trade_executor_symbols.split(",") if symbol.strip()]

    @property
    def trade_leverage_by_symbol(self) -> dict[str, float]:
        return _parse_float_map(self.trade_leverage_map)

    @property
    def trade_notional_usd_by_symbol(self) -> dict[str, float]:
        return _parse_float_map(self.trade_notional_usd_map)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _parse_float_map(raw: str) -> dict[str, float]:
    parsed: dict[str, float] = {}
    for chunk in raw.split(","):
        item = chunk.strip()
        if not item or ":" not in item:
            continue
        key, value = item.split(":", 1)
        try:
            parsed[key.strip().upper()] = float(value.strip())
        except ValueError:
            continue
    return parsed
