from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Opportunity, Signal


async def build_alerts(db: AsyncSession) -> list[dict]:
    signals = (await db.execute(select(Signal).order_by(Signal.created_at.desc()).limit(10))).scalars().all()
    opportunities = (
        await db.execute(select(Opportunity).order_by(Opportunity.created_at.desc()).limit(10))
    ).scalars().all()

    alerts = [
        {
            "id": str(item.id),
            "title": item.title,
            "category": "signal",
            "severity": item.severity,
            "description": item.description,
            "created_at": item.created_at.isoformat(),
        }
        for item in signals
    ]
    alerts.extend(
        [
            {
                "id": str(item.id),
                "title": item.title,
                "category": "opportunity",
                "severity": "medium" if float(item.confidence) < 80 else "high",
                "description": item.description,
                "created_at": item.created_at.isoformat(),
            }
            for item in opportunities
        ]
    )

    if not alerts:
        alerts.append(
            {
                "id": "fallback-alert",
                "title": "Realtime alerts are standing by",
                "category": "platform",
                "severity": "info",
                "description": "Alerts will populate once crawl and scoring jobs begin generating data.",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return alerts[:20]
