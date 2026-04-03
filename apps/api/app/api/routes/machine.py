from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ApiKeyPrincipal, get_api_key_principal, require_api_scopes
from app.db.session import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.domain import ExportRequest, SearchResponse
from app.services.company import get_company, get_company_by_slug
from app.services.exports import create_export
from app.services.search import semantic_search
from app.services.tenancy import record_usage
from app.utils.serializers import serialize_company, serialize_company_detail

router = APIRouter(prefix="/machine")


@router.get("/search", response_model=SearchResponse)
async def machine_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=20, ge=1, le=100),
    principal: ApiKeyPrincipal = Depends(require_api_scopes("search:read")),
    db: AsyncSession = Depends(get_db),
):
    results, suggested_filters, applied_filters = await semantic_search(db, q, limit=limit)
    await record_usage(
        db,
        principal.organization_id,
        "search",
        quantity=1,
        context={"channel": "machine", "query": q, "result_count": len(results)},
    )
    return SearchResponse(
        query=q,
        total=len(results),
        results=[serialize_company(item) for item in results],
        suggested_filters=suggested_filters,
        applied_filters=applied_filters,
    )


@router.get("/company/{company_id}")
async def machine_company_detail(
    company_id: str,
    _: ApiKeyPrincipal = Depends(require_api_scopes("company:read")),
    db: AsyncSession = Depends(get_db),
):
    company, relationships = await get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return serialize_company_detail(company, relationships)


@router.get("/company/slug/{slug}")
async def machine_company_detail_by_slug(
    slug: str,
    _: ApiKeyPrincipal = Depends(require_api_scopes("company:read")),
    db: AsyncSession = Depends(get_db),
):
    company, relationships = await get_company_by_slug(db, slug)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return serialize_company_detail(company, relationships)


@router.post("/exports", response_model=PaginatedResponse)
async def machine_export_request(
    payload: ExportRequest,
    principal: ApiKeyPrincipal = Depends(require_api_scopes("exports:create")),
    db: AsyncSession = Depends(get_db),
):
    export = await create_export(db, payload.export_type, payload.filters, payload.user_id)
    await record_usage(db, principal.organization_id, "export", quantity=1, context={"channel": "machine"})
    return PaginatedResponse(
        items=[
            {
                "id": str(export.id),
                "status": export.status,
                "export_type": export.export_type,
                "filters": export.filters,
                "file_url": export.file_url,
            }
        ],
        total=1,
    )


@router.get("/me")
async def machine_identity(principal: ApiKeyPrincipal = Depends(get_api_key_principal)):
    return {
        "id": principal.id,
        "organization_id": principal.organization_id,
        "name": principal.name,
        "key_prefix": principal.key_prefix,
        "scopes": principal.scopes,
    }
