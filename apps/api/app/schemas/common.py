from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(APIModel):
    items: list[Any]
    total: int


class RealtimeEvent(APIModel):
    event: str
    payload: dict[str, Any]
    timestamp: datetime


class MetricCard(APIModel):
    label: str
    value: float | int | str
    delta: float | None = None
    meta: dict[str, Any] = {}


class RelationshipEdge(APIModel):
    id: UUID
    relationship_type: str
    weight: float
    metadata: dict[str, Any]

