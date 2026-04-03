from app.schemas.domain import CompanyDetail, CompanySummary, OpportunityItem, SignalItem


def serialize_signal(signal) -> SignalItem:
    return SignalItem.model_validate(signal)


def serialize_opportunity(opportunity) -> OpportunityItem:
    return OpportunityItem.model_validate(opportunity)


def serialize_company(company) -> CompanySummary:
    return CompanySummary.model_validate(company)


def serialize_company_detail(company, relationships) -> CompanyDetail:
    return CompanyDetail(
        id=company.id,
        name=company.name,
        slug=company.slug,
        industry=company.industry,
        city=company.city,
        country=company.country,
        website=company.website,
        health_score=float(company.health_score),
        growth_score=float(company.growth_score),
        opportunity_score=float(company.opportunity_score),
        enrichment=company.enrichment or {},
        description=company.description,
        ai_summary=company.ai_summary,
        metadata=company.company_metadata or {},
        signals=[serialize_signal(item) for item in company.signals],
        opportunities=[serialize_opportunity(item) for item in company.opportunities],
        relationships=[
            {
                "id": str(item.id),
                "relationship_type": item.relationship_type,
                "weight": float(item.weight),
                "metadata": item.relationship_metadata,
            }
            for item in relationships
        ],
        sources=[
            {
                "id": str(item.id),
                "source_type": item.source_type,
                "source_key": item.source_key,
                "source_url": item.source_url,
                "confidence": float(item.confidence),
                "metadata": item.source_metadata,
            }
            for item in getattr(company, "sources", [])
        ],
    )
