import json
from typing import Any

from redis.asyncio import Redis

from app.core.config import settings


class QueueClient:
    def __init__(self) -> None:
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    async def enqueue(self, queue_name: str, payload: dict[str, Any]) -> None:
        await self.redis.rpush(queue_name, json.dumps(payload))

    async def size(self, queue_name: str) -> int:
        return await self.redis.llen(queue_name)


queue_client = QueueClient()

