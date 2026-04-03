import Link from "next/link";
import { ChevronLeft } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import {
  SuperadminMembershipCreateForm,
  SuperadminMembershipUpdateForm,
  SuperadminOrganizationLifecycleForm,
  SuperadminOrganizationUpdateForm,
  SuperadminSubscriptionForm
} from "@/components/forms/superadmin-forms";
import { Card } from "@/components/ui/card";
import { getAdminData, getAdminOrganizationDetail } from "@/lib/data";

export default async function SuperadminClientDetailPage({
  params
}: {
  params: { id: string };
}) {
  const [detailResponse, admin] = await Promise.all([
    getAdminOrganizationDetail(params.id),
    getAdminData()
  ]);

  if (!detailResponse || "status" in detailResponse) {
    return (
      <AppShell eyebrow="Superadmin Client" title="Client not found" mode="superadmin">
        <Card>
          <p className="text-white">This client organization is not available.</p>
        </Card>
      </AppShell>
    );
  }

  const detail: any = detailResponse;
  const organization = detail.organization;
  const subscription = detail.subscription;

  return (
    <AppShell eyebrow="Superadmin Client" title={organization.name} mode="superadmin">
      <Link href="/superadmin/clients" className="mb-6 inline-flex items-center gap-2 text-sm text-slate-300 hover:text-white">
        <ChevronLeft className="h-4 w-4" />
        Back to clients
      </Link>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Client Profile</p>
          <h2 className="mt-3 font-display text-3xl text-white">{organization.name}</h2>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm text-slate-400">Plan</p>
              <p className="mt-2 text-white">{organization.plan}</p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm text-slate-400">Status</p>
              <p className="mt-2 text-white">{organization.status}</p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm text-slate-400">Slug</p>
              <p className="mt-2 text-white">{organization.slug}</p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm text-slate-400">Regions</p>
              <p className="mt-2 text-white">{organization.settings?.regions?.join(", ") || "Not set"}</p>
            </div>
          </div>
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
          <div className="mt-6 rounded-3xl border border-white/10 bg-black/20 p-5">
            <p className="text-sm uppercase tracking-[0.24em] text-accent">Lifecycle controls</p>
            <div className="mt-4">
              <SuperadminOrganizationLifecycleForm organizationId={organization.id} />
            </div>
          </div>
        </Card>

        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Subscription and Usage</p>
          <div className="mt-5 space-y-3">
            {[
              ["Subscription plan", subscription?.plan ?? "n/a"],
              ["Subscription status", subscription?.status ?? "n/a"],
              ["Seats", subscription?.seats ?? 0],
              ["Search usage", `${detail.usage.search ?? 0} / ${subscription?.search_quota ?? 0}`],
              ["Export usage", `${detail.usage.export ?? 0} / ${subscription?.export_quota ?? 0}`],
              ["Crawl usage", `${detail.usage.crawl ?? 0} / ${subscription?.crawl_quota ?? 0}`]
            ].map(([label, value]) => (
              <div key={String(label)} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between">
                  <p className="text-slate-300">{label}</p>
                  <p className="text-white">{value}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-6 rounded-3xl border border-white/10 bg-black/20 p-5">
            <p className="text-sm uppercase tracking-[0.24em] text-accent">Update subscription</p>
            <div className="mt-4">
              <SuperadminSubscriptionForm
                organizationId={organization.id}
                subscription={subscription}
                fallbackPlan={organization.plan}
              />
            </div>
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card>
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-accent">Memberships</p>
              <h3 className="mt-3 font-display text-2xl text-white">Manage client members</h3>
            </div>
          </div>
          <div className="mt-5 rounded-3xl border border-white/10 bg-black/20 p-5">
            <SuperadminMembershipCreateForm
              organizationId={organization.id}
              users={admin.users.map((user: any) => ({
                id: user.id,
                name: user.full_name,
                email: user.email
              }))}
            />
          </div>
          <div className="mt-5 space-y-4">
            {detail.memberships.length ? (
              detail.memberships.map((membership: any) => (
                <div key={membership.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="text-white">{membership.user?.full_name ?? "Unknown user"}</p>
                      <p className="mt-1 text-sm text-slate-400">{membership.user?.email}</p>
                    </div>
                    <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{membership.role}</span>
                  </div>
                  <div className="mt-4">
                    <SuperadminMembershipUpdateForm
                      organizationId={organization.id}
                      membershipId={membership.id}
                      defaultRole={membership.role}
                      defaultIsDefault={membership.is_default}
                    />
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                No memberships yet.
              </div>
            )}
          </div>
        </Card>

        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Billing and Finance</p>
          <div className="mt-5 space-y-4">
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Payment methods</p>
              <div className="mt-3 space-y-3">
                {detail.payment_methods.length ? (
                  detail.payment_methods.map((method: any) => (
                    <div key={method.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                      <div className="flex items-center justify-between">
                        <p className="text-white">{method.brand} ending in {method.last4}</p>
                        {method.is_default ? <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">Default</span> : null}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                    No payment methods attached.
                  </div>
                )}
              </div>
            </div>
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Invoices</p>
              <div className="mt-3 space-y-3">
                {detail.invoices.length ? (
                  detail.invoices.map((invoice: any) => (
                    <div key={invoice.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                      <div className="flex items-center justify-between">
                        <p className="text-white">{invoice.currency.toUpperCase()} {invoice.amount}</p>
                        <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{invoice.status}</span>
                      </div>
                      <p className="mt-2 text-sm text-slate-400">Seats {invoice.seats}</p>
                    </div>
                  ))
                ) : (
                  <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                    No invoices yet.
                  </div>
                )}
              </div>
            </div>
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Seat Invites</p>
          <div className="mt-5 space-y-3">
            {detail.seat_invites.length ? (
              detail.seat_invites.map((invite: any) => (
                <div key={invite.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center justify-between">
                    <p className="text-white">{invite.email}</p>
                    <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{invite.status}</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-400">{invite.role}</p>
                </div>
              ))
            ) : (
              <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                No seat invites for this client.
              </div>
            )}
          </div>
        </Card>

        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Audit Timeline</p>
          <div className="mt-5 space-y-3">
            {detail.audit_events.length ? (
              detail.audit_events.map((event: any) => (
                <div key={event.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center justify-between gap-4">
                    <p className="text-white">{event.action}</p>
                    <p className="text-xs text-slate-500">{new Date(event.created_at).toLocaleString()}</p>
                  </div>
                  <p className="mt-2 text-sm text-slate-400">{event.resource_type} / {event.resource_id}</p>
                </div>
              ))
            ) : (
              <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                No audit events for this client yet.
              </div>
            )}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
