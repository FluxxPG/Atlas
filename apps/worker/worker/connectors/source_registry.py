from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceSpec:
    key: str
    label: str
    mode: str
    site_query: str | None = None
    domain_patterns: tuple[str, ...] = ()
    business_type: str = "smb"
    country_scope: str | None = None
    policy: str = "approved"
    rate_limit_per_minute: int = 12
    requires_playwright: bool = False
    notes: str | None = None
    query_suffixes: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()


SOURCE_REGISTRY: dict[str, SourceSpec] = {
    "public_web": SourceSpec(
        key="public_web",
        label="Public Web Search",
        mode="search",
        policy="approved",
        rate_limit_per_minute=30,
    ),
    "serpapi": SourceSpec(
        key="serpapi",
        label="SerpAPI Search",
        mode="search",
        policy="approved",
        rate_limit_per_minute=30,
    ),
    "india_local": SourceSpec(
        key="india_local",
        label="India Local Mix",
        mode="aggregator",
        country_scope="India",
        policy="approved",
        rate_limit_per_minute=18,
    ),
    "google_business_profiles": SourceSpec(
        key="google_business_profiles",
        label="Google Business Profile",
        mode="directory",
        site_query="site:google.com/maps",
        domain_patterns=("google.com", "maps.google.com"),
        business_type="local_business",
        country_scope="India",
        rate_limit_per_minute=10,
        requires_playwright=True,
        categories=("Local", "Maps"),
    ),
    "google_maps": SourceSpec(
        key="google_maps",
        label="Google Maps",
        mode="directory",
        site_query="site:google.com",
        domain_patterns=("google.com", "maps.google.com"),
        business_type="local_business",
        country_scope="India",
        rate_limit_per_minute=10,
        requires_playwright=True,
        categories=("Local", "Maps"),
    ),
    "justdial": SourceSpec(
        key="justdial",
        label="Justdial",
        mode="directory",
        site_query="site:justdial.com",
        domain_patterns=("justdial.com",),
        business_type="local_business",
        country_scope="India",
        rate_limit_per_minute=8,
        requires_playwright=True,
        categories=("Local", "Directory"),
    ),
    "sulekha": SourceSpec(
        key="sulekha",
        label="Sulekha",
        mode="directory",
        site_query="site:sulekha.com",
        domain_patterns=("sulekha.com",),
        business_type="local_business",
        country_scope="India",
        rate_limit_per_minute=8,
        requires_playwright=True,
        categories=("Local", "Directory"),
    ),
    "tracxn": SourceSpec(
        key="tracxn",
        label="Tracxn",
        mode="directory",
        site_query="site:tracxn.com",
        domain_patterns=("tracxn.com",),
        business_type="startup",
        country_scope="India",
        rate_limit_per_minute=8,
        requires_playwright=True,
        categories=("Startup", "Technology"),
    ),
    "indiamart": SourceSpec(
        key="indiamart",
        label="IndiaMART",
        mode="directory",
        site_query="site:indiamart.com",
        domain_patterns=("indiamart.com",),
        business_type="supplier",
        country_scope="India",
        rate_limit_per_minute=8,
        requires_playwright=True,
        categories=("Supplier", "Manufacturing"),
    ),
}


INDIA_DIRECTORY_KEYS = tuple(
    key for key, spec in SOURCE_REGISTRY.items() if spec.country_scope == "India" and spec.mode == "directory"
)


def get_source_spec(key: str | None) -> SourceSpec:
    normalized = (key or "public_web").lower()
    return SOURCE_REGISTRY.get(normalized, SOURCE_REGISTRY["public_web"])


def list_source_specs() -> list[SourceSpec]:
    return list(SOURCE_REGISTRY.values())
