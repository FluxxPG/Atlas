from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.common import PaginatedResponse
from app.services.company import get_company, get_company_by_slug, list_companies
from app.utils.serializers import serialize_company, serialize_company_detail

router = APIRouter(prefix="/company")


@router.get("", response_model=PaginatedResponse)
async def companies(
    limit: int = Query(default=20, ge=1, le=100),
    country: str | None = None,
    industry: str | None = None,
    min_opportunity_score: float | None = None,
    db: AsyncSession = Depends(get_db),
):
    items = await list_companies(
        db,
        limit=limit,
        country=country,
        industry=industry,
        min_opportunity_score=min_opportunity_score,
    )
    return PaginatedResponse(items=[serialize_company(item) for item in items], total=len(items))


@router.get("/{company_id}")
async def company_detail(company_id: str, db: AsyncSession = Depends(get_db)):
    company, relationships = await get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return serialize_company_detail(company, relationships)


@router.get("/slug/{slug}")
async def company_detail_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    company, relationships = await get_company_by_slug(db, slug)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return serialize_company_detail(company, relationships)
