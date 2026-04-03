import { Activity, Building2, Database, Users } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { MetricCard } from "@/components/metric-card";
import { Card } from "@/components/ui/card";
import { getAdminData } from "@/lib/data";

export default async function SuperadminOverviewPage() {
  const admin = await getAdminData();

  return (
    <AppShell eyebrow="Superadmin Overview" title="Company operations command center" mode="superadmin">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Clients" value={admin.analytics.total_organizations} meta={{ scope: "organizations" }} />
        <MetricCard label="Platform users" value={admin.analytics.total_users} meta={{ active: admin.analytics.active_users }} />
        <MetricCard label="Companies indexed" value={admin.analytics.total_companies} meta={{ dataset: "live" }} />
        <MetricCard label="Queued jobs" value={admin.analytics.queued_jobs} meta={{ running: admin.analytics.running_jobs }} />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Company-Level Management</p>
          <h3 className="mt-3 font-display text-3xl text-white">Operate AtlasBI for all clients from one internal surface</h3>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {[
              { label: "Client organizations", copy: "Manage plans, status, workspace footprint, and regional settings.", Icon: Building2 },
              { label: "Accounts and users", copy: "Control access, operator roles, and customer seats across the platform.", Icon: Users },
              { label: "Platform analytics", copy: "Track client growth, user activity, dataset size, and queue behavior.", Icon: Activity },
              { label: "Dataset growth", copy: "Monitor crawlers, company coverage, and operational ingestion throughput.", Icon: Database }
            ].map(({ label, copy, Icon }) => (
              <div key={label} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                <Icon className="h-5 w-5 text-accent" />
                <p className="mt-4 text-white">{label}</p>
                <p className="mt-2 text-sm leading-6 text-slate-400">{copy}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Plan Mix</p>
          <div className="mt-5 space-y-3">
            {Object.entries(admin.analytics.plans).map(([plan, count]) => (
              <div key={plan} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between">
                  <p className="text-white">{plan}</p>
                  <p className="font-display text-2xl text-white">{count}</p>
                </div>
              </div>
            ))}
          </div>
          <p className="mt-5 text-sm leading-7 text-slate-400">
            The superadmin surface is internal-only. Customer dashboards stay separate and package-gated.
          </p>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card>
          <h3 className="font-display text-2xl text-white">Recent client organizations</h3>
          <div className="mt-5 space-y-3">
            {admin.organizations.length ? (
              admin.organizations.slice(0, 6).map((organization: any) => (
                <div key={organization.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="text-white">{organization.name}</p>
                      <p className="mt-1 text-sm text-slate-400">{organization.slug}</p>
                    </div>
                    <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{organization.plan}</span>
                  </div>
                  <p className="mt-3 text-sm text-slate-400">
                    Members {organization.member_count} / Admins {organization.admin_count} / {organization.status}
                  </p>
                </div>
              ))
            ) : (
              <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                Client organizations will appear here as workspaces are provisioned.
              </div>
            )}
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-2xl text-white">Operational pulse</h3>
          <div className="mt-5 space-y-3">
            {[
              ["Active users", admin.analytics.active_users],
              ["Running jobs", admin.analytics.running_jobs],
              ["Queue depth", admin.queue_depth],
              ["Dataset size", admin.dataset_size]
            ].map(([label, value]) => (
              <div key={String(label)} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between">
                  <p className="text-slate-300">{label}</p>
                  <p className="font-display text-2xl text-white">{value}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
