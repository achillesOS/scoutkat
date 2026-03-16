from __future__ import annotations

from abc import ABC, abstractmethod

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings


class CacheService(ABC):
    @abstractmethod
    def get(self, key: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        raise NotImplementedError


class NullCacheService(CacheService):
    def get(self, key: str) -> str | None:
        return None

    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        return None

    def delete(self, key: str) -> None:
        return None


class RedisCacheService(CacheService):
    def __init__(self) -> None:
        self._client = Redis.from_url(get_settings().redis_url, decode_responses=True, socket_timeout=1)

    def get(self, key: str) -> str | None:
        try:
            return self._client.get(key)
        except RedisError:
            return None

    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        try:
            self._client.setex(key, ttl_seconds, value)
        except RedisError:
            return None

    def delete(self, key: str) -> None:
        try:
            self._client.delete(key)
        except RedisError:
            return None
