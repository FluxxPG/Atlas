from slugify import slugify


def discover_companies_from_seed(seed: dict) -> list[dict]:
    city = seed["city"]
    region = seed["region"]
    country = seed["country"]
    locality = city.lower().replace(" ", "-")

    return [
        {
            "name": f"{city} Smile Dental Clinic",
            "slug": slugify(f"{city} Smile Dental Clinic"),
            "website": None,
            "industry": "Healthcare",
            "subindustry": "Clinics",
            "city": city,
            "region": region,
            "country": country,
            "rating": 4.1,
            "reviews_count": 86,
            "description": f"Google Business Profile-style dental clinic listing discovered in {city}.",
            "metadata": {
                "is_hiring": False,
                "traffic_growth": 10,
                "expanding_regions": [],
                "directory_sources": ["google_business_profiles", "justdial"],
                "business_type": "local_business",
                "categories": ["Healthcare", "Clinics"],
                "contact_phone": "+91 99887 66554",
            },
        },
        {
            "name": f"{city} Dining Collective",
            "slug": slugify(f"{city} Dining Collective"),
            "website": None,
            "industry": "Hospitality",
            "subindustry": "Restaurants",
            "city": city,
            "region": region,
            "country": country,
            "rating": 3.3,
            "reviews_count": 278,
            "description": f"Multi-location restaurant operator listed across Google Maps and Sulekha in {city}.",
            "metadata": {
                "is_hiring": False,
                "traffic_growth": 12,
                "expanding_regions": [],
                "directory_sources": ["google_maps", "sulekha"],
                "business_type": "local_business",
                "categories": ["Hospitality", "Restaurants"],
                "contact_phone": "+91 99770 11223",
            },
        },
        {
            "name": f"{city} Growth Labs",
            "slug": slugify(f"{city} Growth Labs"),
            "website": f"https://{locality}-growthlabs.example.com",
            "industry": "SaaS",
            "subindustry": "B2B Software",
            "city": city,
            "region": region,
            "country": country,
            "rating": 4.2,
            "reviews_count": 126,
            "description": f"High-growth technology company discovered in {city} through Tracxn-style startup signals.",
            "metadata": {
                "is_hiring": True,
                "traffic_growth": 22,
                "expanding_regions": ["APAC"],
                "directory_sources": ["tracxn"],
                "business_type": "startup",
                "categories": ["SaaS", "B2B Software"],
            },
        },
    ]
