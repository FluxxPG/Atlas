import { AppShell } from "@/components/app-shell";
import Link from "next/link";
import {
  SuperadminOrganizationCreateForm,
  SuperadminOrganizationUpdateForm
} from "@/components/forms/superadmin-forms";
import { Card } from "@/components/ui/card";
import { getAdminData } from "@/lib/data";

export default async function SuperadminClientsPage() {
  const admin = await getAdminData();

  return (
    <AppShell eyebrow="Superadmin Clients" title="Client organization management" mode="superadmin">
      <div className="mb-6">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Create Client</p>
          <h3 className="mt-3 font-display text-3xl text-white">Provision a new managed customer organization</h3>
          <div className="mt-5">
            <SuperadminOrganizationCreateForm />
          </div>
        </Card>
      </div>
      <div className="grid gap-6">
        {admin.organizations.length ? (
          admin.organizations.map((organization: any) => (
            <Card key={organization.id}>
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-accent">{organization.plan}</p>
                  <h3 className="mt-3 font-display text-2xl text-white">{organization.name}</h3>
                  <p className="mt-2 text-sm text-slate-400">{organization.slug}</p>
                </div>
                <div className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white">
                  {organization.status}
                </div>
              </div>
              <div className="mt-6 grid gap-3 md:grid-cols-3">
                <div className="rounded-2xl bg-white/5 p-4 text-sm text-slate-300">Members {organization.member_count}</div>
                <div className="rounded-2xl bg-white/5 p-4 text-sm text-slate-300">Admins {organization.admin_count}</div>
                <div className="rounded-2xl bg-white/5 p-4 text-sm text-slate-300">Regions {organization.settings?.regions?.join(", ") ?? "Default"}</div>
              </div>
              <Link
                href={`/superadmin/clients/${organization.id}`}
                className="mt-5 inline-flex rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10"
              >
                Open client details
              </Link>
              <div className="mt-6 rounded-3xl border border-white/10 bg-black/20 p-5">
                <p className="text-sm uppercase tracking-[0.24em] text-accent">Update client</p>
                <div className="mt-4">
                  <SuperadminOrganizationUpdateForm
                    organizationId={organization.id}
                    defaultPlan={organization.plan}
                    defaultStatus={organization.status}
                    defaultRegions={organization.settings?.regions ?? []}
                  />
                </div>
              </div>
            </Card>
          ))
        ) : (
          <Card>
            <p className="text-white">No client organizations are available yet.</p>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
