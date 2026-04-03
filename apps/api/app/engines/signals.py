def generate_signals(company: dict) -> list[dict]:
    signals = []
    rating = float(company.get("rating") or 0)
    reviews = int(company.get("reviews_count") or 0)
    website = company.get("website")
    metadata = company.get("metadata", {})
    enrichment = company.get("enrichment", {})
    business_type = enrichment.get("business_type") or metadata.get("business_type")
    directories = enrichment.get("directory_sources", [])
    digital_presence_score = int(enrichment.get("digital_presence_score") or 0)

    if rating and rating < 3.8 and reviews >= 50:
        signals.append(
            {
                "type": "low_rating",
                "severity": "high",
                "title": "Low rating with high review volume",
                "description": "The business is visible in-market but customer sentiment is under pressure.",
                "payload": {"rating": rating, "reviews": reviews},
            }
        )
    if not website:
        signals.append(
            {
                "type": "no_website",
                "severity": "high" if directories else "medium",
                "title": "No website detected",
                "description": "The business lacks an owned web presence.",
                "payload": {"directory_sources": directories},
            }
        )
    if directories and not website:
        signals.append(
            {
                "type": "directory_only_presence",
                "severity": "high",
                "title": "Directory presence without owned channel",
                "description": "Listings are visible on local directories but there is no primary website.",
                "payload": {"directory_sources": directories, "business_type": business_type},
            }
        )
    if website and reviews < 20:
        signals.append(
            {
                "type": "weak_review_presence",
                "severity": "medium",
                "title": "Low review presence",
                "description": "The brand has a website but weak review proof for local search conversion.",
                "payload": {"reviews": reviews},
            }
        )
    if not enrichment.get("has_social_presence"):
        signals.append(
            {
                "type": "limited_social_presence",
                "severity": "medium",
                "title": "Limited social presence",
                "description": "Owned channels are missing or underdeveloped.",
                "payload": {"social_profiles": enrichment.get("social_profiles", [])},
            }
        )
    if metadata.get("is_hiring"):
        signals.append(
            {
                "type": "hiring_activity",
                "severity": "medium",
                "title": "Hiring activity detected",
                "description": "Active hiring suggests expansion or operational investment.",
                "payload": {"roles": metadata.get("open_roles", [])},
            }
        )
    if metadata.get("traffic_growth", 0) > 15:
        signals.append(
            {
                "type": "rapid_growth",
                "severity": "high",
                "title": "Rapid growth pattern",
                "description": "Traffic and market traction indicate strong upside.",
                "payload": {"traffic_growth": metadata.get("traffic_growth")},
            }
        )
    if digital_presence_score < 45:
        signals.append(
            {
                "type": "weak_digital_presence",
                "severity": "medium",
                "title": "Weak digital presence score",
                "description": "The business has a meaningful digital gap across website, social, and reviews.",
                "payload": {"digital_presence_score": digital_presence_score},
            }
        )

    return signals
