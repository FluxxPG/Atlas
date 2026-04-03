import json
from datetime import datetime, timezone

from redis.asyncio import Redis

from worker.config import settings


class RealtimePublisher:
    def __init__(self) -> None:
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    async def publish(self, event: str, payload: dict):
        await self.redis.publish(
            "platform:events",
            json.dumps(
                {
                    "channel": "platform",
                    "event": event,
                    "payload": payload,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
        )


realtime_publisher = RealtimePublisher()

