from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
import asyncio
import json

from fastapi import WebSocket
from redis.asyncio import Redis

from app.core.config import settings


class RealtimeManager:
    def __init__(self) -> None:
        self.connections: dict[str, set[WebSocket]] = defaultdict(set)
        self.redis: Redis | None = None
        self.pubsub = None
        self.listener_task = None

    async def connect(self) -> None:
        try:
            self.redis = Redis.from_url(settings.redis_url, decode_responses=True)
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe("platform:events")
            self.listener_task = asyncio.create_task(self._listen())
        except Exception:
            self.redis = None
            self.pubsub = None
            self.listener_task = None

    async def disconnect(self) -> None:
        if self.listener_task:
            self.listener_task.cancel()
        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()

    async def subscribe(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[channel].add(websocket)

    async def unsubscribe(self, channel: str, websocket: WebSocket) -> None:
        if websocket in self.connections[channel]:
            self.connections[channel].remove(websocket)

    async def broadcast(self, channel: str, event: str, payload: dict[str, Any]) -> None:
        message = {
            "event": event,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        for websocket in list(self.connections[channel]):
            await websocket.send_json(message)

    async def publish(self, event: str, payload: dict[str, Any]) -> None:
        if self.redis:
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

    async def _listen(self) -> None:
        async for message in self.pubsub.listen():
            if message["type"] != "message":
                continue
            payload = json.loads(message["data"])
            await self.broadcast(payload.get("channel", "platform"), payload["event"], payload["payload"])


realtime_manager = RealtimeManager()
