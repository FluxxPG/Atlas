import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, text

from worker.runtime import configure_runtime
from worker.connectors import discover_by_query, enrich_company_with_vendors, expand_geo_grid, expand_related_companies, merge_enrichment
from worker.db import SessionLocal
from worker.engines.embeddings import build_company_embedding_text, format_vector_literal, generate_embedding
from worker.engines.discovery import discover_companies_from_seed
from worker.engines.enrichment import enrich_company, merge_directory_website_profile
from worker.engines.graph import build_relationships
from worker.engines.intent import detect_buyer_intent
from worker.engines.opportunities import generate_opportunities
from worker.engines.scoring import compute_growth_score, compute_health_score, compute_opportunity_score
from worker.engines.signals import generate_signals
from worker.models import Company, CompanySource, CrawlJob, Log, Opportunity, Relationship, Signal
from worker.queue.redis_queue import redis_queue
from worker.realtime import realtime_publisher

configure_runtime()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def write_log(level: str, message: str, context: dict | None = None):
    async with SessionLocal() as session:
        session.add(Log(level=level, source="worker", message=message, context=context or {}))
        await session.commit()


async def set_job_status(job_id: str | None, **updates):
    if not job_id:
        return

    async with SessionLocal() as session:
        job = await session.get(CrawlJob, job_id)
        if not job:
            return

        for key, value in updates.items():
            setattr(job, key, value)
        await session.commit()


async def persist_company(company_data: dict):
    db_company_data = {
        **company_data,
        "company_metadata": company_data.get("metadata", {}),
    }
    db_company_data.pop("metadata", None)
    db_company_data.pop("source_records", None)

    async with SessionLocal() as session:
        existing = await session.execute(select(Company).where(Company.slug == company_data["slug"]))
        company = existing.scalar_one_or_none()
        if not company:
            company = Company(**db_company_data)
            session.add(company)
            await session.flush()
        else:
            for key, value in db_company_data.items():
                setattr(company, key, value)

        await session.execute(Signal.__table__.delete().where(Signal.company_id == company.id))
        await session.execute(Opportunity.__table__.delete().where(Opportunity.company_id == company.id))
        await session.execute(Relationship.__table__.delete().where(Relationship.source_company_id == company.id))
        await session.execute(CompanySource.__table__.delete().where(CompanySource.company_id == company.id))

        for signal in generate_signals(company_data):
            session.add(Signal(id=uuid.uuid4(), company_id=company.id, **signal))
        for opportunity in generate_opportunities(company_data):
            session.add(Opportunity(id=uuid.uuid4(), company_id=company.id, **opportunity))
        for relationship in build_relationships(company_data):
            session.add(
                Relationship(
                    id=uuid.uuid4(),
                    source_company_id=company.id,
                    relationship_type=relationship["relationship_type"],
                    weight=relationship["weight"],
                    relationship_metadata=relationship["metadata"],
                )
            )
        for source in company_data.get("source_records", []):
            session.add(
                CompanySource(
                    id=uuid.uuid4(),
                    company_id=company.id,
                    source_type=source["source_type"],
                    source_key=source["source_key"],
                    source_url=source.get("source_url"),
                    confidence=source.get("confidence", 0.5),
                    source_metadata=source.get("metadata", {}),
                )
            )

        embedding_text = build_company_embedding_text(company_data)
        embedding = format_vector_literal(generate_embedding(embedding_text))
        await session.execute(
            text("update companies set embedding = cast(:embedding as vector) where id = :company_id"),
            {"embedding": embedding, "company_id": company.id},
        )

        await session.commit()
        await realtime_publisher.publish(
            "company.updated",
            {
                "company": company_data["name"],
                "scores": {
                    "health": company_data["health_score"],
                    "growth": company_data["growth_score"],
                    "opportunity": company_data["opportunity_score"],
                },
            },
        )


async def process_seed_job(job: dict):
    discovered = discover_companies_from_seed(job)
    await realtime_publisher.publish(
        "crawl.started",
        {"city": job["city"], "country": job["country"], "job_id": job.get("job_id")},
    )
    for company in discovered:
        buyer_intent = detect_buyer_intent(company)
        enrichment = enrich_company({**company, "content": f"{company['description']} contact@{company['slug']}.com hubspot zapier"})
        vendor_enrichment = await enrich_company_with_vendors(company)
        enrichment = merge_enrichment(enrichment, vendor_enrichment)
        _apply_vendor_company_updates(company, vendor_enrichment)
        enrichment["new_technology_detected"] = "zapier" in enrichment.get("technology_stack", [])
        company = merge_directory_website_profile(company, enrichment)
        enrichment = company["enrichment"]
        company["metadata"] = {
            **company.get("metadata", {}),
            "intent_topics": [
                key.replace("_signal", "")
                for key, value in buyer_intent.items()
                if key.endswith("_signal") and value
            ],
        }
        company["health_score"] = compute_health_score(company)
        company["growth_score"] = compute_growth_score(company)
        company["opportunity_score"] = compute_opportunity_score(company)
        company["ai_summary"] = (
            f"{company['name']} shows {company['industry']} demand in {company['city']} with an "
            f"intent score of {buyer_intent['intent_score']}."
        )
        await persist_company(company)
    await realtime_publisher.publish(
        "crawl.completed",
        {"city": job["city"], "records": len(discovered), "job_id": job.get("job_id")},
    )
    await write_log(
        "info",
        "Seed crawl completed",
        {"job_id": job.get("job_id"), "city": job["city"], "records": len(discovered)},
    )


