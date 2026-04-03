import { cancelSeatInviteAction } from "@/app/actions";
import { CreditCard, Receipt, Users, Wallet } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { BillingSeatForm } from "@/components/forms/billing-seat-form";
import { BillingPaymentForm } from "@/components/forms/billing-payment-form";
import { BillingUpgradeForm } from "@/components/forms/billing-upgrade-form";
import { Card } from "@/components/ui/card";
import { getBillingData } from "@/lib/data";

export default async function BillingPage() {
  const billing = await getBillingData();
  const subscription = billing.subscription;

  return (
    <AppShell eyebrow="Revenue Operations" title="Billing and Seats" feature="billing">
      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Subscription Control</p>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {[
              { label: "Plan", value: subscription?.plan ?? "growth", Icon: Wallet },
              { label: "Status", value: subscription?.status ?? "active", Icon: CreditCard },
              { label: "Seats", value: String(subscription?.seats ?? 0), Icon: Users },
              { label: "Renewal", value: subscription?.renews_at ? new Date(subscription.renews_at).toLocaleDateString() : "-", Icon: Receipt }
            ].map(({ label, value, Icon }) => (
              <div key={label} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                <Icon className="h-5 w-5 text-accent" />
                <p className="mt-4 text-sm text-slate-400">{label}</p>
                <p className="mt-2 font-display text-2xl text-white">{value}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Seat Allocation</p>
          <div className="mt-5 space-y-4">
            {[
              ["Assigned", billing.seat_usage.assigned],
              ["Pending Invites", billing.seat_usage.pending],
              ["Capacity", billing.seat_usage.capacity]
            ].map(([label, value]) => (
              <div key={String(label)} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-slate-300">{label}</p>
                  <p className="text-lg text-white">{value}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Payment Methods</p>
          <p className="mt-3 text-sm text-slate-400">
            Attach a default billing method for invoices, upgrades, and Stripe customer linkage.
          </p>
          <div className="mt-5">
            <BillingPaymentForm organizationId={billing.organization?.id ?? "org-1"} />
          </div>
          <div className="mt-5 space-y-3">
            {billing.payment_methods.map((item: any) => (
              <div key={item.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between">
                  <p className="text-white">{item.brand} ending in {item.last4}</p>
                  {item.is_default ? <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">Default</span> : null}
                </div>
                <p className="mt-2 text-sm text-slate-400">Expires {item.exp_month}/{item.exp_year}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Invoices</p>
          <p className="mt-3 text-sm text-slate-400">
            Prepare a checkout session to upgrade plans or change seat volume from the platform console.
          </p>
          <div className="mt-5">
            <BillingUpgradeForm
              organizationId={billing.organization?.id ?? "org-1"}
              currentPlan={subscription?.plan ?? "growth"}
              currentSeats={subscription?.seats ?? 10}
            />
          </div>
          <div className="mt-5 space-y-3">
            {billing.invoices.map((item: any) => (
              <div key={item.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between">
                  <p className="text-white">{item.currency.toUpperCase()} {item.amount}</p>
                  <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{item.status}</span>
                </div>
                <p className="mt-2 text-sm text-slate-400">Seats {item.seats} / Due {item.due_at ? new Date(item.due_at).toLocaleDateString() : "-"}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card>
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-accent">Seat Invites</p>
              <p className="mt-2 text-sm text-slate-400">Pending enterprise access orchestration for go-to-market teams.</p>
            </div>
            <a
              href={billing.portal_url ?? "#"}
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:border-accent/60 hover:text-accent"
            >
              Open billing portal
            </a>
          </div>
          <div className="mt-5">
            <BillingSeatForm organizationId={billing.organization?.id ?? "org-1"} />
          </div>
          <div className="mt-5 space-y-3">
            {billing.seat_invites.map((item: any) => (
              <div key={item.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between">
                  <p className="text-white">{item.email}</p>
                  <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{item.status}</span>
                </div>
                <p className="mt-2 text-sm text-slate-400">
                  {item.role} / Expires {item.expires_at ? new Date(item.expires_at).toLocaleDateString() : "-"}
                </p>
                {item.status === "pending" ? (
                  <form action={cancelSeatInviteAction} className="mt-3">
                    <input type="hidden" name="organization_id" value={billing.organization?.id ?? "org-1"} />
                    <input type="hidden" name="invite_id" value={item.id} />
                    <button type="submit" className="text-xs text-accent transition hover:text-white">
                      Cancel invite
                    </button>
                  </form>
                ) : null}
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Plan Catalog</p>
          <div className="mt-5 space-y-3">
            {billing.plans.map((plan: any) => (
              <div key={plan.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">{plan.label}</p>
                    <p className="mt-1 text-sm text-slate-400">
                      ${plan.monthly_price} / month / {plan.included_seats} seats included
                    </p>
                  </div>
                  <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{plan.id}</span>
                </div>
                <p className="mt-3 text-sm text-slate-400">
                  Search {plan.search_quota} / Exports {plan.export_quota} / Crawls {plan.crawl_quota}
                </p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
