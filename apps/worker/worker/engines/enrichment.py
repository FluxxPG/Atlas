import re


DIRECTORY_TOKENS = {
    "google_business_profiles": ["google business", "google maps", "maps.google"],
    "justdial": ["justdial"],
    "sulekha": ["sulekha"],
    "tracxn": ["tracxn"],
    "indiamart": ["indiamart"],
}

CATEGORY_PATTERNS = {
    "Restaurants": ["restaurant", "cafe", "dining", "food"],
    "Beauty & Wellness": ["salon", "spa", "wellness", "beauty"],
    "Healthcare": ["clinic", "hospital", "dentist", "medical"],
    "Education": ["academy", "school", "coaching", "education"],
    "Real Estate": ["property", "real estate", "builder"],
    "Manufacturing": ["factory", "manufacturing", "industrial"],
    "Business Services": ["agency", "consulting", "marketing", "services"],
    "Software": ["saas", "software", "startup", "crm", "automation"],
}


def enrich_company(raw: dict) -> dict:
    html = raw.get("content", "")
    lowered = html.lower()
    website = raw.get("website")
    metadata = raw.get("metadata", {}) or {}
    source_records = raw.get("source_records", []) or []

    emails = sorted(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html)))
    phones = sorted(set(re.findall(r"\+?\d[\d\-\s]{8,}\d", html)))
    social = []
    for token in ["linkedin.com", "facebook.com", "instagram.com", "x.com", "youtube.com"]:
        if token in lowered:
            social.append(token)

    technologies = []
    for tech in ["shopify", "hubspot", "wordpress", "salesforce", "zapier", "zoho", "meta pixel", "google analytics"]:
        if tech in lowered:
            technologies.append(tech)

    directory_sources = _detect_directory_sources(lowered, metadata, source_records)
    categories = _detect_categories(lowered, raw)
    business_type = _infer_business_type(raw, directory_sources, categories)
    presence_channels = _detect_presence_channels(website, social, directory_sources)
    digital_presence_score = _compute_digital_presence_score(website, social, directory_sources, technologies, raw)
    service_gaps = _detect_service_gaps(raw, website, social, technologies, directory_sources, digital_presence_score)

    return {
        "emails": emails[:10],
        "phones": list(dict.fromkeys([*phones[:10], metadata.get("contact_phone")] if metadata.get("contact_phone") else phones[:10])),
        "social_profiles": social,
        "technology_stack": technologies,
        "crm": any(tool in technologies for tool in {"hubspot", "salesforce", "zoho"}),
        "automation_tools": [tool for tool in technologies if tool in {"zapier"}],
        "directory_sources": directory_sources,
        "categories": categories,
        "business_category": categories[0] if categories else raw.get("industry"),
        "business_type": business_type,
        "presence_channels": presence_channels,
        "digital_presence_score": digital_presence_score,
        "lead_segments": service_gaps,
        "has_contact_number": bool(phones or metadata.get("contact_phone")),
        "has_social_presence": bool(social),
        "has_directory_presence": bool(directory_sources),
    }


def merge_directory_website_profile(company: dict, enrichment: dict) -> dict:
    metadata = company.get("metadata", {}) or {}
    merged_metadata = {
        **metadata,
        "directory_profile": {
            "provider": metadata.get("provider"),
            "directory_sources": enrichment.get("directory_sources", []),
            "categories": enrichment.get("categories", []),
            "contact_phone": metadata.get("contact_phone"),
            "address": metadata.get("address"),
            "detail_candidates": metadata.get("detail_candidates", []),
        },
        "connector_diagnostics": summarize_connector_diagnostics(company),
    }

    return {
        **company,
        "industry": company.get("industry") or enrichment.get("business_category"),
        "subindustry": company.get("subindustry") or (enrichment.get("categories") or [None])[0],
        "metadata": merged_metadata,
        "enrichment": {
            **enrichment,
            "normalized_channels": _normalized_channels(enrichment),
            "data_completeness_score": _data_completeness_score(company, enrichment),
        },
    }


def summarize_connector_diagnostics(company: dict) -> dict:
    metadata = company.get("metadata", {}) or {}
    telemetry = metadata.get("crawl_telemetry", {}) or {}
    return {
        "provider": metadata.get("provider"),
        "stage": telemetry.get("stage"),
        "parser_used": telemetry.get("parser_used", False),
        "listing_pages_count": telemetry.get("listing_pages_count", 0),
        "detail_pages_count": telemetry.get("detail_pages_count", 0),
        "raw_result_count": telemetry.get("raw_result_count", 0),
        "accepted_result_count": telemetry.get("accepted_result_count", 0),
    }


