from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.entities import Opportunity
from app.schemas.common import PaginatedResponse
from app.utils.serializers import serialize_opportunity

router = APIRouter(prefix="/opportunities")


@router.get("", response_model=PaginatedResponse)
async def opportunities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Opportunity).order_by(Opportunity.confidence.desc()).limit(50))
    items = result.scalars().all()
    return PaginatedResponse(items=[serialize_opportunity(item) for item in items], total=len(items))

