import "server-only";

import { redirect } from "next/navigation";

import { getSessionUser, type SessionUser } from "@/lib/server-api";

export type FeatureKey =
  | "dashboard"
  | "search"
  | "company"
  | "leads"
  | "exports"
  | "alerts"
  | "insights"
  | "workspace"
  | "billing";

export type PlanTier = "starter" | "growth" | "enterprise";

export const SUPERADMIN_ROLES = new Set(["admin", "operator", "superadmin"]);

const PLAN_ORDER: Record<PlanTier, number> = {
  starter: 1,
  growth: 2,
  enterprise: 3
};

const FEATURE_MIN_PLAN: Record<FeatureKey, PlanTier> = {
  dashboard: "starter",
  search: "starter",
  company: "starter",
  leads: "starter",
  exports: "growth",
  alerts: "growth",
  insights: "growth",
  workspace: "starter",
  billing: "starter"
};

const FEATURE_LABELS: Record<FeatureKey, string> = {
  dashboard: "Dashboard",
  search: "AI Search",
  company: "Company Explorer",
  leads: "Saved Leads",
  exports: "Exports",
  alerts: "Alerts",
  insights: "Insights",
  workspace: "Workspace",
  billing: "Billing"
};

export function normalizePlan(plan?: string | null): PlanTier {
  if (plan === "growth" || plan === "enterprise") {
    return plan;
  }
  return "starter";
}

export function isSuperadminRole(role?: string | null) {
  return SUPERADMIN_ROLES.has(String(role ?? "").toLowerCase());
}

export function getSessionPlan(session: SessionUser | null | undefined): PlanTier {
  return normalizePlan(session?.default_organization?.plan);
}

export function hasFeatureAccess(session: SessionUser | null | undefined, feature: FeatureKey) {
  if (!session) {
    return false;
  }

  if (isSuperadminRole(session.role)) {
    return true;
  }

  return PLAN_ORDER[getSessionPlan(session)] >= PLAN_ORDER[FEATURE_MIN_PLAN[feature]];
}

export function getFeatureLabel(feature: FeatureKey) {
  return FEATURE_LABELS[feature];
}

export function getRequiredPlan(feature: FeatureKey) {
  return FEATURE_MIN_PLAN[feature];
}

export function getDefaultAppPath(session: SessionUser | null | undefined) {
  if (!session) {
    return "/login";
  }
  return isSuperadminRole(session.role) ? "/superadmin" : "/dashboard";
}

export async function requireSession() {
  const session = await getSessionUser();

  if (!session) {
    redirect("/login");
  }

  return session;
}

export async function redirectIfAuthenticated() {
  const session = await getSessionUser();
  if (session) {
    redirect(getDefaultAppPath(session));
  }
}
