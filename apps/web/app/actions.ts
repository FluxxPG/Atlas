"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { getDefaultAppPath } from "@/lib/access";
import { apiRequest, clearSessionToken, getSessionToken, setSessionToken } from "@/lib/server-api";

export type FormState = {
  status: "idle" | "success" | "error";
  message?: string;
  token?: string;
  id?: string;
};

function listFromCsv(value: FormDataEntryValue | null) {
  return String(value ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export async function loginAction(_: FormState, formData: FormData): Promise<FormState> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");

  if (!email || !password) {
    return { status: "error", message: "Email and password are required." };
  }

  const response = await apiRequest("/auth/login", {
    method: "POST",
    body: { email, password }
  });

  if (!response.ok) {
    return { status: "error", message: "Invalid credentials." };
  }

  const payload = await response.json();
  setSessionToken(payload.access_token);
  revalidatePath("/");
  redirect(getDefaultAppPath(payload.user ?? null));
}

export async function logoutAction() {
  clearSessionToken();
  revalidatePath("/");
  redirect("/");
}

export async function queueIndiaSeedAction() {
  if (!getSessionToken()) {
    redirect("/login");
  }
  await apiRequest("/admin/jobs/seed", { method: "POST", auth: true });
  revalidatePath("/superadmin");
}

export async function rebuildInsightsAction() {
  if (!getSessionToken()) {
    redirect("/login");
  }
  await apiRequest("/admin/insights/rebuild", { method: "POST", auth: true });
  revalidatePath("/superadmin");
  revalidatePath("/insights");
}

export async function rebuildEmbeddingsAction() {
  if (!getSessionToken()) {
    redirect("/login");
  }
  await apiRequest("/admin/embeddings/rebuild", { method: "POST", auth: true });
  revalidatePath("/superadmin");
}

export async function queueDiscoveryAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const query = String(formData.get("query") ?? "").trim();
  const city = String(formData.get("city") ?? "").trim() || undefined;
  const region = String(formData.get("region") ?? "").trim() || undefined;
  const country = String(formData.get("country") ?? "").trim() || undefined;
  const source = String(formData.get("source") ?? "hybrid").trim();
  const keywords = listFromCsv(formData.get("keywords"));
  const industries = listFromCsv(formData.get("industries"));
  const employeeRange = String(formData.get("employee_range") ?? "").trim() || undefined;
  const minReviewsValue = String(formData.get("min_reviews") ?? "").trim();
  const maxRatingValue = String(formData.get("max_rating") ?? "").trim();
  const hasWebsiteValue = String(formData.get("has_website") ?? "").trim();

  if (!query) {
    return { status: "error", message: "A discovery query is required." };
  }

  const response = await apiRequest("/admin/jobs/discover", {
    method: "POST",
    auth: true,
    body: {
      query,
      city,
      region,
      country,
      source,
      keywords,
      industries,
      employee_range: employeeRange,
      min_reviews: minReviewsValue ? Number(minReviewsValue) : undefined,
      max_rating: maxRatingValue ? Number(maxRatingValue) : undefined,
      has_website: hasWebsiteValue ? hasWebsiteValue === "true" : undefined
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Discovery job could not be queued." };
  }

  const payload = await response.json();
  revalidatePath("/superadmin");
  return { status: "success", message: `Discovery queued for ${query}.`, id: payload.job_id };
}

export async function queueGeoGridAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const city = String(formData.get("city") ?? "").trim();
  const region = String(formData.get("region") ?? "").trim() || undefined;
  const country = String(formData.get("country") ?? "").trim() || undefined;
  const source = String(formData.get("source") ?? "hybrid").trim();
  const keywordSet = listFromCsv(formData.get("keyword_set"));
  const industries = listFromCsv(formData.get("industries"));
  const radiusValue = String(formData.get("radius_km") ?? "").trim();
  const latitude = Number(formData.get("latitude") ?? 0);
  const longitude = Number(formData.get("longitude") ?? 0);

  if (!city || Number.isNaN(latitude) || Number.isNaN(longitude)) {
    return { status: "error", message: "City and valid coordinates are required." };
  }

  const response = await apiRequest("/admin/jobs/geo-grid", {
    method: "POST",
    auth: true,
    body: {
      city,
      region,
      country,
      source,
      grid: [latitude, longitude],
      keyword_set: keywordSet,
      industries,
      radius_km: radiusValue ? Number(radiusValue) : undefined
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Geo-grid job could not be queued." };
  }

  const payload = await response.json();
  revalidatePath("/superadmin");
  return { status: "success", message: `Geo grid queued for ${city}.`, id: payload.job_id };
}

export async function createApiKeyAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim();
  const name = String(formData.get("name") ?? "").trim();
  const scopesValue = String(formData.get("scopes") ?? "").trim();
  const scopes = scopesValue
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  if (!organizationId || !name) {
    return { status: "error", message: "Organization and key name are required." };
  }

  const response = await apiRequest("/workspace/api-keys", {
    method: "POST",
    auth: true,
    body: { organization_id: organizationId, name, scopes }
  });

  if (!response.ok) {
    return { status: "error", message: "API key could not be created." };
  }

  const payload = await response.json();
  revalidatePath("/workspace");
  return {
    status: "success",
    message: `API key ${payload.name} created. Copy the token now.`,
    token: payload.token,
    id: payload.id
  };
}

export async function revokeApiKeyAction(formData: FormData) {
  if (!getSessionToken()) {
    redirect("/login");
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim();
  const apiKeyId = String(formData.get("api_key_id") ?? "").trim();

  await apiRequest(`/workspace/api-keys/${apiKeyId}/revoke?organization_id=${organizationId}`, {
    method: "POST",
    auth: true
  });
  revalidatePath("/workspace");
}

export async function createSeatInviteAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim();
  const email = String(formData.get("email") ?? "").trim();
  const role = String(formData.get("role") ?? "member").trim();

  if (!organizationId || !email) {
    return { status: "error", message: "Organization and email are required." };
  }

  const response = await apiRequest("/billing/seat-invites", {
    method: "POST",
    auth: true,
    body: { organization_id: organizationId, email, role }
  });

  if (!response.ok) {
    return { status: "error", message: "Seat invite could not be created." };
  }

  const payload = await response.json();
  revalidatePath("/billing");
  return {
    status: "success",
    message: `Invite queued for ${payload.email}.`,
    id: payload.id
  };
}

export async function createOrganizationAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const name = String(formData.get("name") ?? "").trim();
  if (!name) {
    return { status: "error", message: "Organization name is required." };
  }

  const response = await apiRequest("/workspace/organizations", {
    method: "POST",
    auth: true,
    body: { name }
  });

  if (!response.ok) {
    return { status: "error", message: "Workspace could not be created." };
  }

  const payload = await response.json();
  revalidatePath("/workspace");
  return {
    status: "success",
    message: `Workspace ${payload.name} created.`,
    id: payload.id
  };
}

export async function attachPaymentMethodAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim();
  const brand = String(formData.get("brand") ?? "").trim();
  const last4 = String(formData.get("last4") ?? "").trim();
  const expMonth = Number(formData.get("exp_month") ?? 0);
  const expYear = Number(formData.get("exp_year") ?? 0);
  const providerCustomerId = String(formData.get("provider_customer_id") ?? "").trim() || undefined;
  const providerPaymentMethodId = String(formData.get("provider_payment_method_id") ?? "").trim() || undefined;

  if (!organizationId || !brand || last4.length !== 4 || !expMonth || !expYear) {
    return { status: "error", message: "Complete payment method details are required." };
  }

  const response = await apiRequest("/billing/payment-methods", {
    method: "POST",
    auth: true,
    body: {
      organization_id: organizationId,
      provider: "stripe",
      provider_customer_id: providerCustomerId,
      provider_payment_method_id: providerPaymentMethodId,
      brand,
      last4,
      exp_month: expMonth,
      exp_year: expYear,
      is_default: true
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Payment method could not be attached." };
  }

  const payload = await response.json();
  revalidatePath("/billing");
  return {
    status: "success",
    message: `Payment method ${payload.brand} ending in ${payload.last4} attached.`,
    id: payload.id
  };
}

export async function createCheckoutSessionAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim();
  const plan = String(formData.get("plan") ?? "").trim();
  const seats = Number(formData.get("seats") ?? 0);

  if (!organizationId || !plan || !seats) {
    return { status: "error", message: "Plan and seat count are required." };
  }

  const response = await apiRequest("/billing/checkout-session", {
    method: "POST",
    auth: true,
    body: { organization_id: organizationId, plan, seats }
  });

  if (!response.ok) {
    return { status: "error", message: "Checkout session could not be created." };
  }

  const payload = await response.json();
  revalidatePath("/billing");
  return {
    status: "success",
    message: `Checkout prepared for ${plan}.`,
    id: payload.invoice_id,
    token: payload.checkout_url
  };
}

export async function cancelSeatInviteAction(formData: FormData) {
  if (!getSessionToken()) {
    redirect("/login");
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim();
  const inviteId = String(formData.get("invite_id") ?? "").trim();

  await apiRequest(`/billing/seat-invites/${inviteId}/cancel?organization_id=${organizationId}`, {
    method: "POST",
    auth: true
  });
  revalidatePath("/billing");
}

export async function adminCreateOrganizationAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const name = String(formData.get("name") ?? "").trim();
  const plan = String(formData.get("plan") ?? "starter").trim();
  const status = String(formData.get("status") ?? "active").trim();
  const regions = listFromCsv(formData.get("regions"));

  if (!name) {
    return { status: "error", message: "Organization name is required." };
  }

  const response = await apiRequest("/admin/organizations", {
    method: "POST",
    auth: true,
    body: { name, plan, status, regions }
  });

  if (!response.ok) {
    return { status: "error", message: "Client organization could not be created." };
  }

  const payload = await response.json();
  revalidatePath("/superadmin");
  revalidatePath("/superadmin/clients");
  return { status: "success", message: `Client ${payload.name} created.`, id: payload.id };
}

export async function adminUpdateOrganizationAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim();
  const name = String(formData.get("name") ?? "").trim() || undefined;
  const plan = String(formData.get("plan") ?? "").trim() || undefined;
  const status = String(formData.get("status") ?? "").trim() || undefined;
  const regions = listFromCsv(formData.get("regions"));

  if (!organizationId) {
    return { status: "error", message: "Organization is required." };
  }

  const response = await apiRequest(`/admin/organizations/${organizationId}`, {
    method: "PATCH",
    auth: true,
    body: {
      name,
      plan,
      status,
      regions: regions.length ? regions : undefined
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Client organization could not be updated." };
  }

  revalidatePath("/superadmin");
  revalidatePath("/superadmin/clients");
  return { status: "success", message: "Client organization updated." };
}

export async function adminCreateUserAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const email = String(formData.get("email") ?? "").trim();
  const fullName = String(formData.get("full_name") ?? "").trim();
  const password = String(formData.get("password") ?? "").trim();
  const role = String(formData.get("role") ?? "analyst").trim();
  const organizationId = String(formData.get("organization_id") ?? "").trim() || undefined;
  const isActive = String(formData.get("is_active") ?? "true").trim() !== "false";

  if (!email || !fullName || !password) {
    return { status: "error", message: "Email, name, and password are required." };
  }

  const response = await apiRequest("/admin/users", {
    method: "POST",
    auth: true,
    body: {
      email,
      full_name: fullName,
      password,
      role,
      organization_id: organizationId,
      is_active: isActive
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Account could not be created." };
  }

  revalidatePath("/superadmin");
  revalidatePath("/superadmin/accounts");
  return { status: "success", message: `Account ${email} created.` };
}

export async function adminUpdateUserAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const userId = String(formData.get("user_id") ?? "").trim();
  const fullName = String(formData.get("full_name") ?? "").trim() || undefined;
  const role = String(formData.get("role") ?? "").trim() || undefined;
  const isActiveValue = String(formData.get("is_active") ?? "").trim();
  const isActive = isActiveValue ? isActiveValue === "true" : undefined;

  if (!userId) {
    return { status: "error", message: "User is required." };
  }

  const response = await apiRequest(`/admin/users/${userId}`, {
    method: "PATCH",
    auth: true,
    body: {
      full_name: fullName,
      role,
      is_active: isActive
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Account could not be updated." };
  }

  revalidatePath("/superadmin");
  revalidatePath("/superadmin/accounts");
  return { status: "success", message: "Account updated." };
}

export async function adminUpdateConfigAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const crawlerConcurrency = Number(formData.get("crawler_concurrency") ?? 0);
  const crawlerMaxRetries = Number(formData.get("crawler_max_retries") ?? 0);
  const defaultRegion = String(formData.get("default_region") ?? "").trim() || undefined;
  const rateLimitRequests = Number(formData.get("rate_limit_requests") ?? 0);
  const rateLimitWindowSeconds = Number(formData.get("rate_limit_window_seconds") ?? 0);

  const response = await apiRequest("/admin/configs", {
    method: "PATCH",
    auth: true,
    body: {
      crawler_concurrency: crawlerConcurrency || undefined,
      crawler_max_retries: crawlerMaxRetries || undefined,
      default_region: defaultRegion,
      rate_limit_requests: rateLimitRequests || undefined,
      rate_limit_window_seconds: rateLimitWindowSeconds || undefined
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Platform configuration could not be updated." };
  }

  revalidatePath("/superadmin/crawlers");
  revalidatePath("/superadmin/configs");
  return { status: "success", message: "Platform configuration updated." };
}

export async function adminCreateMembershipAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim();
  const userId = String(formData.get("user_id") ?? "").trim();
  const role = String(formData.get("role") ?? "member").trim();

  if (!organizationId || !userId) {
    return { status: "error", message: "Organization and user are required." };
  }

  const response = await apiRequest("/admin/memberships", {
    method: "POST",
    auth: true,
    body: {
      organization_id: organizationId,
      user_id: userId,
      role,
      is_default: false
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Membership could not be created." };
  }

  revalidatePath(`/superadmin/clients/${organizationId}`);
  revalidatePath("/superadmin/clients");
  return { status: "success", message: "Membership created." };
}

export async function adminUpdateMembershipAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const membershipId = String(formData.get("membership_id") ?? "").trim();
  const organizationId = String(formData.get("organization_id") ?? "").trim();
  const role = String(formData.get("role") ?? "").trim() || undefined;
  const isDefaultValue = String(formData.get("is_default") ?? "").trim();
  const isDefault = isDefaultValue ? isDefaultValue === "true" : undefined;

  if (!membershipId || !organizationId) {
    return { status: "error", message: "Membership is required." };
  }

  const response = await apiRequest(`/admin/memberships/${membershipId}`, {
    method: "PATCH",
    auth: true,
    body: {
      role,
      is_default: isDefault
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Membership could not be updated." };
  }

  revalidatePath(`/superadmin/clients/${organizationId}`);
  return { status: "success", message: "Membership updated." };
}

export async function adminDeleteMembershipAction(formData: FormData) {
  if (!getSessionToken()) {
    redirect("/login");
  }

  const membershipId = String(formData.get("membership_id") ?? "").trim();
  const organizationId = String(formData.get("organization_id") ?? "").trim();

  await apiRequest(`/admin/memberships/${membershipId}`, {
    method: "DELETE",
    auth: true
  });
  revalidatePath(`/superadmin/clients/${organizationId}`);
  revalidatePath("/superadmin/clients");
}

export async function adminUpdateSubscriptionAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim();
  const plan = String(formData.get("plan") ?? "").trim() || undefined;
  const status = String(formData.get("status") ?? "").trim() || undefined;
  const seats = Number(formData.get("seats") ?? 0);
  const searchQuota = Number(formData.get("search_quota") ?? 0);
  const exportQuota = Number(formData.get("export_quota") ?? 0);
  const crawlQuota = Number(formData.get("crawl_quota") ?? 0);

  if (!organizationId) {
    return { status: "error", message: "Organization is required." };
  }

  const response = await apiRequest(`/admin/organizations/${organizationId}/subscription`, {
    method: "PATCH",
    auth: true,
    body: {
      plan,
      status,
      seats: seats || undefined,
      search_quota: searchQuota || undefined,
      export_quota: exportQuota || undefined,
      crawl_quota: crawlQuota || undefined
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Subscription could not be updated." };
  }

  revalidatePath(`/superadmin/clients/${organizationId}`);
  revalidatePath("/superadmin/finance");
  revalidatePath("/superadmin/clients");
  return { status: "success", message: "Subscription updated." };
}

export async function adminUpdateInvoiceAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const invoiceId = String(formData.get("invoice_id") ?? "").trim();
  const status = String(formData.get("status") ?? "").trim();

  if (!invoiceId || !status) {
    return { status: "error", message: "Invoice and status are required." };
  }

  const response = await apiRequest(`/admin/invoices/${invoiceId}`, {
    method: "PATCH",
    auth: true,
    body: { status }
  });

  if (!response.ok) {
    return { status: "error", message: "Invoice could not be updated." };
  }

  revalidatePath("/superadmin/finance");
  revalidatePath(`/superadmin/clients`);
  return { status: "success", message: "Invoice updated." };
}

export async function adminCreateSupportTicketAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim() || undefined;
  const title = String(formData.get("title") ?? "").trim();
  const priority = String(formData.get("priority") ?? "medium").trim();
  const status = String(formData.get("status") ?? "open").trim();
  const description = String(formData.get("description") ?? "").trim();
  const assigneeUserId = String(formData.get("assignee_user_id") ?? "").trim() || undefined;
  const slaLabel = String(formData.get("sla_label") ?? "").trim() || undefined;

  if (!title || !description) {
    return { status: "error", message: "Ticket title and description are required." };
  }

  const response = await apiRequest("/admin/support", {
    method: "POST",
    auth: true,
    body: {
      organization_id: organizationId,
      title,
      priority,
      status,
      description,
      assignee_user_id: assigneeUserId,
      sla_label: slaLabel
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Support ticket could not be created." };
  }

  revalidatePath("/superadmin/support");
  return { status: "success", message: "Support ticket created." };
}

export async function adminUpdateSupportTicketAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const ticketId = String(formData.get("ticket_id") ?? "").trim();
  const priority = String(formData.get("priority") ?? "").trim() || undefined;
  const status = String(formData.get("status") ?? "").trim() || undefined;
  const description = String(formData.get("description") ?? "").trim() || undefined;
  const assigneeUserId = String(formData.get("assignee_user_id") ?? "").trim() || undefined;
  const slaLabel = String(formData.get("sla_label") ?? "").trim() || undefined;

  if (!ticketId) {
    return { status: "error", message: "Ticket is required." };
  }

  const response = await apiRequest(`/admin/support/${ticketId}`, {
    method: "PATCH",
    auth: true,
    body: {
      priority,
      status,
      description,
      assignee_user_id: assigneeUserId,
      sla_label: slaLabel
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Support ticket could not be updated." };
  }

  revalidatePath("/superadmin/support");
  return { status: "success", message: "Support ticket updated." };
}

export async function adminCreateInvoiceAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim();
  const amount = Number(formData.get("amount") ?? 0);
  const seats = Number(formData.get("seats") ?? 1);
  const currency = String(formData.get("currency") ?? "usd").trim();
  const status = String(formData.get("status") ?? "open").trim();

  if (!organizationId || !amount) {
    return { status: "error", message: "Organization and amount are required." };
  }

  const response = await apiRequest("/admin/invoices", {
    method: "POST",
    auth: true,
    body: {
      organization_id: organizationId,
      amount,
      seats,
      currency,
      status
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Invoice could not be created." };
  }

  revalidatePath("/superadmin/invoices");
  revalidatePath(`/superadmin/clients/${organizationId}`);
  return { status: "success", message: "Invoice created." };
}

export async function adminResendInvoiceAction(formData: FormData) {
  if (!getSessionToken()) {
    redirect("/login");
  }

  const invoiceId = String(formData.get("invoice_id") ?? "").trim();
  if (!invoiceId) {
    return;
  }

  await apiRequest(`/admin/invoices/${invoiceId}/resend`, {
    method: "POST",
    auth: true
  });
  revalidatePath("/superadmin/invoices");
}

export async function adminArchiveOrganizationAction(formData: FormData) {
  if (!getSessionToken()) {
    redirect("/login");
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim();
  if (!organizationId) {
    return;
  }

  await apiRequest(`/admin/organizations/${organizationId}/archive`, {
    method: "POST",
    auth: true
  });
  revalidatePath("/superadmin/clients");
  revalidatePath(`/superadmin/clients/${organizationId}`);
}

export async function adminDeleteOrganizationAction(formData: FormData) {
  if (!getSessionToken()) {
    redirect("/login");
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim();
  if (!organizationId) {
    return;
  }

  await apiRequest(`/admin/organizations/${organizationId}`, {
    method: "DELETE",
    auth: true
  });
  revalidatePath("/superadmin/clients");
  redirect("/superadmin/clients");
}

export async function adminCreatePaymentMethodAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const organizationId = String(formData.get("organization_id") ?? "").trim();
  const provider = String(formData.get("provider") ?? "manual").trim();
  const brand = String(formData.get("brand") ?? "").trim();
  const last4 = String(formData.get("last4") ?? "").trim();
  const expMonth = Number(formData.get("exp_month") ?? 0);
  const expYear = Number(formData.get("exp_year") ?? 0);
  const isDefault = String(formData.get("is_default") ?? "true").trim() !== "false";

  if (!organizationId || !brand || last4.length !== 4) {
    return { status: "error", message: "Complete payment method details are required." };
  }

  const response = await apiRequest("/admin/payment-methods", {
    method: "POST",
    auth: true,
    body: {
      organization_id: organizationId,
      provider,
      brand,
      last4,
      exp_month: expMonth,
      exp_year: expYear,
      is_default: isDefault
    }
  });

  if (!response.ok) {
    return { status: "error", message: "Payment method could not be created." };
  }

  revalidatePath("/superadmin/payment-methods");
  revalidatePath(`/superadmin/clients/${organizationId}`);
  return { status: "success", message: "Payment method created." };
}

export async function adminSetDefaultPaymentMethodAction(formData: FormData) {
  if (!getSessionToken()) {
    redirect("/login");
  }

  const paymentMethodId = String(formData.get("payment_method_id") ?? "").trim();
  const organizationId = String(formData.get("organization_id") ?? "").trim();
  if (!paymentMethodId) {
    return;
  }

  await apiRequest(`/admin/payment-methods/${paymentMethodId}/default`, {
    method: "POST",
    auth: true
  });
  revalidatePath("/superadmin/payment-methods");
  if (organizationId) {
    revalidatePath(`/superadmin/clients/${organizationId}`);
  }
}

export async function adminDeletePaymentMethodAction(formData: FormData) {
  if (!getSessionToken()) {
    redirect("/login");
  }

  const paymentMethodId = String(formData.get("payment_method_id") ?? "").trim();
  const organizationId = String(formData.get("organization_id") ?? "").trim();
  if (!paymentMethodId) {
    return;
  }

  await apiRequest(`/admin/payment-methods/${paymentMethodId}`, {
    method: "DELETE",
    auth: true
  });
  revalidatePath("/superadmin/payment-methods");
  if (organizationId) {
    revalidatePath(`/superadmin/clients/${organizationId}`);
  }
}

export async function adminCreateSupportNoteAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const ticketId = String(formData.get("ticket_id") ?? "").trim();
  const body = String(formData.get("body") ?? "").trim();
  if (!ticketId || !body) {
    return { status: "error", message: "A ticket and note body are required." };
  }

  const response = await apiRequest(`/admin/support/${ticketId}/notes`, {
    method: "POST",
    auth: true,
    body: { body }
  });

  if (!response.ok) {
    return { status: "error", message: "Support note could not be added." };
  }

  revalidatePath("/superadmin/support");
  return { status: "success", message: "Support note added." };
}

export async function adminCreateCrawlerPresetAction(_: FormState, formData: FormData): Promise<FormState> {
  if (!getSessionToken()) {
    return { status: "error", message: "Sign in required." };
  }

  const name = String(formData.get("name") ?? "").trim();
  const mode = String(formData.get("mode") ?? "discovery").trim();
  if (!name) {
    return { status: "error", message: "Preset name is required." };
  }

  const body = {
    name,
    mode,
    query: String(formData.get("query") ?? "").trim() || undefined,
    city: String(formData.get("city") ?? "").trim() || undefined,
    region: String(formData.get("region") ?? "").trim() || undefined,
    country: String(formData.get("country") ?? "").trim() || undefined,
    source: String(formData.get("source") ?? "hybrid").trim(),
    keywords: listFromCsv(formData.get("keywords")),
    industries: listFromCsv(formData.get("industries")),
    employee_range: String(formData.get("employee_range") ?? "").trim() || undefined,
    min_reviews: String(formData.get("min_reviews") ?? "").trim() ? Number(formData.get("min_reviews")) : undefined,
    max_rating: String(formData.get("max_rating") ?? "").trim() ? Number(formData.get("max_rating")) : undefined,
    has_website: String(formData.get("has_website") ?? "").trim() ? String(formData.get("has_website")) === "true" : undefined,
    grid: String(formData.get("latitude") ?? "").trim() && String(formData.get("longitude") ?? "").trim()
      ? [Number(formData.get("latitude")), Number(formData.get("longitude"))]
      : undefined,
    keyword_set: listFromCsv(formData.get("keyword_set")),
    radius_km: String(formData.get("radius_km") ?? "").trim() ? Number(formData.get("radius_km")) : undefined
  };

  const response = await apiRequest("/admin/crawler-presets", {
    method: "POST",
    auth: true,
    body
  });

  if (!response.ok) {
    return { status: "error", message: "Crawler preset could not be created." };
  }

  revalidatePath("/superadmin/crawlers");
  return { status: "success", message: `Preset ${name} created.` };
}

export async function adminRunCrawlerPresetAction(formData: FormData) {
  if (!getSessionToken()) {
    redirect("/login");
  }

  const presetId = String(formData.get("preset_id") ?? "").trim();
  if (!presetId) {
    return;
  }

  await apiRequest(`/admin/crawler-presets/${presetId}/run`, {
    method: "POST",
    auth: true
  });
  revalidatePath("/superadmin/crawlers");
}

export async function adminDeleteCrawlerPresetAction(formData: FormData) {
  if (!getSessionToken()) {
    redirect("/login");
  }

  const presetId = String(formData.get("preset_id") ?? "").trim();
  if (!presetId) {
    return;
  }

  await apiRequest(`/admin/crawler-presets/${presetId}`, {
    method: "DELETE",
    auth: true
  });
  revalidatePath("/superadmin/crawlers");
}
