from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.common import PaginatedResponse
from app.services.alerts import build_alerts

router = APIRouter(prefix="/alerts")


@router.get("", response_model=PaginatedResponse)
async def alerts(db: AsyncSession = Depends(get_db)):
    items = await build_alerts(db)
    return PaginatedResponse(items=items, total=len(items))
