from urllib.parse import urlparse

import httpx

from worker.config import settings


async def enrich_company_with_vendors(company: dict) -> dict:
    domain = company.get("domain") or _extract_domain(company.get("website"))
    enrichment: dict = {
        "emails": [],
        "phones": [],
        "social_profiles": [],
        "technology_stack": [],
        "provider_matches": [],
        "source_records": [],
    }

    hunter = await _enrich_with_hunter(domain)
    enrichment = merge_enrichment(enrichment, hunter)

    pdl = await _enrich_with_peopledatalabs(company, domain)
    enrichment = merge_enrichment(enrichment, pdl)

    return enrichment


def merge_enrichment(base: dict, extra: dict | None) -> dict:
    if not extra:
        return base

    merged = {**base}
    list_fields = ["emails", "phones", "social_profiles", "technology_stack", "automation_tools", "provider_matches", "source_records"]
    for field in list_fields:
        merged[field] = list(dict.fromkeys([*(merged.get(field) or []), *((extra.get(field) or []))]))

    for field in ["crm", "new_technology_detected"]:
        if field in extra:
            merged[field] = bool(extra[field])

    for field in ["description", "industry", "employee_range", "revenue_range"]:
        if extra.get(field) and not merged.get(field):
            merged[field] = extra[field]

    for key, value in extra.items():
        if key not in merged:
            merged[key] = value

    return merged


async def _enrich_with_hunter(domain: str | None) -> dict:
    if not domain or not settings.hunter_api_key:
        return {}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://api.hunter.io/v2/domain-search",
                params={"domain": domain, "api_key": settings.hunter_api_key},
            )
            response.raise_for_status()
            payload = response.json().get("data") or {}
    except Exception:
        return {}

    emails = []
    phones = []
    for item in payload.get("emails", [])[:10]:
        value = item.get("value")
        if value:
            emails.append(value)
        phone = item.get("phone_number")
        if phone:
            phones.append(phone)

    return {
        "emails": emails,
        "phones": phones,
        "provider_matches": ["hunter"],
        "source_records": [
            {
                "source_type": "hunter",
                "source_key": domain,
                "source_url": f"https://hunter.io/search/{domain}",
                "confidence": 0.88,
                "metadata": {"provider": "hunter"},
            }
        ],
    }


async def _enrich_with_peopledatalabs(company: dict, domain: str | None) -> dict:
    if not settings.peopledatalabs_api_key or not (domain or company.get("website") or company.get("name")):
        return {}

    params: dict[str, str] = {}
    if company.get("website"):
        params["website"] = company["website"]
    elif domain:
        params["website"] = f"https://{domain}"
    elif company.get("name"):
        params["name"] = company["name"]

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://api.peopledatalabs.com/v5/company/enrich",
                params=params,
                headers={"X-Api-Key": settings.peopledatalabs_api_key},
            )
            response.raise_for_status()
            payload = response.json()
    except Exception:
        return {}

    socials = [
        value
        for value in [
            payload.get("linkedin_url"),
            payload.get("facebook_url"),
            payload.get("twitter_url"),
            payload.get("website"),
        ]
        if value
    ]
    technologies = payload.get("technologies") or payload.get("technology_names") or []

    return {
        "description": payload.get("description"),
        "industry": payload.get("industry"),
        "social_profiles": socials,
        "technology_stack": technologies[:12] if isinstance(technologies, list) else [],
        "provider_matches": ["peopledatalabs"],
        "source_records": [
            {
                "source_type": "peopledatalabs",
                "source_key": domain or company.get("slug") or company.get("name", "company"),
                "source_url": payload.get("website") or company.get("website"),
                "confidence": 0.84,
                "metadata": {"provider": "peopledatalabs"},
            }
        ],
        "employee_range": str(payload.get("employee_count")) if payload.get("employee_count") else None,
        "revenue_range": str(payload.get("inferred_revenue")) if payload.get("inferred_revenue") else None,
    }


def _extract_domain(website: str | None) -> str | None:
    if not website:
        return None
    return urlparse(website).netloc.replace("www.", "") or None
