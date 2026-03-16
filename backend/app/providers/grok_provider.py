from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from string import Template
from typing import Any

import httpx

from app.core.config import get_settings
from app.providers.base import GrokProvider
from app.schemas.grok import GrokAttentionExtraction, GrokNormalizedAttention
from app.services.cache_service import CacheService


class GrokXProvider(GrokProvider):
    def __init__(self, cache_service: CacheService) -> None:
        self.settings = get_settings()
        self.cache_service = cache_service
        self.system_prompt = self.settings.grok_system_prompt_path.read_text()
        self.user_prompt_template = Template(self.settings.grok_user_prompt_path.read_text())

    async def fetch_social_summary(self, token_symbol: str, time_window: str) -> dict[str, Any]:
        cache_key = self._cache_key(token_symbol, time_window)
        cached = self.cache_service.get(cache_key)
        if cached:
            return json.loads(cached)

        raw_attempts: list[dict[str, Any]] = []
        try:
            raw_response = await self._call_with_retry(
                token_symbol=token_symbol,
                time_window=time_window,
                repair_payload=None,
            )
            raw_attempts.append(raw_response)
            validated = self._validate_response_content(raw_response, token_symbol, time_window)
        except Exception as exc:
            try:
                repaired_response = await self._repair_invalid_response(
                    token_symbol=token_symbol,
                    time_window=time_window,
                    invalid_payload=raw_attempts[-1] if raw_attempts else None,
                    error_message=str(exc),
                )
                raw_attempts.append(repaired_response)
                validated = self._validate_response_content(repaired_response, token_symbol, time_window)
            except Exception as repair_exc:
                incomplete = self._build_incomplete_snapshot(
                    token_symbol=token_symbol,
                    time_window=time_window,
                    raw_attempts=raw_attempts,
                    validation_error=f"{exc} | repair_failed: {repair_exc}",
                )
                self.cache_service.setex(cache_key, self.settings.grok_cache_bucket_minutes * 60, json.dumps(incomplete))
                return incomplete

        normalized = self._normalize_payload(validated, raw_attempts[-1])
        self.cache_service.setex(cache_key, self.settings.grok_cache_bucket_minutes * 60, json.dumps(normalized))
        return normalized

    async def _call_with_retry(
        self,
        *,
        token_symbol: str,
        time_window: str,
        repair_payload: dict[str, Any] | None,
    ) -> dict[str, Any]:
        delay = 1.0
        last_error: Exception | None = None
        for attempt in range(1, self.settings.grok_max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.settings.grok_timeout_seconds) as client:
                    response = await client.post(
                        self.settings.grok_api_url or "",
                        headers={
                            "Authorization": f"Bearer {self.settings.grok_api_key}",
                            "Content-Type": "application/json",
                        },
                        json=self._build_request_payload(token_symbol, time_window, repair_payload),
                    )
                    response.raise_for_status()
                    return response.json()
            except Exception as exc:
                last_error = exc
                if attempt == self.settings.grok_max_retries:
                    break
                await asyncio.sleep(delay)
                delay *= 2
        assert last_error is not None
        raise last_error

    def _build_request_payload(
        self,
        token_symbol: str,
        time_window: str,
        repair_payload: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if repair_payload is not None:
            return {
                "model": _normalize_model_name(self.settings.grok_model),
                "temperature": 0,
                "messages": [
                    {
                        "role": "system",
                        "content": "Repair invalid JSON into valid JSON only. Preserve original meaning and satisfy the required schema exactly.",
                    },
                    {
                        "role": "user",
                        "content": json.dumps(repair_payload),
                    },
                ],
            }

        user_prompt = self.user_prompt_template.safe_substitute(
            TOKEN_SYMBOL=token_symbol,
            TIME_WINDOW=time_window,
        )
        return {
            "model": _normalize_model_name(self.settings.grok_model),
            "temperature": 0,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

    async def _repair_invalid_response(
        self,
        *,
        token_symbol: str,
        time_window: str,
        invalid_payload: dict[str, Any] | None,
        error_message: str,
    ) -> dict[str, Any]:
        repair_payload = {
            "token_symbol": token_symbol,
            "time_window": time_window,
            "error": error_message,
            "invalid_provider_response": invalid_payload,
        }
        return await self._call_with_retry(
            token_symbol=token_symbol,
            time_window=time_window,
            repair_payload=repair_payload,
        )

    def _validate_response_content(
        self,
        raw_response: dict[str, Any],
        token_symbol: str,
        time_window: str,
    ) -> GrokAttentionExtraction:
        content = _strip_code_fences(self._extract_content(raw_response))
        payload = json.loads(content)
        validated = GrokAttentionExtraction.model_validate(payload)
        if validated.token_symbol.upper() != token_symbol.upper():
            validated.token_symbol = token_symbol.upper()
        if validated.time_window != time_window:
            validated.time_window = time_window
        return validated

    def _extract_content(self, raw_response: dict[str, Any]) -> str:
        choices = raw_response.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                text_chunks = [item.get("text", "") for item in content if isinstance(item, dict)]
                return "".join(text_chunks)
        output = raw_response.get("output", [])
        if output:
            first = output[0]
            content = first.get("content", [])
            if isinstance(content, list):
                text_chunks = [item.get("text", "") for item in content if isinstance(item, dict)]
                return "".join(text_chunks)
        raise ValueError("No response content returned by Grok")

    def _normalize_payload(
        self,
        validated: GrokAttentionExtraction,
        raw_response: dict[str, Any],
    ) -> dict[str, Any]:
        normalized = GrokNormalizedAttention(
            token_symbol=validated.token_symbol.upper(),
            time_window=validated.time_window,
            mentions_1h=validated.mentions_1h_estimate,
            mentions_6h=validated.mentions_6h_estimate,
            unique_authors_1h=validated.unique_authors_1h_estimate,
            mention_acceleration=_map_acceleration(validated.attention_acceleration),
            retail_breadth=_map_level(validated.retail_breadth_level),
            expert_presence=_map_level(validated.expert_presence_level),
            narrative_novelty=validated.narrative_novelty,
            signal_hint=validated.signal_hint.likely_pattern,
            confidence=validated.confidence,
            snapshot_incomplete=False,
            raw_provider_response=raw_response,
            validated_payload=validated.model_dump(),
            validation_error=None,
        )
        payload = normalized.model_dump()
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        return payload

    def _build_incomplete_snapshot(
        self,
        *,
        token_symbol: str,
        time_window: str,
        raw_attempts: list[dict[str, Any]],
        validation_error: str,
    ) -> dict[str, Any]:
        return GrokNormalizedAttention(
            token_symbol=token_symbol.upper(),
            time_window=time_window,
            mentions_1h=0,
            mentions_6h=0,
            unique_authors_1h=0,
            mention_acceleration=0.0,
            retail_breadth=0.0,
            expert_presence=0.0,
            narrative_novelty=0.0,
            signal_hint="unclear",
            confidence=0.0,
            snapshot_incomplete=True,
            raw_provider_response={"attempts": raw_attempts, "error": validation_error},
            validated_payload=None,
            validation_error=validation_error,
        ).model_dump() | {"timestamp": datetime.now(timezone.utc).isoformat()}

    def _cache_key(self, token_symbol: str, time_window: str) -> str:
        now = datetime.now(timezone.utc)
        bucket_minutes = max(self.settings.grok_cache_bucket_minutes, 1)
        bucket_start = now.replace(
            minute=(now.minute // bucket_minutes) * bucket_minutes,
            second=0,
            microsecond=0,
        )
        return f"scoutkat:grok:{token_symbol.upper()}:{time_window}:{bucket_start.isoformat()}"


class MockGrokProvider(GrokProvider):
    async def fetch_social_summary(self, token_symbol: str, time_window: str) -> dict[str, Any]:
        return {
            "token_symbol": token_symbol,
            "time_window": time_window,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mentions_1h": 182,
            "mentions_6h": 640,
            "unique_authors_1h": 94,
            "mention_acceleration": 0.75,
            "retail_breadth": 0.72,
            "expert_presence": 0.31,
            "narrative_novelty": 0.58,
            "signal_hint": "narrative_ignition",
            "confidence": 0.72,
            "snapshot_incomplete": False,
            "raw_provider_response": {"provider": "mock", "query_mode": "shortlisted_only"},
            "validated_payload": None,
            "validation_error": None,
        }


def _map_acceleration(value: str) -> float:
    return {
        "falling": 0.1,
        "flat": 0.3,
        "rising": 0.65,
        "spiking": 1.0,
    }.get(value, 0.2)


def _map_level(value: str) -> float:
    return {
        "low": 0.2,
        "medium": 0.55,
        "high": 0.9,
    }.get(value, 0.2)


def _normalize_model_name(value: str) -> str:
    normalized = value.strip()
    replacements = {
        "grok-4.1-fast-non-reasoning": "grok-4-1-fast-non-reasoning",
        "grok-4.1-fast-reasoning": "grok-4-1-fast-reasoning",
    }
    return replacements.get(normalized, normalized)


def _strip_code_fences(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return stripped
