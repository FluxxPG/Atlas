import csv
import json
from io import StringIO
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Company, Export, SavedLead


async def create_export(db: AsyncSession, export_type: str, filters: dict, user_id=None) -> Export:
    export = Export(
        id=uuid4(),
        user_id=user_id,
        export_type=export_type,
        filters=filters,
        file_url=f"/api/v1/exports/{export_type}/{uuid4()}",
        status="ready",
    )
    db.add(export)
    await db.commit()
    await db.refresh(export)
    return export


async def build_export_preview(db: AsyncSession, export_type: str) -> str:
    companies = (await db.execute(select(Company).limit(25))).scalars().all()
    rows = [
        {
            "name": item.name,
            "industry": item.industry,
            "city": item.city,
            "country": item.country,
            "website": item.website,
            "opportunity_score": float(item.opportunity_score),
        }
        for item in companies
    ]
    if export_type == "json":
        return json.dumps(rows, indent=2)
    if export_type == "csv":
        buffer = StringIO()
        writer = csv.DictWriter(buffer, fieldnames=rows[0].keys() if rows else ["name"])
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue()
    if export_type == "excel":
        return "Excel export queued. Use CSV payload as the workbook source in downstream processors."
    return ""


async def save_lead(db: AsyncSession, user_id, company_id, notes: str | None):
    entity = SavedLead(user_id=user_id, company_id=company_id, notes=notes)
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity

