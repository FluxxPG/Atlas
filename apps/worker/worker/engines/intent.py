def detect_buyer_intent(company: dict) -> dict:
    metadata = company.get("metadata", {})
    enrichment = company.get("enrichment", {})
    return {
        "hiring_signal": bool(metadata.get("is_hiring")),
        "expansion_signal": bool(metadata.get("expanding_regions")),
        "tech_change_signal": bool(enrichment.get("new_technology_detected")),
        "intent_score": min(
            100,
            (25 if metadata.get("is_hiring") else 0)
            + (35 if metadata.get("expanding_regions") else 0)
            + (20 if enrichment.get("new_technology_detected") else 0)
            + (20 if metadata.get("traffic_growth", 0) > 10 else 0),
        ),
    }
