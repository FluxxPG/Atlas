import html
import json
import re
from typing import Callable


def parse_directory_page(source_key: str, page: dict) -> dict:
    parser = PARSER_REGISTRY.get(source_key, _parse_generic_directory_page)
    return parser(page)


def _parse_generic_directory_page(page: dict) -> dict:
    content = page.get("content", "")
    title = page.get("title")
    categories = _extract_categories(content)
    return {
        "title": title,
        "name": _normalize_listing_name(title),
        "address": _extract_address(content),
        "phone": _extract_phone(content),
        "website": _extract_website(content),
        "rating": _extract_rating(content),
        "reviews_count": _extract_reviews_count(content),
        "categories": categories,
        "industry": _infer_industry_from_categories(categories),
        "subindustry": categories[0] if categories else None,
        "detail_candidates": _extract_detail_candidates(content),
        "pagination_candidates": _extract_pagination_candidates(content),
        "description": _extract_summary(content),
    }


def _parse_google_like_page(page: dict) -> dict:
    payload = _parse_generic_directory_page(page)
    content = page.get("content", "")
    ld_json = _extract_json_ld(content)
    if ld_json:
        payload["name"] = payload.get("name") or ld_json.get("name")
        payload["title"] = payload.get("title") or ld_json.get("name")
        payload["address"] = payload.get("address") or _json_ld_address(ld_json.get("address"))
        payload["phone"] = payload.get("phone") or ld_json.get("telephone")
        payload["website"] = payload.get("website") or ld_json.get("url")
        payload["rating"] = payload.get("rating") or _safe_float((ld_json.get("aggregateRating") or {}).get("ratingValue"))
        payload["reviews_count"] = payload.get("reviews_count") or _safe_int((ld_json.get("aggregateRating") or {}).get("reviewCount"))
    return payload


def _parse_justdial_page(page: dict) -> dict:
    payload = _parse_generic_directory_page(page)
    content = page.get("content", "")
    payload["categories"] = payload.get("categories") or _extract_tagged_values(content, ("category", "categories"))
    payload["address"] = payload.get("address") or _extract_tagged_text(content, ("address", "location"))
    payload["phone"] = payload.get("phone") or _extract_tagged_text(content, ("phone", "mobile"))
    return payload


def _parse_sulekha_page(page: dict) -> dict:
    payload = _parse_generic_directory_page(page)
    content = page.get("content", "")
    payload["categories"] = payload.get("categories") or _extract_tagged_values(content, ("service", "services"))
    payload["description"] = payload.get("description") or _extract_meta_description(content)
    return payload


def _parse_tracxn_page(page: dict) -> dict:
    payload = _parse_generic_directory_page(page)
    content = page.get("content", "")
    payload["categories"] = list(dict.fromkeys([*(payload.get("categories") or []), *["Startup", "Technology"]]))
    payload["industry"] = payload.get("industry") or "SaaS"
    payload["subindustry"] = payload.get("subindustry") or "B2B Software"
    payload["description"] = payload.get("description") or _extract_meta_description(content)
    return payload


def _parse_indiamart_page(page: dict) -> dict:
    payload = _parse_generic_directory_page(page)
    content = page.get("content", "")
    payload["categories"] = list(dict.fromkeys([*(payload.get("categories") or []), *["Supplier", "Manufacturing"]]))
    payload["industry"] = payload.get("industry") or "Manufacturing"
    payload["subindustry"] = payload.get("subindustry") or "Suppliers"
    payload["address"] = payload.get("address") or _extract_tagged_text(content, ("address", "city"))
    return payload


def _extract_json_ld(content: str) -> dict | None:
    matches = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', content, re.IGNORECASE | re.DOTALL)
    for match in matches:
        try:
            payload = json.loads(html.unescape(match.strip()))
        except Exception:
            continue
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    return item
    return None


def _json_ld_address(address: object) -> str | None:
    if isinstance(address, str):
        return address
    if not isinstance(address, dict):
        return None
    parts = [
        address.get("streetAddress"),
        address.get("addressLocality"),
        address.get("addressRegion"),
        address.get("postalCode"),
        address.get("addressCountry"),
    ]
    return ", ".join(part for part in parts if part)


def _extract_summary(content: str) -> str | None:
    description = _extract_meta_description(content)
    if description:
        return description
    text = re.sub(r"<[^>]+>", " ", content or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:240] if text else None


def _extract_meta_description(content: str) -> str | None:
    match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', content, re.IGNORECASE)
    return html.unescape(match.group(1)).strip() if match else None


def _extract_address(content: str) -> str | None:
    return _extract_tagged_text(content, ("address", "location"))


