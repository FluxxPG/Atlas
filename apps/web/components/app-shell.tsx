import type { ReactNode } from "react";
import Link from "next/link";
import { redirect } from "next/navigation";
import {
  BarChart3,
  Bell,
  Building2,
  CreditCard,
  Database,
  Download,
  FileText,
  Home,
  Lock,
  Radar,
  Search,
  Settings,
  Sparkles,
  Star,
  Telescope,
  Users
} from "lucide-react";

import { logoutAction, queueIndiaSeedAction } from "@/app/actions";
import { Button } from "@/components/ui/button";
import {
  getDefaultAppPath,
  getFeatureLabel,
  getRequiredPlan,
  hasFeatureAccess,
  isSuperadminRole,
  type FeatureKey
} from "@/lib/access";
import { getSessionData } from "@/lib/data";

type ShellMode = "client" | "superadmin";

type NavItem = {
  href: string;
  label: string;
  icon: typeof Home;
  feature?: FeatureKey;
};

const clientNav: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: Home, feature: "dashboard" },
  { href: "/search", label: "Search", icon: Search, feature: "search" },
  { href: "/company", label: "Explorer", icon: Database, feature: "company" },
  { href: "/leads", label: "Saved Leads", icon: Star, feature: "leads" },
  { href: "/exports", label: "Exports", icon: Download, feature: "exports" },
  { href: "/alerts", label: "Alerts", icon: Bell, feature: "alerts" },
  { href: "/insights", label: "Insights", icon: Radar, feature: "insights" },
  { href: "/workspace", label: "Workspace", icon: Building2, feature: "workspace" },
  { href: "/billing", label: "Billing", icon: CreditCard, feature: "billing" }
];

const superadminNav: NavItem[] = [
  { href: "/superadmin", label: "Overview", icon: Home },
  { href: "/superadmin/clients", label: "Clients", icon: Building2 },
  { href: "/superadmin/accounts", label: "Accounts", icon: Users },
  { href: "/superadmin/subscriptions", label: "Subscriptions", icon: CreditCard },
  { href: "/superadmin/payment-methods", label: "Payment Methods", icon: CreditCard },
  { href: "/superadmin/invoices", label: "Invoices", icon: Download },
  { href: "/superadmin/support", label: "Support", icon: Bell },
  { href: "/superadmin/crawlers", label: "Crawlers", icon: Telescope },
  { href: "/superadmin/finance", label: "Finance", icon: CreditCard },
  { href: "/superadmin/logs", label: "Logs", icon: FileText },
  { href: "/superadmin/configs", label: "Configs", icon: Settings }
];

function UpgradeGate({
  feature,
  plan
}: {
  feature: FeatureKey;
  plan: string;
}) {
  return (
    <div className="glass rounded-[30px] p-8">
      <p className="text-xs uppercase tracking-[0.35em] text-accent">Feature Gate</p>
      <h3 className="mt-4 font-display text-4xl text-white">{getFeatureLabel(feature)} is locked on {plan}</h3>
      <p className="mt-4 max-w-2xl text-sm text-slate-300">
        Upgrade to the {getRequiredPlan(feature)} package to unlock this workflow for customer users. Superadmin users can still access the platform-wide controls separately.
      </p>
      <div className="mt-6 flex flex-wrap gap-3">
        <Button asChild>
          <Link href="/billing">View packages</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/dashboard">Back to dashboard</Link>
        </Button>
      </div>
    </div>
  );
}