async def process_search_discovery_job(job: dict):
    query = job["query"]
    source = job.get("source")
    discovered = await discover_by_query(
        query,
        job.get("city"),
        job.get("region"),
        job.get("country"),
        provider=source,
    )
    await realtime_publisher.publish("crawl.discovery_started", {"query": query, "job_id": job.get("job_id")})
    source_breakdown: dict[str, int] = {}
    expanded = []
    for company in discovered:
        provider = (company.get("metadata") or {}).get("provider") or source or "public_web"
        source_breakdown[provider] = source_breakdown.get(provider, 0) + 1
        enrichment = enrich_company(
            {
                **company,
                "content": f"{company['description']} hello@{company['slug']}.com hubspot automation linkedin.com/{company['slug']}"
            }
        )
        vendor_enrichment = await enrich_company_with_vendors(company)
        enrichment = merge_enrichment(enrichment, vendor_enrichment)
        _apply_vendor_company_updates(company, vendor_enrichment)
        enrichment["new_technology_detected"] = "hubspot" in enrichment.get("technology_stack", [])
        company = merge_directory_website_profile(company, enrichment)
        enrichment = company["enrichment"]
        intent = detect_buyer_intent(company)
        company["metadata"] = {
            **company.get("metadata", {}),
            "intent_topics": [key.replace("_signal", "") for key, value in intent.items() if key.endswith("_signal") and value],
        }
        company["health_score"] = compute_health_score(company)
        company["growth_score"] = compute_growth_score(company)
        company["opportunity_score"] = compute_opportunity_score(company)
        company["ai_summary"] = f"{company['name']} was discovered through {job.get('source', 'public web')} for query '{query}'."
        await persist_company(company)
        expanded.extend(expand_related_companies(company))

    for company in expanded[:4]:
        enrichment = enrich_company({**company, "content": f"{company['description']} info@{company['slug']}.com zapier"})
        vendor_enrichment = await enrich_company_with_vendors(company)
        enrichment = merge_enrichment(enrichment, vendor_enrichment)
        _apply_vendor_company_updates(company, vendor_enrichment)
        company = merge_directory_website_profile(company, enrichment)
        company["health_score"] = compute_health_score(company)
        company["growth_score"] = compute_growth_score(company)
        company["opportunity_score"] = compute_opportunity_score(company)
        await persist_company(company)

    await realtime_publisher.publish(
        "crawl.discovery_completed",
        {
            "query": query,
            "job_id": job.get("job_id"),
            "records": len(discovered) + min(len(expanded), 4),
            "sources": source_breakdown,
        },
    )
    await write_log(
        "info",
        "Search discovery completed",
        {"job_id": job.get("job_id"), "query": query, "requested_source": source, "source_breakdown": source_breakdown},
    )


async def process_geo_grid_scan_job(job: dict):
    city = job["city"]
    cells = expand_geo_grid(job["grid"])
    await realtime_publisher.publish("crawl.grid_started", {"city": city, "cells": len(cells), "job_id": job.get("job_id")})
    source_breakdown: dict[str, int] = {}
    for lat, lon in cells[:4]:
        discovered = await discover_by_query(
            "business software",
            city=city,
            region=job.get("region"),
            country=job.get("country"),
            provider=job.get("source"),
        )
        for company in discovered[:2]:
            provider = (company.get("metadata") or {}).get("provider") or job.get("source") or "public_web"
            source_breakdown[provider] = source_breakdown.get(provider, 0) + 1
            company["metadata"] = {**company.get("metadata", {}), "grid_cell": [lat, lon]}
            enrichment = enrich_company({**company, "content": f"{company['description']} sales@{company['slug']}.com salesforce"})
            vendor_enrichment = await enrich_company_with_vendors(company)
            enrichment = merge_enrichment(enrichment, vendor_enrichment)
            _apply_vendor_company_updates(company, vendor_enrichment)
            company = merge_directory_website_profile(company, enrichment)
            company["health_score"] = compute_health_score(company)
            company["growth_score"] = compute_growth_score(company)
            company["opportunity_score"] = compute_opportunity_score(company)
            await persist_company(company)
    await realtime_publisher.publish(
        "crawl.grid_completed",
        {"city": city, "cells": len(cells), "job_id": job.get("job_id"), "sources": source_breakdown},
    )
    await write_log(
        "info",
        "Geo grid scan completed",
        {"job_id": job.get("job_id"), "city": city, "cells": len(cells), "source_breakdown": source_breakdown},
    )


