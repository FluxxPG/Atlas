from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, rate_limit
from app.db.session import get_db
from app.schemas.domain import SearchResponse
from app.services.search import semantic_search
from app.services.tenancy import get_workspace_overview, record_usage
from app.utils.serializers import serialize_company

router = APIRouter(prefix="/search")


@router.get("", response_model=SearchResponse)
async def search_companies(q: str = Query(..., min_length=2), db: AsyncSession = Depends(get_db)):
    results, suggested_filters, applied_filters = await semantic_search(
        db,
        q,
        country=None,
        industry=None,
        min_opportunity_score=None,
        min_growth_score=None,
    )
    return SearchResponse(
        query=q,
        total=len(results),
        results=[serialize_company(item) for item in results],
        suggested_filters=suggested_filters,
        applied_filters=applied_filters,
    )


@router.get("/advanced", response_model=SearchResponse)
async def advanced_search(
    q: str = Query(..., min_length=2),
    limit: int = Query(default=20, ge=1, le=100),
    country: str | None = None,
    industry: str | None = None,
    min_opportunity_score: float | None = None,
    min_growth_score: float | None = None,
    sort_by: str = Query(default="opportunity", pattern="^(opportunity|growth)$"),
    _: None = Depends(rate_limit),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    results, suggested_filters, applied_filters = await semantic_search(
        db,
        q,
        limit=limit,
        country=country,
        industry=industry,
        min_opportunity_score=min_opportunity_score,
        min_growth_score=min_growth_score,
        sort_by=sort_by,
    )
    overview = await get_workspace_overview(db, user)
    default_org = overview.get("default_organization")
    if default_org:
        await record_usage(
            db,
            default_org["id"],
            "search",
            quantity=1,
            context={"query": q, "result_count": len(results)},
        )
    return SearchResponse(
        query=q,
        total=len(results),
        results=[serialize_company(item) for item in results],
        suggested_filters=suggested_filters,
        applied_filters=applied_filters,
    )