def _extract_phone(content: str) -> str | None:
    text = re.sub(r"<[^>]+>", " ", content or "")
    match = re.search(r"(\+?\d[\d\-\s]{8,}\d)(?=\s+(?:\d(?:\.\d)?\s*(?:/ ?5|stars?|rating)|\d[\d,]*\s*(?:reviews?|ratings?)|$))", text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _extract_website(content: str) -> str | None:
    match = re.search(r'https?://[^\s"\'<>]+', content or "", re.IGNORECASE)
    return match.group(0) if match else None


def _extract_rating(content: str) -> float | None:
    match = re.search(r'([1-5](?:\.\d)?)\s*(?:/ ?5|stars?|rating)', re.sub(r"<[^>]+>", " ", content or ""), re.IGNORECASE)
    return _safe_float(match.group(1)) if match else None


def _extract_reviews_count(content: str) -> int | None:
    text = re.sub(r"<[^>]+>", " ", content or "")
    match = re.search(r'(?<![\d.])(\d[\d,]*)\s*(?:reviews?|ratings?)', text, re.IGNORECASE)
    return _safe_int(match.group(1).replace(",", "")) if match else None


def _extract_categories(content: str) -> list[str]:
    values = _extract_tagged_values(content, ("category", "categories", "service", "services"))
    return list(dict.fromkeys(values))


def _extract_detail_candidates(content: str) -> list[str]:
    urls = re.findall(r'https?://[^\s"\'<>]+', content or "", re.IGNORECASE)
    return list(dict.fromkeys(urls[:5]))


def _extract_pagination_candidates(content: str) -> list[str]:
    urls = re.findall(r'https?://[^\s"\'<>]+', content or "", re.IGNORECASE)
    pagination = []
    for url in urls:
        lowered = url.lower()
        if any(token in lowered for token in ("page=", "/page/", "&page", "pageno=", "start=", "page-", "/p/")):
            pagination.append(url)
    return list(dict.fromkeys(pagination[:5]))


def _normalize_listing_name(title: str | None) -> str | None:
    if not title:
        return None
    cleaned = re.sub(r"\s*[-|].*$", "", title).strip()
    return cleaned or title


def _infer_industry_from_categories(categories: list[str]) -> str | None:
    lowered = " ".join(categories).lower()
    if any(token in lowered for token in ("restaurant", "cafe", "dining", "hotel", "hospitality")):
        return "Hospitality"
    if any(token in lowered for token in ("clinic", "hospital", "dentist", "health")):
        return "Healthcare"
    if any(token in lowered for token in ("software", "startup", "technology", "saas")):
        return "SaaS"
    if any(token in lowered for token in ("supplier", "manufacturing", "industrial")):
        return "Manufacturing"
    if any(token in lowered for token in ("school", "academy", "education")):
        return "Education"
    return None


def _extract_tagged_text(content: str, labels: tuple[str, ...]) -> str | None:
    text = re.sub(r"<[^>]+>", " ", content or "")
    for label in labels:
        match = re.search(
            rf"{label}\s*[:\-]\s*(.+?)(?=\s+(?:{'|'.join(labels)}|phone|mobile|category|categories|service|services|\d(?:\.\d)?\s*(?:/ ?5|stars?|rating)|\d[\d,]*\s*(?:reviews?|ratings?)|$))",
            text,
            re.IGNORECASE,
        )
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip(" ,.-")
    return None


def _extract_tagged_values(content: str, labels: tuple[str, ...]) -> list[str]:
    found: list[str] = []
    text = re.sub(r"<[^>]+>", " ", content or "")
    for label in labels:
        match = re.search(
            rf"{label}\s*[:\-]\s*(.+?)(?=\s+(?:address|location|phone|mobile|service|services|category|categories|\d(?:\.\d)?\s*(?:/ ?5|stars?|rating)|\d[\d,]*\s*(?:reviews?|ratings?)|$))",
            text,
            re.IGNORECASE,
        )
        if match:
            raw = match.group(1)
            found.extend(part.strip() for part in re.split(r"[,/|]", raw) if part.strip())
    return found


def _safe_float(value: object) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _safe_int(value: object) -> int | None:
    try:
        return int(value)
    except Exception:
        return None


PARSER_REGISTRY: dict[str, Callable[[dict], dict]] = {
    "google_business_profiles": _parse_google_like_page,
    "google_maps": _parse_google_like_page,
    "justdial": _parse_justdial_page,
    "sulekha": _parse_sulekha_page,
    "tracxn": _parse_tracxn_page,
    "indiamart": _parse_indiamart_page,
}
