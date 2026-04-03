import json

from redis.asyncio import Redis

from worker.config import settings


class RedisQueue:
    def __init__(self) -> None:
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    async def pop(self, queue_name: str, timeout: int = 5):
        item = await self.redis.blpop(queue_name, timeout=timeout)
        if not item:
            return None
        _, payload = item
        return json.loads(payload)

    async def push(self, queue_name: str, payload: dict):
        await self.redis.rpush(queue_name, json.dumps(payload))


redis_queue = RedisQueue()
