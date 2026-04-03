from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import APIModel, MetricCard


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    full_name: str
    password: str
    role: str = "analyst"


class UserResponse(APIModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool


class AuthResponse(APIModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class OrganizationSummary(APIModel):
    id: UUID
    name: str
    slug: str
    plan: str
    status: str
    settings: dict


class MembershipSummary(APIModel):
    id: UUID
    role: str
    is_default: bool
    created_at: datetime
    organization: OrganizationSummary


class WorkspaceOverview(APIModel):
    user: dict
    memberships: list[MembershipSummary]
    default_organization: dict | None = None
    subscription: dict | None = None
    usage: dict
    api_keys: list[dict]
    audit_events: list[dict]


class OrganizationCreateRequest(BaseModel):
    name: str


class AdminOrganizationCreateRequest(BaseModel):
    name: str
    plan: str = "starter"
    status: str = "active"
    regions: list[str] = []


class AdminOrganizationUpdateRequest(BaseModel):
    name: str | None = None
    plan: str | None = None
    status: str | None = None
    regions: list[str] | None = None


class ApiKeyCreateRequest(BaseModel):
    organization_id: UUID
    name: str
    scopes: list[str] = []


class SeatInviteRequest(BaseModel):
    organization_id: UUID
    email: str
    role: str = "member"


class CheckoutSessionRequest(BaseModel):
    organization_id: UUID
    plan: str
    seats: int = 5


class PaymentMethodRequest(BaseModel):
    organization_id: UUID
    provider: str = "stripe"
    provider_customer_id: str | None = None
    provider_payment_method_id: str | None = None
    brand: str | None = None
    last4: str | None = None
    exp_month: int | None = None
    exp_year: int | None = None
    is_default: bool = True


class AdminUserCreateRequest(BaseModel):
    email: str
    full_name: str
    password: str
    role: str = "analyst"
    organization_id: UUID | None = None
    is_active: bool = True


class AdminUserUpdateRequest(BaseModel):
    full_name: str | None = None
    role: str | None = None
    is_active: bool | None = None


class AdminConfigUpdateRequest(BaseModel):
    crawler_concurrency: int | None = None
    crawler_max_retries: int | None = None
    default_region: str | None = None
    rate_limit_requests: int | None = None
    rate_limit_window_seconds: int | None = None


class AdminMembershipCreateRequest(BaseModel):
    organization_id: UUID
    user_id: UUID
    role: str = "member"
    is_default: bool = False


class AdminMembershipUpdateRequest(BaseModel):
    role: str | None = None
    is_default: bool | None = None


class AdminSubscriptionUpdateRequest(BaseModel):
    plan: str | None = None
    status: str | None = None
    seats: int | None = None
    search_quota: int | None = None
    export_quota: int | None = None
    crawl_quota: int | None = None


class AdminSupportTicketCreateRequest(BaseModel):
    organization_id: UUID | None = None
    title: str
    priority: str = "medium"
    status: str = "open"
    description: str
    assignee_user_id: UUID | None = None
    sla_label: str | None = None


class AdminSupportTicketUpdateRequest(BaseModel):
    priority: str | None = None
    status: str | None = None
    description: str | None = None
    assignee_user_id: UUID | None = None
    sla_label: str | None = None


class AdminSupportNoteCreateRequest(BaseModel):
    body: str


class AdminInvoiceUpdateRequest(BaseModel):
    status: str


class AdminInvoiceCreateRequest(BaseModel):
    organization_id: UUID
    amount: float
    seats: int = 1
    currency: str = "usd"
    status: str = "open"


class AdminPaymentMethodCreateRequest(BaseModel):
    organization_id: UUID
    provider: str = "manual"
    brand: str
    last4: str
    exp_month: int
    exp_year: int
    is_default: bool = True


class AdminCrawlerPresetCreateRequest(BaseModel):
    name: str
    mode: str = "discovery"
    query: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    source: str = "hybrid"
    keywords: list[str] = []
    industries: list[str] = []
    employee_range: str | None = None
    min_reviews: int | None = None
    max_rating: float | None = None
    has_website: bool | None = None
    grid: list[float] | None = None
    keyword_set: list[str] = []
    radius_km: int | None = None


class DiscoverySeedRequest(BaseModel):
    query: str
    city: str | None = None
    region: str | None = None
    country: str | None = None
    source: str = "public_web"
    keywords: list[str] = []
    industries: list[str] = []
    employee_range: str | None = None
    min_reviews: int | None = None
    max_rating: float | None = None
    has_website: bool | None = None


class GeoGridScanRequest(BaseModel):
    city: str
    region: str | None = None
    country: str | None = None
    grid: list[float]
    source: str = "hybrid"
    keyword_set: list[str] = []
    industries: list[str] = []
    radius_km: int | None = None


class BillingOverview(APIModel):
    organization: dict
    subscription: dict | None = None
    payment_methods: list[dict]
    invoices: list[dict]
    seat_invites: list[dict]
    seat_usage: dict
    plans: list[dict] = []
    portal_url: str | None = None


class CompanySummary(APIModel):
    id: UUID
    name: str
    slug: str
    industry: str | None = None
    city: str | None = None
    country: str | None = None
    website: str | None = None
    health_score: float
    growth_score: float
    opportunity_score: float
    enrichment: dict


class SignalItem(APIModel):
    id: UUID
    company_id: UUID
    type: str
    severity: str
    title: str
    description: str
    payload: dict
    created_at: datetime


class OpportunityItem(APIModel):
    id: UUID
    company_id: UUID
    category: str
    title: str
    description: str
    confidence: float
    estimated_value: float
    status: str
    payload: dict
    created_at: datetime


class CompanyDetail(CompanySummary):
    description: str | None = None
    ai_summary: str | None = None
    metadata: dict
    signals: list[SignalItem]
    opportunities: list[OpportunityItem]
    relationships: list[dict]
    sources: list[dict] = []


class SearchResponse(APIModel):
    query: str
    total: int
    results: list[CompanySummary]
    suggested_filters: list[str]
    applied_filters: dict


class DashboardResponse(APIModel):
    metrics: list[MetricCard]
    top_signals: list[SignalItem]
    top_opportunities: list[OpportunityItem]
    market_map: list[dict]
    heatmap: list[dict]


class AdminOverview(APIModel):
    queue_depth: int
    active_jobs: int
    dataset_size: int
    logs: list[dict]
    configs: dict
    users: list[dict]


class InsightResponse(APIModel):
    trend_cards: list[MetricCard]
    industry_trends: list[dict]
    city_heatmap: list[dict]
    tech_adoption: list[dict]


class SaveLeadRequest(BaseModel):
    user_id: UUID
    company_id: UUID
    notes: str | None = None


class ExportRequest(BaseModel):
    user_id: UUID | None = None
    export_type: str
    filters: dict = {}


class ExportResponse(APIModel):
    id: UUID
    export_type: str
    status: str
    file_url: str | None = None
    filters: dict


class AlertItem(APIModel):
    id: str
    title: str
    category: str
    severity: str
    description: str
    created_at: str
