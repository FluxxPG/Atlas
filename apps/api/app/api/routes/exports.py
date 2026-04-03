from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import SavedLead
from app.schemas.common import PaginatedResponse
from app.schemas.domain import ExportRequest, ExportResponse, SaveLeadRequest
from app.services.exports import build_export_preview, create_export, save_lead
from app.services.tenancy import get_workspace_overview, record_usage

router = APIRouter()


@router.post("/exports", response_model=ExportResponse)
async def create_export_job(payload: ExportRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    export = await create_export(db, payload.export_type, payload.filters, payload.user_id)
    overview = await get_workspace_overview(db, user)
    default_org = overview.get("default_organization")
    if default_org:
        await record_usage(db, default_org["id"], "export", quantity=1, context={"type": payload.export_type})
    return ExportResponse.model_validate(export)


@router.get("/exports/{export_type}/preview", response_class=PlainTextResponse)
async def export_preview(export_type: str, db: AsyncSession = Depends(get_db)):
    if export_type not in {"csv", "json", "excel"}:
        raise HTTPException(status_code=400, detail="Unsupported export type")
    return await build_export_preview(db, export_type)


@router.post("/saved-leads")
async def save_lead_route(payload: SaveLeadRequest, db: AsyncSession = Depends(get_db)):
    lead = await save_lead(db, payload.user_id, payload.company_id, payload.notes)
    return {"id": str(lead.id), "status": "saved"}


@router.get("/saved-leads", response_model=PaginatedResponse)
async def list_saved_leads(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(SavedLead).order_by(SavedLead.created_at.desc()).limit(50))).scalars().all()
    items = [
        {
            "id": str(item.id),
            "user_id": str(item.user_id),
            "company_id": str(item.company_id),
            "notes": item.notes,
            "created_at": item.created_at.isoformat(),
        }
        for item in rows
    ]
    return PaginatedResponse(items=items, total=len(items))
