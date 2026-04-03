import { AppShell } from "@/components/app-shell";
import { SuperadminSubscriptionForm } from "@/components/forms/superadmin-forms";
import { Card } from "@/components/ui/card";
import { getAdminData } from "@/lib/data";

export default async function SuperadminFinancePage() {
  const admin = await getAdminData();

  const estimatedMrr =
    (admin.analytics.plans.starter ?? 0) * 99 +
    (admin.analytics.plans.growth ?? 0) * 199 +
    (admin.analytics.plans.enterprise ?? 0) * 499;

  return (
    <AppShell eyebrow="Superadmin Finance" title="Revenue posture and client package mix" mode="superadmin">
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <p className="text-xs uppercase tracking-[0.24em] text-accent">Estimated MRR</p>
          <p className="mt-4 font-display text-4xl text-white">${estimatedMrr}</p>
        </Card>
        <Card>
          <p className="text-xs uppercase tracking-[0.24em] text-accent">Client count</p>
          <p className="mt-4 font-display text-4xl text-white">{admin.analytics.total_organizations}</p>
        </Card>
        <Card>
          <p className="text-xs uppercase tracking-[0.24em] text-accent">Active users</p>
          <p className="mt-4 font-display text-4xl text-white">{admin.analytics.active_users}</p>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card>
          <h3 className="font-display text-2xl text-white">Plan distribution</h3>
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
        </Card>

        <Card>
          <h3 className="font-display text-2xl text-white">Commercial note</h3>
          <p className="mt-5 text-sm leading-7 text-slate-400">
            This finance view is internal-facing and summarizes client plan distribution at the company level. Customer users never enter this surface.
          </p>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <h3 className="font-display text-2xl text-white">Managed subscriptions</h3>
          <div className="mt-5 grid gap-6">
            {admin.organizations.length ? (
              admin.organizations.map((organization: any) => (
                <div key={organization.id} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div>
                      <p className="text-white">{organization.name}</p>
                      <p className="mt-1 text-sm text-slate-400">{organization.slug}</p>
                    </div>
                    <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{organization.plan}</span>
                  </div>
                  <div className="mt-5">
                    <SuperadminSubscriptionForm
                      organizationId={organization.id}
                      fallbackPlan={organization.plan}
                    />
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                No organizations available for subscription management.
              </div>
            )}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
