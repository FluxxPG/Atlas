from sqlalchemy import and_, desc, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Company
from app.services.embeddings import format_vector_literal, generate_embedding, rerank_companies


async def semantic_search(
    db: AsyncSession,
    query: str,
    limit: int = 20,
    country: str | None = None,
    industry: str | None = None,
    min_opportunity_score: float | None = None,
    min_growth_score: float | None = None,
    sort_by: str = "opportunity",
) -> tuple[list[Company], list[str], dict]:
    lowered = query.lower()
    heuristic_clauses, heuristic_sql = _build_heuristic_clauses(lowered)
    filters = _build_suggested_filters(lowered)

    applied_filters = {
        "country": country,
        "industry": industry,
        "min_opportunity_score": min_opportunity_score,
        "min_growth_score": min_growth_score,
        "sort_by": sort_by,
    }

    try:
        vector_ids = await _vector_ranked_ids(
            db,
            query=query,
            limit=limit,
            country=country,
            industry=industry,
            min_opportunity_score=min_opportunity_score,
            min_growth_score=min_growth_score,
            sort_by=sort_by,
            heuristic_sql=heuristic_sql,
        )
    except Exception:
        vector_ids = []

    text_match = or_(
        Company.name.ilike(f"%{query}%"),
        Company.industry.ilike(f"%{query}%"),
        Company.description.ilike(f"%{query}%"),
        Company.city.ilike(f"%{query}%"),
    )
    statement = select(Company).where(and_(*heuristic_clauses) if heuristic_clauses else text_match)

    if country:
        statement = statement.where(Company.country == country)
    if industry:
        statement = statement.where(Company.industry == industry)
    if min_opportunity_score is not None:
        statement = statement.where(Company.opportunity_score >= min_opportunity_score)
    if min_growth_score is not None:
        statement = statement.where(Company.growth_score >= min_growth_score)

    order_field = Company.opportunity_score if sort_by == "opportunity" else Company.growth_score
    statement = statement.order_by(desc(order_field), desc(Company.health_score)).limit(limit)
    rows = await db.execute(statement)
    companies = rows.scalars().all()
    if vector_ids:
        companies = await _merge_ranked_results(db, vector_ids, companies, limit)

    if not companies:
        if heuristic_clauses:
            heuristic_statement = select(Company).where(and_(*heuristic_clauses))
            if country:
                heuristic_statement = heuristic_statement.where(Company.country == country)
            if industry:
                heuristic_statement = heuristic_statement.where(Company.industry == industry)
            if min_opportunity_score is not None:
                heuristic_statement = heuristic_statement.where(Company.opportunity_score >= min_opportunity_score)
            if min_growth_score is not None:
                heuristic_statement = heuristic_statement.where(Company.growth_score >= min_growth_score)

            heuristic_statement = heuristic_statement.order_by(desc(order_field), desc(Company.health_score)).limit(limit)
            heuristic_rows = await db.execute(heuristic_statement)
            companies = heuristic_rows.scalars().all()

    if companies:
        reranked = rerank_companies(
            query,
            [
                {
                    "id": str(company.id),
                    "name": company.name,
                    "industry": company.industry,
                    "description": company.description,
                    "ai_summary": company.ai_summary,
                    "enrichment": company.enrichment or {},
                    "opportunity_score": float(company.opportunity_score),
                    "growth_score": float(company.growth_score),
                }
                for company in companies
            ],
        )
        order = {item["id"]: index for index, item in enumerate(reranked)}
        companies = sorted(companies, key=lambda company: order.get(str(company.id), len(order)))

    return companies, filters, applied_filters


async def _vector_ranked_ids(
    db: AsyncSession,
    query: str,
    limit: int,
    country: str | None,
    industry: str | None,
    min_opportunity_score: float | None,
    min_growth_score: float | None,
    sort_by: str,
    heuristic_sql: list[str],
) -> list[str]:
    query_vector = format_vector_literal(generate_embedding(query))
    score_field = "opportunity_score" if sort_by == "opportunity" else "growth_score"

    sql = [
        "select id::text",
        "from companies",
        "where embedding is not null",
    ]
    params: dict[str, object] = {"embedding": query_vector, "limit": limit}

    if country:
        sql.append("and country = :country")
        params["country"] = country
    if industry:
        sql.append("and industry = :industry")
        params["industry"] = industry
    if min_opportunity_score is not None:
        sql.append("and opportunity_score >= :min_opportunity_score")
        params["min_opportunity_score"] = min_opportunity_score
    if min_growth_score is not None:
        sql.append("and growth_score >= :min_growth_score")
        params["min_growth_score"] = min_growth_score
    for clause in heuristic_sql:
        sql.append(f"and {clause}")

    sql.append(f"order by embedding <=> cast(:embedding as vector), {score_field} desc, health_score desc")
    sql.append("limit :limit")

    rows = await db.execute(text("\n".join(sql)), params)
    return list(rows.scalars().all())


