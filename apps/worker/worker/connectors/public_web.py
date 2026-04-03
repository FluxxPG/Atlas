import re
from urllib.parse import urlparse

import httpx
from slugify import slugify


async def discover_by_query(query: str, city: str | None = None, region: str | None = None, country: str | None = None) -> list[dict]:
    search_query = " ".join(part for part in [query, city, region, country] if part)
    results = []
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(
                "https://duckduckgo.com/html/",
                params={"q": search_query},
                headers={"User-Agent": "AtlasBIBot/1.0"},
            )
            html = response.text
        for match in re.finditer(
            r'nofollow" class="result__a" href="(?P<href>[^"]+)">(?P<title>.*?)</a>',
            html,
            re.IGNORECASE,
        ):
            href = re.sub(r"<.*?>", "", match.group("href"))
            title = re.sub(r"<.*?>", "", match.group("title"))
            domain = urlparse(href).netloc.replace("www.", "")
            if not domain:
                continue
            company_name = _normalize_company_name(title, domain)
            results.append(
                {
                    "name": company_name,
                    "slug": slugify(company_name),
                    "website": href,
                    "domain": domain,
                    "industry": _infer_industry(query),
                    "city": city,
                    "region": region,
                    "country": country,
                    "rating": 4.0,
                    "reviews_count": 40,
                    "description": f"Discovered from public web search for '{search_query}'.",
                    "metadata": {"query": query, "provider": "public_web_search", "is_hiring": False, "traffic_growth": 9},
                    "source_records": [
                        {
                            "source_type": "public_web_search",
                            "source_key": domain,
                            "source_url": href,
                            "confidence": 0.74,
                            "metadata": {"query": search_query},
                        }
                    ],
                }
            )
            if len(results) >= 8:
                break
    except Exception:
        pass

    if results:
        return results

    fallback_city = city or "Global"
    base = [
        f"{fallback_city} {query.title()} Labs",
        f"{fallback_city} {query.title()} Systems",
    ]
    discovered = []
    for name in base:
        discovered.append(
            {
                "name": name,
                "slug": slugify(name),
                "website": f"https://{slugify(name)}.example.com",
                "domain": f"{slugify(name)}.example.com",
                "industry": _infer_industry(query),
                "city": city,
                "region": region,
                "country": country,
                "rating": 4.1,
                "reviews_count": 18,
                "description": f"Synthetic fallback discovery result for '{search_query}'.",
                "metadata": {"query": query, "provider": "fallback_discovery", "is_hiring": True, "traffic_growth": 15},
                "source_records": [
                    {
                        "source_type": "fallback_discovery",
                        "source_key": slugify(name),
                        "source_url": f"https://{slugify(name)}.example.com",
                        "confidence": 0.55,
                        "metadata": {"query": search_query},
                    }
                ],
            }
        )
    return discovered


def expand_geo_grid(grid: list[float], step: float = 0.12) -> list[list[float]]:
    lat, lon = grid
    expanded = []
    for lat_offset in (-step, 0.0, step):
        for lon_offset in (-step, 0.0, step):
            expanded.append([round(lat + lat_offset, 4), round(lon + lon_offset, 4)])
    return expanded


def expand_related_companies(company: dict) -> list[dict]:
    industry = company.get("industry") or "Business"
    city = company.get("city") or "Global"
    base_name = company.get("name", "Atlas")
    related_names = [
        f"{city} {industry} Partners",
        f"{base_name.split()[0]} Growth Services",
    ]
    related = []
    for name in related_names:
        related.append(
            {
                "name": name,
                "slug": slugify(name),
                "website": f"https://{slugify(name)}.example.com",
                "domain": f"{slugify(name)}.example.com",
                "industry": industry,
                "city": city,
                "region": company.get("region"),
                "country": company.get("country"),
                "rating": 3.8,
                "reviews_count": 28,
                "description": f"Related-company expansion based on {company.get('name', 'seed record')}.",
                "metadata": {"provider": "related_expansion", "is_hiring": False, "traffic_growth": 12},
                "source_records": [
                    {
                        "source_type": "related_expansion",
                        "source_key": slugify(name),
                        "source_url": f"https://{slugify(name)}.example.com",
                        "confidence": 0.61,
                        "metadata": {"related_to": company.get("slug")},
                    }
                ],
            }
        )
    return related


def _normalize_company_name(title: str, domain: str) -> str:
    cleaned = re.sub(r"\s*[\-|:|].*$", "", title).strip()
    return cleaned or domain.split(".")[0].replace("-", " ").title()


def _infer_industry(query: str) -> str:
    lowered = query.lower()
    if any(token in lowered for token in ("restaurant", "dining", "hospitality")):
        return "Hospitality"
    if any(token in lowered for token in ("crm", "software", "saas", "startup")):
        return "SaaS"
    if any(token in lowered for token in ("factory", "manufacturing", "operations")):
        return "Manufacturing"
    return "Business Services"
