from collections import Counter, defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Company, Opportunity, Signal


async def build_dashboard(db: AsyncSession) -> dict:
    company_count = (await db.execute(select(func.count()).select_from(Company))).scalar_one()
    signal_count = (await db.execute(select(func.count()).select_from(Signal))).scalar_one()
    opportunity_count = (await db.execute(select(func.count()).select_from(Opportunity))).scalar_one()
    companies = (await db.execute(select(Company))).scalars().all()

    top_signals = (
        await db.execute(select(Signal).order_by(Signal.created_at.desc()).limit(6))
    ).scalars().all()
    top_opportunities = (
        await db.execute(select(Opportunity).order_by(Opportunity.confidence.desc()).limit(6))
    ).scalars().all()
    industry_counter = Counter(company.industry or "Unknown" for company in companies)
    city_scores: dict[str, list[float]] = defaultdict(list)
    for company in companies:
        if company.city:
            city_scores[company.city].append(float(company.opportunity_score))

    total_companies = max(company_count, 1)
    market_map = [
        {"label": label, "value": round((count / total_companies) * 100)}
        for label, count in industry_counter.most_common(4)
    ]
    heatmap = [
        {"city": city, "score": round(sum(scores) / len(scores))}
        for city, scores in sorted(city_scores.items(), key=lambda item: sum(item[1]) / len(item[1]), reverse=True)[:4]
    ]

    return {
        "metrics": [
            {"label": "Companies indexed", "value": company_count, "delta": 12.8, "meta": {"window": "30d"}},
            {"label": "Signals detected", "value": signal_count, "delta": 24.1, "meta": {"window": "7d"}},
            {
                "label": "Opportunities generated",
                "value": opportunity_count,
                "delta": 18.4,
                "meta": {"window": "7d"},
            },
            {
                "label": "Crawler coverage",
                "value": f"{len({company.country for company in companies if company.country})} countries",
                "delta": None,
                "meta": {"grids": len({company.city for company in companies if company.city})},
            },
        ],
        "top_signals": top_signals,
        "top_opportunities": top_opportunities,
        "market_map": market_map or [{"label": "No data", "value": 0}],
        "heatmap": heatmap or [{"city": "No data", "score": 0}],
    }


async def build_insights(db: AsyncSession) -> dict:
    companies = (await db.execute(select(Company))).scalars().all()
    signals = (await db.execute(select(Signal))).scalars().all()
    opportunities = (await db.execute(select(Opportunity))).scalars().all()

    industry_stats: dict[str, dict[str, list[float] | int]] = defaultdict(
        lambda: {"growth_scores": [], "opportunity_scores": [], "count": 0}
    )
    city_scores: dict[str, list[float]] = defaultdict(list)
    tech_counts: Counter[str] = Counter()

    for company in companies:
        industry = company.industry or "Unknown"
        industry_stats[industry]["growth_scores"].append(float(company.growth_score))
        industry_stats[industry]["opportunity_scores"].append(float(company.opportunity_score))
        industry_stats[industry]["count"] += 1
        if company.city:
            city_scores[company.city].append(float(company.opportunity_score))
        for technology in (company.enrichment or {}).get("technology_stack", []):
            tech_counts[str(technology).title()] += 1

    trend_cards = [
        {
            "label": "Hiring surge",
            "value": sum(1 for signal in signals if signal.type == "hiring-activity"),
            "delta": 14.0,
            "meta": {"signal": "jobs"},
        },
        {
            "label": "CRM whitespace",
            "value": sum(
                1 for opportunity in opportunities if opportunity.category in {"software-needs", "marketing-needs"}
            ),
            "delta": 6.2,
            "meta": {"segment": "SMB"},
        },
        {
            "label": "Automation fit",
            "value": sum(1 for opportunity in opportunities if opportunity.category == "automation-needs"),
            "delta": 9.5,
            "meta": {"region": "Global"},
        },
    ]

    industry_trends = [
        {
            "industry": industry,
            "growth": round(sum(stats["growth_scores"]) / max(len(stats["growth_scores"]), 1)),
            "opportunity": round(sum(stats["opportunity_scores"]) / max(len(stats["opportunity_scores"]), 1)),
        }
        for industry, stats in sorted(
            industry_stats.items(),
            key=lambda item: sum(item[1]["opportunity_scores"]) / max(len(item[1]["opportunity_scores"]), 1),
            reverse=True,
        )[:6]
    ]
    city_heatmap = [
        {"city": city, "density": round(sum(scores) / len(scores))}
        for city, scores in sorted(city_scores.items(), key=lambda item: sum(item[1]) / len(item[1]), reverse=True)[:6]
    ]
    tech_adoption = [
        {"technology": technology, "adoption": count}
        for technology, count in tech_counts.most_common(6)
    ]

    return {
        "trend_cards": trend_cards,
        "industry_trends": industry_trends,
        "city_heatmap": city_heatmap,
        "tech_adoption": tech_adoption,
    }