async def _merge_ranked_results(
    db: AsyncSession,
    vector_ids: list[str],
    keyword_results: list[Company],
    limit: int,
) -> list[Company]:
    ordered_ids = []
    seen = set()
    for company_id in vector_ids + [str(item.id) for item in keyword_results]:
        if company_id not in seen:
            seen.add(company_id)
            ordered_ids.append(company_id)

    rows = await db.execute(select(Company).where(Company.id.in_(ordered_ids)))
    company_map = {str(item.id): item for item in rows.scalars().all()}
    return [company_map[company_id] for company_id in ordered_ids if company_id in company_map][:limit]


def _build_suggested_filters(lowered: str) -> list[str]:
    filters = []
    if "crm" in lowered:
        filters.append("software-needs")
    if "restaurant" in lowered or "reviews" in lowered or "hospitality" in lowered:
        filters.append("hospitality")
    if "website" in lowered or "web design" in lowered:
        filters.append("website-development")
    if "seo" in lowered or "local seo" in lowered:
        filters.append("seo-needs")
    if "marketing" in lowered or "agency" in lowered:
        filters.append("marketing-needs")
    if "india" in lowered or "local business" in lowered:
        filters.append("india-local")
    if "startup" in lowered or "fast growing" in lowered or "rapid growth" in lowered:
        filters.append("high-growth")
    if "automation" in lowered:
        filters.append("automation-needs")
    return filters


def _build_heuristic_clauses(lowered: str):
    orm_clauses = []
    sql_clauses: list[str] = []

    if any(keyword in lowered for keyword in ("restaurant", "restaurants", "dining", "hospitality", "reviews")):
        orm_clauses.append(Company.industry.ilike("%Hospitality%"))
        sql_clauses.append("industry ilike '%Hospitality%'")
    if any(keyword in lowered for keyword in ("bad reviews", "low rating", "poor rating", "negative reviews")):
        orm_clauses.append(Company.rating <= 3.7)
        sql_clauses.append("rating <= 3.7")
    if any(keyword in lowered for keyword in ("fast growing", "rapid growth", "startup", "startups", "hiring")):
        orm_clauses.append(Company.growth_score >= 70)
        sql_clauses.append("growth_score >= 70")
    if any(keyword in lowered for keyword in ("need website", "needs website", "website development", "no website", "without website")):
        orm_clauses.append(Company.website.is_(None))
        sql_clauses.append("website is null")
    if any(keyword in lowered for keyword in ("marketing", "agency", "reputation", "reviews", "branding")):
        orm_clauses.append(
            or_(
                Company.website.is_(None),
                Company.rating <= 3.8,
                text("(enrichment ->> 'has_social_presence') = 'false'"),
            )
        )
        sql_clauses.append("(website is null or rating <= 3.8 or (enrichment ->> 'has_social_presence') = 'false')")
    if any(keyword in lowered for keyword in ("seo", "local seo", "search presence")):
        orm_clauses.append(
            or_(
                and_(Company.website.is_not(None), Company.reviews_count < 25),
                Company.rating <= 3.8,
            )
        )
        sql_clauses.append("((website is not null and reviews_count < 25) or rating <= 3.8)")
    if any(keyword in lowered for keyword in ("india", "local business", "justdial", "sulekha", "google business", "google maps")):
        orm_clauses.append(
            or_(
                Company.country.ilike("%India%"),
                text("(enrichment ->> 'business_type') = 'local_business'"),
                text("(metadata ->> 'business_type') = 'local_business'"),
            )
        )
        sql_clauses.append("(country ilike '%India%' or (enrichment ->> 'business_type') = 'local_business' or (metadata ->> 'business_type') = 'local_business')")
    if any(keyword in lowered for keyword in ("need crm", "needs crm", "needing crm", "without crm")):
        crm_clause = or_(
            text("(enrichment ->> 'crm') = 'false'"),
            Company.opportunity_score >= 70,
        )
        orm_clauses.append(crm_clause)
        sql_clauses.append("((enrichment ->> 'crm') = 'false' or opportunity_score >= 70)")

    return orm_clauses, sql_clauses
