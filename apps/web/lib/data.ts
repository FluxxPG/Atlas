import "server-only";

import { apiJson, apiText, getSessionUser } from "@/lib/server-api";

export async function getDashboardData() {
  return apiJson("/dashboard", {
    metrics: [
      { label: "Companies indexed", value: 124823, delta: 12.8, meta: { window: "30d" } },
      { label: "Signals detected", value: 32817, delta: 24.1, meta: { window: "7d" } },
      { label: "Opportunities", value: 9172, delta: 18.4, meta: { window: "7d" } },
      { label: "Crawler coverage", value: "82 countries", delta: null, meta: { grids: 4120 } }
    ],
    top_signals: [],
    top_opportunities: [],
    market_map: [
      { label: "SaaS", value: 74 },
      { label: "Healthcare", value: 48 },
      { label: "Retail", value: 39 },
      { label: "Hospitality", value: 64 }
    ],
    heatmap: [
      { city: "Bengaluru", score: 89 },
      { city: "Mumbai", score: 77 },
      { city: "Delhi NCR", score: 73 },
      { city: "Hyderabad", score: 68 }
    ]
  });
}

export async function getAdminData() {
  const fallback = {
    queue_depth: 428,
    active_jobs: 37,
    dataset_size: 124823,
    analytics: {
      total_users: 84,
      active_users: 71,
      total_organizations: 18,
      total_companies: 124823,
      running_jobs: 37,
      queued_jobs: 428,
      plans: {
        starter: 5,
        growth: 9,
        enterprise: 4
      }
    },
    logs: [],
    jobs: [],
    organizations: [],
    configs: {
      crawler_concurrency: 20,
      crawler_max_retries: 5,
      default_region: "IN",
      rate_limit_requests: 120,
      rate_limit_window_seconds: 60
    },
    users: []
  };
  const [overview, logs, jobs, users, configs, analytics, organizations] = await Promise.all([
    apiJson("/admin/overview", fallback, { auth: true }),
    apiJson("/admin/logs", { items: [] }, { auth: true }),
    apiJson("/admin/jobs", { items: [] }, { auth: true }),
    apiJson("/admin/users", { items: [] }, { auth: true }),
    apiJson("/admin/configs", fallback.configs, { auth: true }),
    apiJson("/admin/analytics", fallback.analytics, { auth: true }),
    apiJson("/admin/organizations", { items: [] }, { auth: true })
  ]);

  return {
    ...overview,
    analytics,
    logs: logs.items.length ? logs.items : overview.logs,
    jobs: jobs.items,
    users: users.items,
    organizations: organizations.items,
    configs
  };
}

export async function getAdminOrganizationDetail(organizationId: string) {
  return apiJson(`/admin/organizations/${organizationId}`, {
    status: "not_found"
  }, { auth: true });
}

export async function getAdminInvoices() {
  return apiJson("/admin/invoices", { items: [] }, { auth: true });
}

export async function getAdminSupportTickets() {
  return apiJson("/admin/support", { items: [] }, { auth: true });
}

export async function getAdminSupportNotes(ticketId: string) {
  return apiJson(`/admin/support/${ticketId}/notes`, { items: [] }, { auth: true });
}

export async function getAdminPaymentMethods() {
  return apiJson("/admin/payment-methods", { items: [] }, { auth: true });
}

export async function getAdminCrawlerPresets() {
  return apiJson("/admin/crawler-presets", { items: [] }, { auth: true });
}

export async function getAdminConnectors() {
  return apiJson("/admin/connectors", { items: [] }, { auth: true });
}

export async function getAdminConnectorDetail(provider: string) {
  return apiJson(`/admin/connectors/${encodeURIComponent(provider)}`, {
    provider,
    summary: { company_count: 0, avg_rating: 0, avg_reviews: 0 },
    field_coverage: {},
    top_categories: [],
    sample_companies: [],
    recent_logs: []
  }, { auth: true });
}

export async function getInsightsData() {
  return apiJson("/insights", {
    trend_cards: [
      { label: "Hiring surge", value: 132, delta: 14.0, meta: { signal: "jobs" } },
      { label: "CRM whitespace", value: 486, delta: 6.2, meta: { segment: "SMB" } },
      { label: "Automation fit", value: 221, delta: 9.5, meta: { region: "India" } }
    ],
    industry_trends: [],
    city_heatmap: [],
    tech_adoption: []
  });
}

export async function getCompanies() {
  return apiJson("/company", { items: [], total: 0 });
}

export async function getCompaniesFiltered(params?: {
  limit?: number;
  country?: string;
  industry?: string;
  minOpportunityScore?: number;
}) {
  const query = new URLSearchParams();
  if (params?.limit) query.set("limit", String(params.limit));
  if (params?.country) query.set("country", params.country);
  if (params?.industry) query.set("industry", params.industry);
  if (params?.minOpportunityScore !== undefined) {
    query.set("min_opportunity_score", String(params.minOpportunityScore));
  }
  return apiJson(`/company?${query.toString()}`, { items: [], total: 0 });
}

export async function getCompanyBySlug(slug: string) {
  return apiJson(`/company/slug/${slug}`, null);
}

export async function getSearchResults(params: {
  q: string;
  limit?: number;
  country?: string;
  industry?: string;
  minOpportunityScore?: number;
  minGrowthScore?: number;
  sortBy?: "opportunity" | "growth";
}) {
  const query = new URLSearchParams();
  query.set("q", params.q);
  if (params.limit) query.set("limit", String(params.limit));
  if (params.country) query.set("country", params.country);
  if (params.industry) query.set("industry", params.industry);
  if (params.minOpportunityScore !== undefined) {
    query.set("min_opportunity_score", String(params.minOpportunityScore));
  }
  if (params.minGrowthScore !== undefined) {
    query.set("min_growth_score", String(params.minGrowthScore));
  }
  if (params.sortBy) query.set("sort_by", params.sortBy);
  return apiJson(`/search/advanced?${query.toString()}`, {
    query: params.q,
    total: 0,
    results: [],
    suggested_filters: [],
    applied_filters: {}
  });
}

