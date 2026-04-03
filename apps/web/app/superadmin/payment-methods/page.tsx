import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import {
  SuperadminPaymentMethodActions,
  SuperadminPaymentMethodCreateForm
} from "@/components/forms/superadmin-forms";
import { Card } from "@/components/ui/card";
import { getAdminData, getAdminPaymentMethods } from "@/lib/data";

export default async function SuperadminPaymentMethodsPage() {
  const [methods, admin] = await Promise.all([getAdminPaymentMethods(), getAdminData()]);

  return (
    <AppShell eyebrow="Superadmin Payment Methods" title="Payment method administration" mode="superadmin">
      <div className="mb-6">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Add Payment Method</p>
          <h3 className="mt-3 font-display text-3xl text-white">Attach a payment method to a managed client</h3>
          <div className="mt-5">
            <SuperadminPaymentMethodCreateForm
              organizations={admin.organizations.map((organization: any) => ({
                id: organization.id,
                name: organization.name
              }))}
            />
          </div>
        </Card>
      </div>

      <div className="grid gap-6">
        {methods.items.length ? (
          methods.items.map((method: any) => (
            <Card key={method.id}>
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-white">{method.organization_name}</p>
                  <p className="mt-1 text-sm text-slate-400">{method.provider} / {method.brand} ending in {method.last4}</p>
                </div>
                <div className="flex items-center gap-3">
                  {method.is_default ? <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">Default</span> : null}
                  <Link
                    href={`/superadmin/clients/${method.organization_id}`}
                    className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10"
                  >
                    Open client
                  </Link>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
                <p className="text-sm text-slate-400">Expires {method.exp_month}/{method.exp_year}</p>
                <SuperadminPaymentMethodActions
                  paymentMethodId={method.id}
                  organizationId={method.organization_id}
                  isDefault={method.is_default}
                />
              </div>
            </Card>
          ))
        ) : (
          <Card>
            <p className="text-white">No payment methods are available yet.</p>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
