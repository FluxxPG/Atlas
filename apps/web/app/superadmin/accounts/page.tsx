import { AppShell } from "@/components/app-shell";
import {
  SuperadminUserCreateForm,
  SuperadminUserUpdateForm
} from "@/components/forms/superadmin-forms";
import { Card } from "@/components/ui/card";
import { getAdminData } from "@/lib/data";

export default async function SuperadminAccountsPage() {
  const admin = await getAdminData();

  return (
    <AppShell eyebrow="Superadmin Accounts" title="Account and operator management" mode="superadmin">
      <div className="mb-6">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Create Account</p>
          <h3 className="mt-3 font-display text-3xl text-white">Add a user to a managed client organization</h3>
          <div className="mt-5">
            <SuperadminUserCreateForm
              organizations={admin.organizations.map((organization: any) => ({
                id: organization.id,
                name: organization.name
              }))}
            />
          </div>
        </Card>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {admin.users.length ? (
          admin.users.map((user: any) => (
            <Card key={user.id}>
              <p className="text-white">{user.full_name}</p>
              <p className="mt-2 text-sm text-slate-400">{user.email}</p>
              <div className="mt-5 flex items-center justify-between text-sm">
                <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{user.role}</span>
                <span className={(user.is_active ?? user.active) ? "text-emerald-300" : "text-rose-300"}>
                  {(user.is_active ?? user.active) ? "active" : "inactive"}
                </span>
              </div>
              <div className="mt-5 rounded-3xl border border-white/10 bg-black/20 p-4">
                <SuperadminUserUpdateForm
                  userId={user.id}
                  defaultRole={user.role}
                  defaultActive={Boolean(user.is_active ?? user.active)}
                />
              </div>
            </Card>
          ))
        ) : (
          <Card className="md:col-span-2 xl:col-span-3">
            <p className="text-white">No accounts are available yet.</p>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