export async function AppShell({
  children,
  title,
  eyebrow,
  mode = "client",
  feature
}: {
  children: ReactNode;
  title: string;
  eyebrow: string;
  mode?: ShellMode;
  feature?: FeatureKey;
}) {
  const session = await getSessionData();

  if (!session) {
    redirect("/login");
  }

  const superadmin = isSuperadminRole(session.role);

  if (mode === "superadmin" && !superadmin) {
    redirect(getDefaultAppPath(session));
  }

  const nav = mode === "superadmin" ? superadminNav : clientNav;
  const lockedFeature = feature && !hasFeatureAccess(session, feature) ? feature : null;
  const plan = session.default_organization?.plan ?? "starter";

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="mesh" />
      <div className="mx-auto flex min-h-screen max-w-[1600px] gap-6 px-4 py-5 lg:px-6">
        <aside className="glass hidden w-72 shrink-0 rounded-[30px] p-6 lg:flex lg:flex-col">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-accent">
              {mode === "superadmin" ? "Superadmin Control" : "Client Intelligence"}
            </p>
            <h1 className="mt-3 font-display text-2xl font-semibold text-white">AtlasBI</h1>
            <p className="mt-2 text-sm text-slate-400">
              {mode === "superadmin"
                ? "Run crawl operations, manage geographies, and seed intelligence into the platform."
                : "Search, monitor, and convert high-conviction opportunities from the intelligence graph."}
            </p>
          </div>
          <nav className="mt-8 space-y-2">
            {nav.map((item) => {
              const Icon = item.icon;
              const allowed = item.feature ? hasFeatureAccess(session, item.feature) : true;

              if (!allowed) {
                return (
                  <div
                    key={item.href}
                    className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-500"
                  >
                    <div className="flex items-center gap-3">
                      <Icon className="h-4 w-4 text-slate-500" />
                      {item.label}
                    </div>
                    <span className="inline-flex items-center gap-1 rounded-full bg-black/20 px-2 py-1 text-[10px] uppercase tracking-[0.2em] text-accent">
                      <Lock className="h-3 w-3" />
                      {getRequiredPlan(item.feature as FeatureKey)}
                    </span>
                  </div>
                );
              }

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-slate-300 transition hover:bg-white/5 hover:text-white"
                >
                  <Icon className="h-4 w-4 text-accent" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="mt-auto rounded-[26px] border border-white/10 bg-white/5 p-5">
            <div className="mb-3 flex items-center gap-2 text-sm text-white">
              {mode === "superadmin" ? (
                <>
                  <Telescope className="h-4 w-4 text-accent" />
                  Crawl Operations
                </>
              ) : (
                <>
                  <BarChart3 className="h-4 w-4 text-accent" />
                  Package Access
                </>
              )}
            </div>
            <p className="text-sm text-slate-400">
              {mode === "superadmin"
                ? "Manage clients, accounts, billing posture, crawler operations, and company-wide platform telemetry from one control surface."
                : `Current package: ${plan}. Upgrade to unlock exports, alerts, insights, and expanded workflow controls.`}
            </p>
            <Button asChild className="mt-4 w-full">
              <Link href={mode === "superadmin" ? "/superadmin/crawlers" : "/billing"}>
                {mode === "superadmin" ? "Open operations" : "Review packages"}
              </Link>
            </Button>
          </div>
        </aside>

        <main className="flex-1">
          <header className="glass rounded-[30px] px-6 py-5">
            <p className="text-xs uppercase tracking-[0.35em] text-accent">{eyebrow}</p>
            <div className="mt-3 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
              <div>
                <h2 className="font-display text-4xl font-semibold tracking-tight text-white">{title}</h2>
                <p className="mt-2 max-w-3xl text-sm text-slate-400">
                  {mode === "superadmin"
                    ? "Company-level control surface for client management, accounts, billing posture, crawl orchestration, and platform analytics."
                    : "Customer workspace for intelligence retrieval, saved leads, alerts, exports, and decision-ready account research."}
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200">
                  {session.full_name} / {superadmin ? "superadmin" : session.role}
                </div>
                <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200">
                  Plan / {plan}
                </div>
                {mode === "superadmin" ? (
                  <form action={queueIndiaSeedAction}>
                    <Button variant="outline" type="submit">Seed India Crawl</Button>
                  </form>
                ) : (
                  <Button asChild>
                    <Link href="/search?q=fast%20growing%20startups">Launch AI Search</Link>
                  </Button>
                )}
                <form action={logoutAction}>
                  <Button variant="ghost" type="submit">Sign out</Button>
                </form>
              </div>
            </div>
          </header>
          <div className="mt-6">
            {lockedFeature ? <UpgradeGate feature={lockedFeature} plan={plan} /> : children}
          </div>
        </main>
      </div>
    </div>
  );
}
