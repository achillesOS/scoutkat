from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.core.config import get_settings
from app.providers.base import TelegramProvider
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository


class NotificationService:
    def __init__(
        self,
        telegram_provider: TelegramProvider,
        notification_repository: NotificationRepository,
        user_repository: UserRepository,
    ) -> None:
        self.settings = get_settings()
        self.telegram_provider = telegram_provider
        self.notification_repository = notification_repository
        self.user_repository = user_repository

    async def notify_signal(self, signal_event: dict, token_symbol: str, explanation: dict) -> dict | None:
        default_user = self.user_repository.get_or_create_default_user()
        if not default_user:
            return None

        chat_id = default_user.get("telegram_chat_id") or self.settings.telegram_default_chat_id
        status = "skipped"
        provider_result: dict | None = None

        if chat_id:
            message = self._format_message(token_symbol, signal_event, explanation)
            provider_result = await self.telegram_provider.send_signal_alert(chat_id, message)
            status = str(provider_result.get("status", "sent"))
        else:
            status = "skipped_missing_chat_id"

        return self.notification_repository.insert_log(
            {
                "user_id": default_user["id"],
                "signal_event_id": signal_event["id"],
                "channel": "telegram",
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "delivery_status": status,
            }
        )

    async def send_hourly_digest(self, digest_rows: list[dict]) -> dict | None:
        default_user = self.user_repository.get_or_create_default_user()
        chat_id = self.settings.telegram_default_chat_id
        if default_user:
            chat_id = default_user.get("telegram_chat_id") or chat_id
        if not chat_id:
            return {"status": "skipped_missing_chat_id"}

        message = self._format_hourly_digest_message(digest_rows)
        return await self.telegram_provider.send_signal_alert(chat_id, message)

    def _format_message(self, token_symbol: str, signal_event: dict, explanation: dict) -> str:
        return "\n".join(
            [
                f"Scoutkat alert: {token_symbol}",
                f"Type: {signal_event['signal_type']}",
                f"Score: {signal_event['signal_score']}",
                f"Confidence: {round(float(signal_event['confidence']) * 100)}%",
                f"Why now: {explanation.get('why_now', '')}",
                f"Action: {explanation.get('suggested_action', '')}",
            ]
        )

    def _format_hourly_digest_message(self, digest_rows: list[dict]) -> str:
        now_local = datetime.now(ZoneInfo("Asia/Shanghai"))
        lines = [
            "Scoutkat 每小时背离播报",
            f"播报时间: {now_local.strftime('%Y-%m-%d %H:%M:%S CST')}",
            "",
        ]
        for row in digest_rows:
            if row.get("status") != "ok":
                lines.append(f"【{row['symbol']}】")
                lines.append("状态: unavailable")
                lines.append(f"原因: {row.get('reason', 'missing latest snapshot')}")
                lines.append("")
                continue

            confidence = round(float(row["confidence"]) * 100)
            lines.append(f"【{row['symbol']}】{_signal_badge(str(row['signal_type']))}")
            lines.append(f"价格: ${_format_price(float(row.get('price', 0.0)))}")
            lines.append(f"信号: {_humanize_signal_type(str(row['signal_type']))}")
            lines.append(f"强度: {round(float(row['signal_score']), 1)}")
            lines.append(f"置信度: {confidence}%")
            lines.append(f"数据: {_humanize_mode(str(row.get('mode', 'live')))}")
            if row.get("market_timestamp"):
                lines.append(f"行情时间: {_format_market_timestamp(str(row['market_timestamp']))}")
            lines.append(f"说明: {row['why_now']}")
            if row.get("warning"):
                lines.append(f"提示: 因 {row['warning']}，本次使用最近一次已验证快照")
            lines.append("")
        return "\n".join(lines)


def _humanize_signal_type(value: str) -> str:
    mapping = {
        "hidden_accumulation": "Hidden Accumulation / 隐性吸筹",
        "narrative_ignition": "Narrative Ignition / 叙事启动",
        "retail_trap": "Retail Trap / 散户陷阱",
        "neutral": "Neutral / 中性",
    }
    return mapping.get(value, value.replace("_", " ").title())


def _format_price(value: float) -> str:
    if value >= 1000:
        return f"{value:,.2f}"
    if value >= 1:
        return f"{value:,.3f}"
    return f"{value:,.6f}"


def _signal_badge(value: str) -> str:
    mapping = {
        "hidden_accumulation": " [偏多观察]",
        "narrative_ignition": " [启动观察]",
        "retail_trap": " [风险警示]",
        "neutral": " [中性]",
    }
    return mapping.get(value, "")


def _humanize_mode(value: str) -> str:
    return "live 实时验证" if value == "live" else "fallback 最近快照"


def _format_market_timestamp(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    localized = parsed.astimezone(ZoneInfo("Asia/Shanghai"))
    return localized.strftime("%Y-%m-%d %H:%M:%S CST")