def _detect_directory_sources(lowered: str, metadata: dict, source_records: list[dict]) -> list[str]:
    sources = list(metadata.get("directory_sources", []))
    for key, tokens in DIRECTORY_TOKENS.items():
        if any(token in lowered for token in tokens):
            sources.append(key)
    for record in source_records:
        source_type = record.get("source_type")
        if source_type:
            sources.append(source_type)
    return list(dict.fromkeys(sources))


def _detect_categories(lowered: str, raw: dict) -> list[str]:
    categories = list((raw.get("metadata") or {}).get("categories", []))
    if raw.get("industry"):
        categories.append(raw["industry"])
    for category, patterns in CATEGORY_PATTERNS.items():
        if any(pattern in lowered for pattern in patterns):
            categories.append(category)
    return list(dict.fromkeys(categories))


def _infer_business_type(raw: dict, directory_sources: list[str], categories: list[str]) -> str:
    metadata = raw.get("metadata", {}) or {}
    if metadata.get("business_type"):
        return metadata["business_type"]
    if "tracxn" in directory_sources or "Software" in categories or raw.get("industry") == "SaaS":
        return "startup"
    if any(source in directory_sources for source in {"google_business_profiles", "google_maps", "justdial", "sulekha"}):
        return "local_business"
    if "Manufacturing" in categories:
        return "supplier"
    return "smb"


def _detect_presence_channels(website: str | None, social: list[str], directory_sources: list[str]) -> list[str]:
    channels = []
    if website:
        channels.append("website")
    if social:
        channels.append("social")
    if directory_sources:
        channels.append("directory")
    return channels


def _compute_digital_presence_score(
    website: str | None,
    social: list[str],
    directory_sources: list[str],
    technologies: list[str],
    raw: dict,
) -> int:
    score = 0
    if website:
        score += 35
    if social:
        score += min(20, len(social) * 7)
    if directory_sources:
        score += min(15, len(directory_sources) * 4)
    if technologies:
        score += min(15, len(technologies) * 4)
    if int(raw.get("reviews_count") or 0) >= 25:
        score += 10
    if float(raw.get("rating") or 0) >= 4.0:
        score += 5
    return min(100, score)


def _detect_service_gaps(
    raw: dict,
    website: str | None,
    social: list[str],
    technologies: list[str],
    directory_sources: list[str],
    digital_presence_score: int,
) -> list[str]:
    gaps: list[str] = []
    rating = float(raw.get("rating") or 0)
    reviews = int(raw.get("reviews_count") or 0)

    if not website:
        gaps.append("website_development")
    if not social:
        gaps.append("social_media_management")
    if website and reviews < 25:
        gaps.append("seo")
    if rating and rating < 3.8 and reviews >= 25:
        gaps.append("reputation_management")
    if not any(tool in technologies for tool in {"hubspot", "salesforce", "zoho"}):
        gaps.append("crm")
    if "zapier" not in technologies:
        gaps.append("automation")
    if directory_sources and not website:
        gaps.append("directory_to_owned_media")
    if digital_presence_score < 45:
        gaps.append("digital_presence")
    if (raw.get("industry") or "") in {"Hospitality", "Healthcare", "Education"} and not website:
        gaps.append("local_lead_capture")

    return list(dict.fromkeys(gaps))


def _normalized_channels(enrichment: dict) -> list[str]:
    channels = []
    if enrichment.get("has_directory_presence"):
        channels.append("directory")
    if enrichment.get("has_social_presence"):
        channels.append("social")
    if enrichment.get("presence_channels"):
        channels.extend(enrichment.get("presence_channels", []))
    return list(dict.fromkeys(channels))


def _data_completeness_score(company: dict, enrichment: dict) -> int:
    score = 0
    if company.get("name"):
        score += 10
    if company.get("website"):
        score += 20
    if enrichment.get("phones"):
        score += 15
    if enrichment.get("emails"):
        score += 15
    if enrichment.get("categories"):
        score += 10
    if company.get("rating") is not None:
        score += 10
    if company.get("reviews_count"):
        score += 10
    if company.get("city"):
        score += 10
    return min(100, score)
