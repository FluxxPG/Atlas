import { adminResendInvoiceAction } from "@/app/actions";
import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { SuperadminInvoiceCreateForm, SuperadminInvoiceStatusForm } from "@/components/forms/superadmin-forms";
import { Card } from "@/components/ui/card";
import { getAdminData, getAdminInvoices } from "@/lib/data";

export default async function SuperadminInvoicesPage() {
  const [invoices, admin] = await Promise.all([getAdminInvoices(), getAdminData()]);

  return (
    <AppShell eyebrow="Superadmin Invoices" title="Invoice operations and payment state" mode="superadmin">
      <div className="mb-6">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Generate Invoice</p>
          <h3 className="mt-3 font-display text-3xl text-white">Create a manual invoice for a managed client</h3>
          <div className="mt-5">
            <SuperadminInvoiceCreateForm
              organizations={admin.organizations.map((organization: any) => ({
                id: organization.id,
                name: organization.name
              }))}
            />
          </div>
        </Card>
      </div>
      <div className="grid gap-6">
        {invoices.items.length ? (
          invoices.items.map((invoice: any) => (
            <Card key={invoice.id}>
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-white">{invoice.organization_name}</p>
                  <p className="mt-1 text-sm text-slate-400">{invoice.currency.toUpperCase()} {invoice.amount} / Seats {invoice.seats}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{invoice.status}</span>
                  <Link
                    href={`/superadmin/clients/${invoice.organization_id}`}
                    className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10"
                  >
                    Open client
                  </Link>
                </div>
              </div>
              <div className="mt-5 grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
                <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
                  <p>Created {new Date(invoice.created_at).toLocaleString()}</p>
                  <p className="mt-2">Due {invoice.due_at ? new Date(invoice.due_at).toLocaleDateString() : "-"}</p>
                </div>
                <div className="rounded-3xl border border-white/10 bg-black/20 p-4">
                  <SuperadminInvoiceStatusForm invoiceId={invoice.id} defaultStatus={invoice.status} />
                  <form action={adminResendInvoiceAction} className="mt-3">
                    <input type="hidden" name="invoice_id" value={invoice.id} />
                    <button type="submit" className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10">
                      Resend notice
                    </button>
                  </form>
                </div>
              </div>
            </Card>
          ))
        ) : (
          <Card>
            <p className="text-white">No invoices are available yet.</p>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
