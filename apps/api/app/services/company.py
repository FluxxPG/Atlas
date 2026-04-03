from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entities import Company, Relationship


async def list_companies(
    db: AsyncSession,
    limit: int = 20,
    country: str | None = None,
    industry: str | None = None,
    min_opportunity_score: float | None = None,
) -> list[Company]:
    statement = select(Company)
    if country:
        statement = statement.where(Company.country == country)
    if industry:
        statement = statement.where(Company.industry == industry)
    if min_opportunity_score is not None:
        statement = statement.where(Company.opportunity_score >= min_opportunity_score)

    result = await db.execute(statement.order_by(desc(Company.opportunity_score)).limit(limit))
    return result.scalars().all()


async def get_company(db: AsyncSession, company_id: str) -> tuple[Company | None, list[Relationship]]:
    result = await db.execute(
        select(Company)
        .where(Company.id == company_id)
        .options(selectinload(Company.signals), selectinload(Company.opportunities), selectinload(Company.sources))
    )
    company = result.scalar_one_or_none()
    if not company:
        return None, []

    relationships = await db.execute(
        select(Relationship).where(
            (Relationship.source_company_id == company.id) | (Relationship.target_company_id == company.id)
        )
    )
    return company, relationships.scalars().all()


async def get_company_by_slug(db: AsyncSession, slug: str) -> tuple[Company | None, list[Relationship]]:
    result = await db.execute(
        select(Company)
        .where(Company.slug == slug)
        .options(selectinload(Company.signals), selectinload(Company.opportunities), selectinload(Company.sources))
    )
    company = result.scalar_one_or_none()
    if not company:
        return None, []

    relationships = await db.execute(
        select(Relationship).where(
            (Relationship.source_company_id == company.id) | (Relationship.target_company_id == company.id)
        )
    )
    return company, relationships.scalars().all()
