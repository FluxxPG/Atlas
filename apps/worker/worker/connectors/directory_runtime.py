import asyncio
import re
from urllib.parse import urlparse

from slugify import slugify

from worker.connectors.parsers import parse_directory_page
from worker.connectors.public_web import discover_by_query as discover_by_query_public_web
from worker.connectors.source_registry import SourceSpec, get_source_spec
from worker.config import settings
from worker.crawlers.playwright_crawler import fetch_page


async def discover_directory_records(
    query: str,
    *,
    city: str | None = None,
    region: str | None = None,
    country: str | None = None,
    source_key: str,
    fetch_pages: bool = False,
) -> list[dict]:
    spec = get_source_spec(source_key)
    search_query = _build_search_query(query, city, region, country, spec)
    raw_results = await discover_by_query_public_web(search_query, city, region, country)
    results = _filter_results_for_source(raw_results, spec)
    telemetry = _build_search_telemetry(spec, search_query, raw_results, results)
    if not results:
        return [_build_fallback_record(query, city, region, country, spec, telemetry=telemetry)]

    normalized = [
        _normalize_listing(item, query, city, region, country, spec, telemetry=telemetry)
        for item in results[:5]
    ]
    if fetch_pages and spec.requires_playwright:
        normalized = await _hydrate_listing_pages(normalized, spec, follow_details=True)
    return normalized


def _build_search_query(
    query: str,
    city: str | None,
    region: str | None,
    country: str | None,
    spec: SourceSpec,
) -> str:
    return " ".join(part for part in [query, city, region, country, spec.site_query] if part)


def _normalize_listing(
    item: dict,
    query: str,
    city: str | None,
    region: str | None,
    country: str | None,
    spec: SourceSpec,
    telemetry: dict | None = None,
) -> dict:
    source_records = [
        *(item.get("source_records") or []),
        {
            "source_type": spec.key,
            "source_key": item.get("domain") or item.get("slug"),
            "source_url": item.get("website"),
            "confidence": 0.8,
            "metadata": {"source_label": spec.label, "site_query": spec.site_query},
        },
    ]
    metadata = dict(item.get("metadata") or {})
    metadata["provider"] = spec.key
    metadata["directory_sources"] = list(dict.fromkeys([*(metadata.get("directory_sources", [])), spec.key]))
    metadata["business_type"] = metadata.get("business_type") or spec.business_type
    metadata["categories"] = list(dict.fromkeys([*(metadata.get("categories", [])), *spec.categories]))
    metadata["crawl_plan"] = {
        "source": spec.key,
        "query": query,
        "city": city,
        "region": region,
        "country": country,
    }
    metadata["crawl_telemetry"] = {
        **(metadata.get("crawl_telemetry") or {}),
        **(telemetry or {}),
        "stage": "search_result",
        "parser_used": False,
    }
    return {
        **item,
        "industry": item.get("industry"),
        "subindustry": item.get("subindustry"),
        "city": item.get("city") or city,
        "region": item.get("region") or region,
        "country": item.get("country") or country,
        "source_records": source_records,
        "metadata": metadata,
    }


