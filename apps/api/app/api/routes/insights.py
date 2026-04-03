from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.domain import DashboardResponse, InsightResponse
from app.services.insights import build_dashboard, build_insights

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(db: AsyncSession = Depends(get_db)):
    return await build_dashboard(db)


@router.get("/insights", response_model=InsightResponse)
async def insights(db: AsyncSession = Depends(get_db)):
    return await build_insights(db)

