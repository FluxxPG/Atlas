def build_relationships(company: dict) -> list[dict]:
    enrichment = company.get("enrichment", {})
    technologies = enrichment.get("technology_stack", [])
    relationships = []
    for technology in technologies:
        relationships.append(
            {
                "relationship_type": "uses_technology",
                "weight": 0.8,
                "metadata": {"technology": technology},
            }
        )
    if company.get("industry"):
        relationships.append(
            {
                "relationship_type": "belongs_to_industry",
                "weight": 0.9,
                "metadata": {"industry": company["industry"]},
            }
        )
    return relationships

