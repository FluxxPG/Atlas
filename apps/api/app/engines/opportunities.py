def generate_opportunities(company: dict) -> list[dict]:
    opportunities: list[dict] = []
    enrichment = company.get("enrichment", {})
    metadata = company.get("metadata", {})
    rating = float(company.get("rating") or 0)
    reviews = int(company.get("reviews_count") or 0)
    website = company.get("website")
    industry = company.get("industry") or "Business Services"
    business_type = enrichment.get("business_type") or metadata.get("business_type") or "smb"
    directories = enrichment.get("directory_sources", [])
    digital_presence_score = int(enrichment.get("digital_presence_score") or 0)

    def add(category: str, title: str, description: str, confidence: float, estimated_value: float, payload: dict):
        if any(item["title"] == title for item in opportunities):
            return
        opportunities.append(
            {
                "category": category,
                "title": title,
                "description": description,
                "confidence": confidence,
                "estimated_value": estimated_value,
                "payload": payload,
            }
        )

    if not website:
        add(
            "website_development",
            "Website launch opportunity",
            "The business is discoverable but still depends on directory or phone-first discovery without an owned website.",
            90 if directories else 82,
            9000,
            {"directory_sources": directories, "business_type": business_type, "services": ["website", "landing-pages", "lead-capture"]},
        )

    if directories and not website:
        add(
            "marketing_needs",
            "Directory-to-brand conversion opportunity",
            "Directory visibility can be converted into owned acquisition with local SEO, maps optimization, and branded lead capture.",
            88,
            6500,
            {"channels": ["local-seo", "gbp-optimization", "maps", "review-generation"]},
        )

    if website and reviews < 20:
        add(
            "seo_needs",
            "SEO and local visibility opportunity",
            "The business has a website but weak review or search proof, suggesting a local SEO and reputation gap.",
            81,
            6000,
            {"channels": ["local-seo", "review-generation", "content"]},
        )

    if rating and rating < 3.8 and reviews >= 25:
        add(
            "marketing_needs",
            "Reputation recovery campaign",
            "Customer sentiment suggests a need for review recovery, service messaging, and brand trust improvements.",
            84,
            8500,
            {"channel": "reputation-management", "rating": rating, "reviews": reviews},
        )

    if not enrichment.get("has_social_presence"):
        add(
            "marketing_needs",
            "Social presence buildout",
            "The business lacks active social proof, which limits brand recall and local discovery.",
            72,
            3500,
            {"channels": ["instagram", "facebook", "content-calendar"]},
        )

    if not enrichment.get("crm"):
        add(
            "software_needs",
            "CRM modernization opportunity",
            "Sales and follow-up workflows appear unmanaged, creating a strong need for CRM adoption.",
            82,
            12000,
            {"recommended_stack": ["HubSpot", "Salesforce Starter", "Zoho CRM"]},
        )

    if metadata.get("is_hiring") and not enrichment.get("automation_tools"):
        add(
            "automation_needs",
            "Workflow automation rollout",
            "Hiring growth without automation indicates manual process strain across lead routing, support, and operations.",
            79,
            15000,
            {"focus": ["lead-routing", "support", "reporting", "internal-ops"]},
        )

    if industry in {"Hospitality", "Healthcare", "Education"} and not website:
        add(
            "software_development",
            "Lead capture and booking workflow build",
            "This category benefits from online bookings, inquiry forms, and conversion-first service pages.",
            83,
            11000,
            {"modules": ["forms", "booking", "calls", "whatsapp-capture"]},
        )

    if digital_presence_score < 45:
        add(
            "marketing_needs",
            "Digital presence acceleration",
            "Owned channels, reviews, and search presence are all underdeveloped and can be improved together.",
            78,
            7000,
            {"digital_presence_score": digital_presence_score, "lead_segments": enrichment.get("lead_segments", [])},
        )

    return opportunities