async def _hydrate_listing_pages(records: list[dict], spec: SourceSpec, follow_details: bool = False) -> list[dict]:
    async def hydrate(record: dict) -> dict:
        website = record.get("website")
        if not website:
            return record
        try:
            page = await fetch_page(website)
        except Exception:
            return record
        parsed = parse_directory_page(spec.key, page)
        aggregated_detail_candidates = list(parsed.get("detail_candidates", []))
        pagination_candidates = _filter_detail_candidates(parsed.get("pagination_candidates", []), spec)
        paginated_pages = []
        for url in pagination_candidates[: max(0, settings.directory_max_listing_pages - 1)]:
            try:
                next_page = await fetch_page(url)
            except Exception:
                continue
            next_parsed = parse_directory_page(spec.key, next_page)
            paginated_pages.append({"url": url, "title": next_page.get("title"), "parsed": next_parsed})
            aggregated_detail_candidates.extend(next_parsed.get("detail_candidates", []))
        record["metadata"] = {
            **(record.get("metadata") or {}),
            "page_title": page.get("title"),
            "listing_summary": _extract_listing_summary(page.get("content", "")),
            "parsed_listing": parsed,
            "paginated_listing_pages": paginated_pages,
        }
        crawl_telemetry = dict(record["metadata"].get("crawl_telemetry") or {})
        crawl_telemetry["stage"] = "listing_page_parsed"
        crawl_telemetry["parser_used"] = True
        crawl_telemetry["parser_source"] = spec.key
        crawl_telemetry["listing_pages_count"] = 1 + len(paginated_pages)
        record["metadata"]["crawl_telemetry"] = crawl_telemetry
        if parsed.get("name"):
            record["name"] = parsed["name"]
        elif parsed.get("title") and not record.get("name"):
            record["name"] = parsed["title"]
        if parsed.get("address"):
            record["metadata"]["address"] = parsed["address"]
        if parsed.get("phone"):
            record["metadata"]["contact_phone"] = parsed["phone"]
        if parsed.get("website") and not record.get("website"):
            record["website"] = parsed["website"]
        if parsed.get("rating") is not None:
            record["rating"] = parsed["rating"]
        if parsed.get("reviews_count") is not None:
            record["reviews_count"] = parsed["reviews_count"]
        if parsed.get("industry") and not record.get("industry"):
            record["industry"] = parsed["industry"]
        if parsed.get("subindustry") and not record.get("subindustry"):
            record["subindustry"] = parsed["subindustry"]
        if parsed.get("categories"):
            record["metadata"]["categories"] = list(
                dict.fromkeys([*(record["metadata"].get("categories", [])), *parsed["categories"]])
            )
        if aggregated_detail_candidates:
            record["metadata"]["detail_candidates"] = list(dict.fromkeys(aggregated_detail_candidates))
        if parsed.get("description") and not record.get("description"):
            record["description"] = parsed["description"]
        elif not record.get("description") and record["metadata"].get("listing_summary"):
            record["description"] = record["metadata"]["listing_summary"]
        if follow_details and aggregated_detail_candidates:
            record = await _hydrate_detail_candidates(record, spec, aggregated_detail_candidates)
        return record

    return await asyncio.gather(*(hydrate(record) for record in records))


async def _hydrate_detail_candidates(record: dict, spec: SourceSpec, candidates: list[str]) -> dict:
    detail_urls = _filter_detail_candidates(candidates, spec)[: settings.directory_max_detail_pages]
    if not detail_urls:
        return record

    detail_pages = []
    for url in detail_urls:
        try:
            detail_pages.append((url, await fetch_page(url)))
        except Exception:
            continue

    if not detail_pages:
        return record

    merged_detail = {}
    parsed_pages = []
    for url, page in detail_pages:
        parsed = parse_directory_page(spec.key, page)
        parsed_pages.append({"url": url, "parsed": parsed, "title": page.get("title")})
        merged_detail = _merge_detail_payloads(merged_detail, parsed)

    record["metadata"] = {
        **(record.get("metadata") or {}),
        "detail_pages": parsed_pages,
        "detail_candidates": detail_urls,
    }
    crawl_telemetry = dict(record["metadata"].get("crawl_telemetry") or {})
    crawl_telemetry["stage"] = "detail_pages_parsed"
    crawl_telemetry["detail_pages_count"] = len(detail_pages)
    record["metadata"]["crawl_telemetry"] = crawl_telemetry

    if merged_detail.get("name"):
        record["name"] = merged_detail["name"]
    if merged_detail.get("address"):
        record["metadata"]["address"] = merged_detail["address"]
    if merged_detail.get("phone"):
        record["metadata"]["contact_phone"] = merged_detail["phone"]
    if merged_detail.get("website") and not record.get("website"):
        record["website"] = merged_detail["website"]
    if merged_detail.get("rating") is not None:
        record["rating"] = merged_detail["rating"]
    if merged_detail.get("reviews_count") is not None:
        record["reviews_count"] = merged_detail["reviews_count"]
    if merged_detail.get("industry"):
        record["industry"] = merged_detail["industry"]
    if merged_detail.get("subindustry"):
        record["subindustry"] = merged_detail["subindustry"]
    if merged_detail.get("categories"):
        record["metadata"]["categories"] = list(
            dict.fromkeys([*(record["metadata"].get("categories", [])), *merged_detail["categories"]])
        )
    if merged_detail.get("description"):
        record["description"] = merged_detail["description"]

    return record