async def handle_crawl_job(job: dict):
    job_id = job.get("job_id")
    attempts = int(job.get("attempts", 0))
    max_attempts = int(job.get("max_attempts", 5))

    await set_job_status(job_id, status="running", attempts=attempts + 1, started_at=utc_now(), last_error=None)
    try:
        if job.get("job_type") == "city_seed":
            await process_seed_job(job)
        elif job.get("job_type") == "search_discovery":
            await process_search_discovery_job(job)
        elif job.get("job_type") == "geo_grid_scan":
            await process_geo_grid_scan_job(job)
        await set_job_status(job_id, status="completed", finished_at=utc_now())
    except Exception as exc:
        await write_log(
            "error",
            "Crawl job failed",
            {"job_id": job_id, "job_type": job.get("job_type"), "error": str(exc), "attempts": attempts + 1},
        )
        if attempts + 1 < max_attempts:
            retry_payload = {**job, "attempts": attempts + 1}
            await set_job_status(job_id, status="queued", last_error=str(exc))
            await redis_queue.push("crawl:jobs", retry_payload)
            await realtime_publisher.publish(
                "crawl.retry_scheduled",
                {"job_id": job_id, "attempts": attempts + 1, "max_attempts": max_attempts},
            )
        else:
            await set_job_status(job_id, status="failed", last_error=str(exc), finished_at=utc_now())
            await realtime_publisher.publish(
                "crawl.failed",
                {"job_id": job_id, "error": str(exc), "attempts": attempts + 1},
            )


async def handle_system_job(job: dict):
    job_type = job.get("job_type")
    if job_type == "rebuild_embeddings":
        async with SessionLocal() as session:
            companies = (await session.execute(select(Company))).scalars().all()
            for company in companies:
                payload = {
                    "name": company.name,
                    "industry": company.industry,
                    "city": company.city,
                    "region": company.region,
                    "country": company.country,
                    "description": company.description,
                    "ai_summary": company.ai_summary,
                    "enrichment": company.enrichment or {},
                    "metadata": company.company_metadata or {},
                }
                embedding = format_vector_literal(generate_embedding(build_company_embedding_text(payload)))
                await session.execute(
                    text("update companies set embedding = cast(:embedding as vector) where id = :company_id"),
                    {"embedding": embedding, "company_id": company.id},
                )
            await session.commit()
        await write_log("info", "Embedding rebuild completed", {"companies": len(companies)})
    elif job_type == "rebuild_insights":
        await write_log("info", "Insight rebuild requested", {"job_type": job_type})


def _apply_vendor_company_updates(company: dict, vendor_enrichment: dict) -> None:
    if not vendor_enrichment:
        return

    if vendor_enrichment.get("description") and (
        not company.get("description")
        or "Discovered from public web search" in company.get("description", "")
        or "Synthetic fallback discovery result" in company.get("description", "")
    ):
        company["description"] = vendor_enrichment["description"]

    if vendor_enrichment.get("industry") and not company.get("industry"):
        company["industry"] = vendor_enrichment["industry"]
    if vendor_enrichment.get("employee_range") and not company.get("employee_range"):
        company["employee_range"] = vendor_enrichment["employee_range"]
    if vendor_enrichment.get("revenue_range") and not company.get("revenue_range"):
        company["revenue_range"] = vendor_enrichment["revenue_range"]

    provider_matches = vendor_enrichment.get("provider_matches") or []
    if provider_matches:
        company["metadata"] = {
            **company.get("metadata", {}),
            "provider_matches": list(dict.fromkeys([*(company.get("metadata", {}).get("provider_matches", [])), *provider_matches])),
        }

    source_records = vendor_enrichment.get("source_records") or []
    if source_records:
        company["source_records"] = [*(company.get("source_records", [])), *source_records]


async def main():
    while True:
        job = await redis_queue.pop("crawl:jobs", timeout=5)
        if job:
            await handle_crawl_job(job)
            continue

        system_job = await redis_queue.pop("system:jobs", timeout=1)
        if system_job:
            await handle_system_job(system_job)
            continue

        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
