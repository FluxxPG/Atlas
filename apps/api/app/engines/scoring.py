def compute_health_score(company: dict) -> float:
    rating = float(company.get("rating") or 0)
    reviews = int(company.get("reviews_count") or 0)
    enrichment = company.get("enrichment", {})
    digital_presence_score = float(enrichment.get("digital_presence_score") or 0)
    website_bonus = 10 if company.get("website") else -12
    crm_bonus = 6 if enrichment.get("crm") else 0
    social_bonus = 5 if enrichment.get("has_social_presence") else 0
    return round(min(100, max(0, rating * 16 + min(reviews / 6, 24) + website_bonus + crm_bonus + social_bonus + digital_presence_score * 0.15)), 2)


def compute_growth_score(company: dict) -> float:
    metadata = company.get("metadata", {})
    enrichment = company.get("enrichment", {})
    hiring = 18 if metadata.get("is_hiring") else 0
    traffic = min(float(metadata.get("traffic_growth", 0)), 30)
    expansions = 15 if metadata.get("expanding_regions") else 0
    directories = min(len(enrichment.get("directory_sources", [])) * 3, 12)
    reviews = min(int(company.get("reviews_count") or 0) / 10, 12)
    return round(min(100, 18 + hiring + traffic + expansions + directories + reviews), 2)


def compute_opportunity_score(company: dict) -> float:
    enrichment = company.get("enrichment", {})
    rating = float(company.get("rating") or 0)
    reviews = int(company.get("reviews_count") or 0)
    score = 28
    score += 18 if not company.get("website") else 0
    score += 10 if enrichment.get("directory_sources") and not company.get("website") else 0
    score += 12 if not enrichment.get("crm") else 0
    score += 15 if rating and rating < 3.8 and reviews > 25 else 0
    score += 10 if not enrichment.get("automation_tools") else 0
    score += 8 if not enrichment.get("has_social_presence") else 0
    score += 8 if float(enrichment.get("digital_presence_score") or 0) < 45 else 0
    return round(min(100, score), 2)
