import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { SuperadminSubscriptionForm } from "@/components/forms/superadmin-forms";
import { Card } from "@/components/ui/card";
import { getAdminData } from "@/lib/data";

export default async function SuperadminSubscriptionsPage() {
  const admin = await getAdminData();

  return (
    <AppShell eyebrow="Superadmin Subscriptions" title="Client subscription management" mode="superadmin">
      <div className="grid gap-6">
        {admin.organizations.length ? (
          admin.organizations.map((organization: any) => (
            <Card key={organization.id}>
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-white">{organization.name}</p>
                  <p className="mt-1 text-sm text-slate-400">{organization.slug}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{organization.plan}</span>
                  <Link
                    href={`/superadmin/clients/${organization.id}`}
                    className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10"
                  >
                    Open client
                  </Link>
                </div>
              </div>
              <div className="mt-5">
                <SuperadminSubscriptionForm
                  organizationId={organization.id}
                  fallbackPlan={organization.plan}
                />
              </div>
            </Card>
          ))
        ) : (
          <Card>
            <p className="text-white">No client subscriptions available.</p>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
