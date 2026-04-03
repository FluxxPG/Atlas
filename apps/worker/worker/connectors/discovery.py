from urllib.parse import urlparse

import httpx
from slugify import slugify

from worker.config import settings
from worker.connectors.directory_runtime import discover_directory_records
from worker.connectors.public_web import discover_by_query as discover_by_query_public_web
from worker.connectors.public_web import expand_geo_grid, expand_related_companies
from worker.connectors.source_registry import INDIA_DIRECTORY_KEYS, get_source_spec


async def discover_by_query(
    query: str,
    city: str | None = None,
    region: str | None = None,
    country: str | None = None,
    provider: str | None = None,
) -> list[dict]:
    selected_provider = (provider or settings.discovery_provider or "public_web").lower()
    approved_sources = {item.strip().lower() for item in settings.approved_sources.split(",") if item.strip()}
    if selected_provider not in approved_sources and selected_provider != "hybrid":
        selected_provider = "public_web"
    results: list[dict] = []

    if selected_provider not in {"hybrid", "public_web", "duckduckgo", "serpapi", "india_local"}:
        results.extend(
            await discover_directory_records(
                query,
                city=city,
                region=region,
                country=country,
                source_key=selected_provider,
                fetch_pages=settings.fetch_directory_pages,
            )
        )

    if selected_provider in {"hybrid", "serpapi"}:
        results.extend(await _discover_via_serpapi(query, city, region, country))

    if _is_india_market(country, city, region) and selected_provider in {"hybrid", "public_web", "duckduckgo", "india_local"}:
        results.extend(await _discover_india_local_sources(query, city, region, country))

    if selected_provider in {"hybrid", "public_web", "duckduckgo"} or not results:
        results.extend(await discover_by_query_public_web(query, city, region, country))

    return _dedupe_results(results)


async def _discover_india_local_sources(
    query: str,
    city: str | None = None,
    region: str | None = None,
    country: str | None = None,
) -> list[dict]:
    discovered: list[dict] = []
    effective_country = country or "India"

    for source_key in INDIA_DIRECTORY_KEYS:
        discovered.extend(
            await discover_directory_records(
                query,
                city=city,
                region=region,
                country=effective_country,
                source_key=source_key,
                fetch_pages=settings.fetch_directory_pages,
            )
        )

    return discovered


async def _discover_via_serpapi(
    query: str,
    city: str | None = None,
    region: str | None = None,
    country: str | None = None,
) -> list[dict]:
    if not settings.serpapi_api_key:
        return []

    search_query = " ".join(part for part in [query, city, region, country] if part)
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            response = await client.get(
                "https://serpapi.com/search.json",
                params={
                    "engine": "google",
                    "q": search_query,
                    "api_key": settings.serpapi_api_key,
                    "num": 10,
                },
            )
            response.raise_for_status()
            payload = response.json()
    except Exception:
        return []

    discovered = []
    for item in payload.get("organic_results", []):
        href = item.get("link")
        if not href:
            continue
        domain = urlparse(href).netloc.replace("www.", "")
        if not domain:
            continue
        title = item.get("title") or domain.split(".")[0].replace("-", " ").title()
        snippet = item.get("snippet") or f"Discovered via SerpAPI for '{search_query}'."
        company_name = _normalize_company_name(title, domain)
        discovered.append(
            {
                "name": company_name,
                "slug": slugify(company_name),
                "website": href,
                "domain": domain,
                "industry": _infer_industry(query),
                "subindustry": _infer_subindustry(query),
                "city": city,
                "region": region,
                "country": country,
                "rating": 4.1,
                "reviews_count": 55,
                "description": snippet,
                "metadata": {
                    "query": query,
                    "provider": "serpapi",
                    "is_hiring": False,
                    "traffic_growth": 11,
                    "business_type": _infer_business_type(query, "serpapi"),
                    "directory_sources": [],
                },
                "source_records": [
                    {
                        "source_type": "serpapi",
                        "source_key": domain,
                        "source_url": href,
                        "confidence": 0.82,
                        "metadata": {"query": search_query},
                    }
                ],
            }
        )
    return discovered


def _dedupe_results(results: list[dict]) -> list[dict]:
    deduped: list[dict] = []
    seen_index: dict[str, int] = {}
    for item in results:
        key = item.get("domain") or item.get("slug") or item.get("name", "")
        if key in seen_index:
            existing = deduped[seen_index[key]]
            existing_metadata = dict(existing.get("metadata") or {})
            incoming_metadata = dict(item.get("metadata") or {})
            existing_sources = list(dict.fromkeys([*(existing_metadata.get("directory_sources", [])), *(incoming_metadata.get("directory_sources", []))]))
            existing_categories = list(dict.fromkeys([*(existing_metadata.get("categories", [])), *(incoming_metadata.get("categories", []))]))
            existing["metadata"] = {**existing_metadata, **incoming_metadata, "directory_sources": existing_sources, "categories": existing_categories}
            existing["source_records"] = [*(existing.get("source_records") or []), *(item.get("source_records") or [])]
            continue
        seen_index[key] = len(deduped)
        deduped.append(item)
    return deduped


def _normalize_company_name(title: str, domain: str) -> str:
    cleaned = title.split(" - ")[0].split(" | ")[0].split(":")[0].strip()
    return cleaned or domain.split(".")[0].replace("-", " ").title()


def _infer_industry(query: str) -> str:
    lowered = query.lower()
    if any(token in lowered for token in ("restaurant", "dining", "hospitality", "cafe", "salon", "spa")):
        return "Hospitality"
    if any(token in lowered for token in ("clinic", "hospital", "health", "dentist")):
        return "Healthcare"
    if any(token in lowered for token in ("school", "coaching", "education", "academy")):
        return "Education"
    if any(token in lowered for token in ("real estate", "property", "builder")):
        return "Real Estate"
    if any(token in lowered for token in ("crm", "software", "saas", "startup", "tech")):
        return "SaaS"
    if any(token in lowered for token in ("factory", "manufacturing", "operations", "industrial")):
        return "Manufacturing"
    return "Business Services"


def _infer_subindustry(query: str) -> str:
    lowered = query.lower()
    if "restaurant" in lowered or "cafe" in lowered:
        return "Restaurants"
    if "salon" in lowered or "spa" in lowered:
        return "Beauty & Wellness"
    if "clinic" in lowered or "dentist" in lowered:
        return "Clinics"
    if "real estate" in lowered or "property" in lowered:
        return "Property Services"
    if "startup" in lowered or "saas" in lowered:
        return "B2B Software"
    return "General"


def _infer_business_type(query: str, provider: str) -> str:
    lowered = query.lower()
    spec = get_source_spec(provider)
    if spec.key != "public_web":
        return spec.business_type
    if "startup" in lowered or "saas" in lowered:
        return "startup"
    if any(token in lowered for token in ("manufacturer", "factory", "industrial")):
        return "supplier"
    return "smb"


def _is_india_market(country: str | None, city: str | None, region: str | None) -> bool:
    joined = " ".join(part for part in [country, city, region] if part).lower()
    return not joined or "india" in joined or any(
        token in joined
        for token in ("bengaluru", "bangalore", "mumbai", "delhi", "hyderabad", "pune", "chennai", "kolkata")
    )


__all__ = ["discover_by_query", "expand_geo_grid", "expand_related_companies", "_dedupe_results"]