def _extract_listing_summary(content: str) -> str | None:
    text = re.sub(r"<[^>]+>", " ", content or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:220] if text else None


def _build_fallback_record(
    query: str,
    city: str | None,
    region: str | None,
    country: str | None,
    spec: SourceSpec,
    telemetry: dict | None = None,
) -> dict:
    location = city or country or "India"
    name = f"{location} {query.title()} {spec.label}".replace("  ", " ").strip()
    slug = slugify(name)
    url = f"https://{spec.key}.example.com/{slug}"
    domain = urlparse(url).netloc
    return {
        "name": name,
        "slug": slug,
        "website": None,
        "domain": domain,
        "industry": None,
        "subindustry": None,
        "city": city,
        "region": region,
        "country": country or spec.country_scope,
        "rating": 3.9,
        "reviews_count": 10,
        "description": f"{spec.label} fallback listing discovered for {query}.",
        "source_records": [
            {
                "source_type": spec.key,
                "source_key": slug,
                "source_url": url,
                "confidence": 0.5,
                "metadata": {"synthetic": True, "source_label": spec.label},
            }
        ],
        "metadata": {
            "provider": spec.key,
            "directory_sources": [spec.key],
            "business_type": spec.business_type,
            "categories": list(spec.categories),
            "crawl_telemetry": {
                **(telemetry or {}),
                "stage": "fallback_record",
                "parser_used": False,
            },
        },
    }


def _filter_detail_candidates(candidates: list[str], spec: SourceSpec) -> list[str]:
    filtered = []
    for url in candidates:
        domain = urlparse(url).netloc.replace("www.", "")
        if not domain:
            continue
        if spec.domain_patterns and not any(pattern.replace("www.", "") in domain for pattern in spec.domain_patterns):
            continue
        filtered.append(url)
    return list(dict.fromkeys(filtered))


def _merge_detail_payloads(base: dict, incoming: dict) -> dict:
    merged = dict(base)
    for field in ("name", "address", "phone", "website", "industry", "subindustry", "description"):
        if incoming.get(field) and not merged.get(field):
            merged[field] = incoming[field]

    if incoming.get("rating") is not None:
        merged["rating"] = max(incoming.get("rating") or 0, merged.get("rating") or 0) or None
    if incoming.get("reviews_count") is not None:
        merged["reviews_count"] = max(incoming.get("reviews_count") or 0, merged.get("reviews_count") or 0) or None

    merged["categories"] = list(
        dict.fromkeys([*(merged.get("categories", []) or []), *(incoming.get("categories", []) or [])])
    )
    merged["detail_candidates"] = list(
        dict.fromkeys([*(merged.get("detail_candidates", []) or []), *(incoming.get("detail_candidates", []) or [])])
    )
    return merged


def _filter_results_for_source(results: list[dict], spec: SourceSpec) -> list[dict]:
    if not spec.domain_patterns:
        return results
    filtered = [
        item
        for item in results
        if any(pattern in (item.get("domain") or "") for pattern in spec.domain_patterns)
    ]
    return filtered or results


def _build_search_telemetry(spec: SourceSpec, search_query: str, raw_results: list[dict], filtered_results: list[dict]) -> dict:
    return {
        "source": spec.key,
        "search_query": search_query,
        "raw_result_count": len(raw_results),
        "accepted_result_count": len(filtered_results),
        "source_mode": spec.mode,
        "rate_limit_per_minute": spec.rate_limit_per_minute,
    }