export async function getSavedLeads() {
  return apiJson("/saved-leads", {
    items: [
      {
        id: "lead-1",
        user_id: "demo-user",
        company_id: "demo-company",
        notes: "High-fit CRM modernization account",
        created_at: new Date().toISOString()
      }
    ],
    total: 1
  });
}

export async function getAlerts() {
  return apiJson("/alerts", {
    items: [
      {
        id: "alert-1",
        title: "Hiring activity detected",
        category: "signal",
        severity: "medium",
        description: "Operations expansion detected in Bengaluru SaaS cluster.",
        created_at: new Date().toISOString()
      },
      {
        id: "alert-2",
        title: "CRM whitespace opportunity",
        category: "opportunity",
        severity: "high",
        description: "New hospitality account without CRM or website footprint.",
        created_at: new Date().toISOString()
      }
    ],
    total: 2
  });
}

export async function getExportPreview(type: "csv" | "json" | "excel") {
  const fallback = type === "json"
    ? JSON.stringify([{ name: "Bengaluru Growth Labs", industry: "SaaS" }], null, 2)
    : "name,industry\nBengaluru Growth Labs,SaaS";
  return apiText(`/exports/${type}/preview`, fallback);
}

export async function getWorkspaceData() {
  return apiJson("/workspace", {
    user: {
      id: "demo-user",
      email: "admin@atlasbi.local",
      full_name: "AtlasBI Admin",
      role: "admin"
    },
    memberships: [
      {
        id: "membership-1",
        role: "owner",
        is_default: true,
        created_at: new Date().toISOString(),
        organization: {
          id: "org-1",
          name: "AtlasBI Workspace",
          slug: "atlasbi-workspace",
          plan: "growth",
          status: "active",
          settings: { regions: ["India"], alerts_enabled: true }
        }
      }
    ],
    default_organization: {
      id: "org-1",
      name: "AtlasBI Workspace",
      slug: "atlasbi-workspace",
      plan: "growth",
      status: "active",
      settings: { regions: ["India"], alerts_enabled: true },
      member_count: 1
    },
    subscription: {
      plan: "growth",
      status: "active",
      seats: 10,
      search_quota: 10000,
      export_quota: 2500,
      crawl_quota: 5000,
      renews_at: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30).toISOString(),
      metadata: { tier: "growth", billing_cycle: "monthly" }
    },
    usage: {
      organizations: 1,
      searches: 184,
      exports: 19,
      crawls: 42,
      api_keys: 2
    },
    api_keys: [
      {
        id: "key-1",
        name: "Production Ingestion",
        key_prefix: "atlas_live_1",
        scopes: ["search:read", "company:read", "exports:create"],
        created_at: new Date().toISOString(),
        last_used_at: new Date().toISOString(),
        revoked_at: null
      }
    ],
    audit_events: [
      {
        id: "audit-1",
        action: "workspace.created",
        resource_type: "organization",
        resource_id: "org-1",
        payload: { name: "AtlasBI Workspace" },
        created_at: new Date().toISOString()
      },
      {
        id: "audit-2",
        action: "api_key.created",
        resource_type: "api_key",
        resource_id: "key-1",
        payload: { name: "Production Ingestion" },
        created_at: new Date().toISOString()
      }
    ]
  });
}

export async function getBillingData() {
  return apiJson("/billing/overview", {
    organization: {
      id: "org-1",
      name: "AtlasBI Workspace",
      slug: "atlasbi-workspace",
      plan: "growth",
      status: "active"
    },
    subscription: {
      plan: "growth",
      status: "active",
      seats: 10,
      search_quota: 10000,
      export_quota: 2500,
      crawl_quota: 5000,
      renews_at: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30).toISOString(),
      metadata: { tier: "growth", billing_cycle: "monthly" }
    },
    payment_methods: [
      {
        id: "pm-1",
        provider: "stripe",
        brand: "Visa",
        last4: "4242",
        exp_month: 12,
        exp_year: new Date().getFullYear() + 2,
        is_default: true
      }
    ],
    invoices: [
      {
        id: "inv-1",
        status: "open",
        amount: 199,
        currency: "usd",
        seats: 10,
        hosted_invoice_url: "https://billing.atlasbi.local/invoices/demo",
        created_at: new Date().toISOString(),
        due_at: new Date(Date.now() + 1000 * 60 * 60 * 24 * 14).toISOString()
      }
    ],
    seat_invites: [
      {
        id: "invite-1",
        email: "ops@atlasbi.local",
        role: "analyst",
        status: "pending",
        expires_at: new Date(Date.now() + 1000 * 60 * 60 * 24 * 7).toISOString(),
        created_at: new Date().toISOString()
      }
    ],
    seat_usage: {
      assigned: 4,
      pending: 1,
      capacity: 10
    },
    plans: [
      { id: "starter", label: "Starter", monthly_price: 99, included_seats: 5, search_quota: 2500, export_quota: 500, crawl_quota: 1000 },
      { id: "growth", label: "Growth", monthly_price: 199, included_seats: 10, search_quota: 10000, export_quota: 2500, crawl_quota: 5000 },
      { id: "enterprise", label: "Enterprise", monthly_price: 499, included_seats: 25, search_quota: 50000, export_quota: 10000, crawl_quota: 25000 }
    ],
    portal_url: "http://localhost:3000/billing"
  });
}

export async function getSessionData() {
  return getSessionUser();
}
