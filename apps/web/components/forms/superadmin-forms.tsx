"use client";

import { useFormState, useFormStatus } from "react-dom";

import type { FormState } from "@/app/actions";
import {
  adminArchiveOrganizationAction,
  adminCreateCrawlerPresetAction,
  adminCreateInvoiceAction,
  adminCreateMembershipAction,
  adminCreateOrganizationAction,
  adminCreatePaymentMethodAction,
  adminCreateSupportNoteAction,
  adminCreateSupportTicketAction,
  adminDeleteCrawlerPresetAction,
  adminDeletePaymentMethodAction,
  adminCreateUserAction,
  adminDeleteOrganizationAction,
  adminDeleteMembershipAction,
  adminRunCrawlerPresetAction,
  adminSetDefaultPaymentMethodAction,
  adminUpdateConfigAction,
  adminUpdateInvoiceAction,
  adminUpdateMembershipAction,
  adminUpdateOrganizationAction,
  adminUpdateSubscriptionAction,
  adminUpdateSupportTicketAction,
  adminUpdateUserAction
} from "@/app/actions";

const initialState: FormState = { status: "idle" };

function SubmitButton({ label, pendingLabel }: { label: string; pendingLabel: string }) {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-glow to-accent px-4 py-2 text-sm font-medium text-ink transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70"
    >
      {pending ? pendingLabel : label}
    </button>
  );
}

function StatusPill({ state }: { state: FormState }) {
  if (!state.message) {
    return null;
  }

  return (
    <div
      className={`rounded-3xl px-4 py-3 text-sm ${
        state.status === "success"
          ? "border border-emerald-400/30 bg-emerald-500/10 text-emerald-200"
          : "border border-rose-400/30 bg-rose-500/10 text-rose-200"
      }`}
    >
      {state.message}
    </div>
  );
}

export function SuperadminOrganizationCreateForm() {
  const [state, action] = useFormState(adminCreateOrganizationAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input
        name="name"
        className="w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        placeholder="Client organization name"
      />
      <div className="grid gap-3 md:grid-cols-3">
        <select name="plan" defaultValue="starter" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="starter">Starter</option>
          <option value="growth">Growth</option>
          <option value="enterprise">Enterprise</option>
        </select>
        <select name="status" defaultValue="active" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="active">Active</option>
          <option value="trialing">Trialing</option>
          <option value="suspended">Suspended</option>
        </select>
        <input
          name="regions"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Regions comma separated"
        />
      </div>
      <StatusPill state={state} />
      <SubmitButton label="Create client" pendingLabel="Creating..." />
    </form>
  );
}

export function SuperadminOrganizationUpdateForm({
  organizationId,
  defaultPlan,
  defaultStatus,
  defaultRegions
}: {
  organizationId: string;
  defaultPlan: string;
  defaultStatus: string;
  defaultRegions: string[];
}) {
  const [state, action] = useFormState(adminUpdateOrganizationAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input type="hidden" name="organization_id" value={organizationId} />
      <div className="grid gap-3 md:grid-cols-3">
        <select name="plan" defaultValue={defaultPlan} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="starter">Starter</option>
          <option value="growth">Growth</option>
          <option value="enterprise">Enterprise</option>
        </select>
        <select name="status" defaultValue={defaultStatus} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="active">Active</option>
          <option value="trialing">Trialing</option>
          <option value="suspended">Suspended</option>
        </select>
        <input
          name="regions"
          defaultValue={defaultRegions.join(", ")}
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Regions comma separated"
        />
      </div>
      <StatusPill state={state} />
      <SubmitButton label="Update client" pendingLabel="Saving..." />
    </form>
  );
}

export function SuperadminUserCreateForm({ organizations }: { organizations: Array<{ id: string; name: string }> }) {
  const [state, action] = useFormState(adminCreateUserAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <div className="grid gap-3 md:grid-cols-2">
        <input
          name="full_name"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Full name"
        />
        <input
          name="email"
          type="email"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="client.user@atlasbi.local"
        />
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <input
          name="password"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Temporary password"
        />
        <select name="role" defaultValue="analyst" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="analyst">Analyst</option>
          <option value="member">Member</option>
          <option value="operator">Operator</option>
          <option value="admin">Admin</option>
        </select>
        <select name="organization_id" defaultValue="" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="">Select client</option>
          {organizations.map((organization) => (
            <option key={organization.id} value={organization.id}>{organization.name}</option>
          ))}
        </select>
      </div>
      <StatusPill state={state} />
      <SubmitButton label="Create account" pendingLabel="Creating..." />
    </form>
  );
}

export function SuperadminUserUpdateForm({
  userId,
  defaultRole,
  defaultActive
}: {
  userId: string;
  defaultRole: string;
  defaultActive: boolean;
}) {
  const [state, action] = useFormState(adminUpdateUserAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input type="hidden" name="user_id" value={userId} />
      <div className="grid gap-3 md:grid-cols-2">
        <select name="role" defaultValue={defaultRole} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="analyst">Analyst</option>
          <option value="member">Member</option>
          <option value="operator">Operator</option>
          <option value="admin">Admin</option>
        </select>
        <select name="is_active" defaultValue={String(defaultActive)} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>
      <StatusPill state={state} />
      <SubmitButton label="Update account" pendingLabel="Saving..." />
    </form>
  );
}

export function SuperadminConfigForm({
  configs
}: {
  configs: {
    crawler_concurrency: number;
    crawler_max_retries: number;
    default_region: string;
    rate_limit_requests: number;
    rate_limit_window_seconds: number;
  };
}) {
  const [state, action] = useFormState(adminUpdateConfigAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <div className="grid gap-3 md:grid-cols-2">
        <input name="crawler_concurrency" type="number" defaultValue={configs.crawler_concurrency} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" />
        <input name="crawler_max_retries" type="number" defaultValue={configs.crawler_max_retries} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" />
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <input name="default_region" defaultValue={configs.default_region} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" />
        <input name="rate_limit_requests" type="number" defaultValue={configs.rate_limit_requests} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" />
        <input name="rate_limit_window_seconds" type="number" defaultValue={configs.rate_limit_window_seconds} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" />
      </div>
      <StatusPill state={state} />
      <SubmitButton label="Update config" pendingLabel="Saving..." />
    </form>
  );
}

export function SuperadminMembershipCreateForm({
  organizationId,
  users
}: {
  organizationId: string;
  users: Array<{ id: string; name: string; email: string }>;
}) {
  const [state, action] = useFormState(adminCreateMembershipAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input type="hidden" name="organization_id" value={organizationId} />
      <div className="grid gap-3 md:grid-cols-2">
        <select name="user_id" defaultValue="" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="">Select user</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>{user.name} / {user.email}</option>
          ))}
        </select>
        <select name="role" defaultValue="member" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="member">Member</option>
          <option value="owner">Owner</option>
          <option value="analyst">Analyst</option>
          <option value="operator">Operator</option>
        </select>
      </div>
      <StatusPill state={state} />
      <SubmitButton label="Add membership" pendingLabel="Adding..." />
    </form>
  );
}

export function SuperadminMembershipUpdateForm({
  organizationId,
  membershipId,
  defaultRole,
  defaultIsDefault
}: {
  organizationId: string;
  membershipId: string;
  defaultRole: string;
  defaultIsDefault: boolean;
}) {
  const [state, action] = useFormState(adminUpdateMembershipAction, initialState);

  return (
    <div className="space-y-3">
      <form action={action} className="space-y-3">
        <input type="hidden" name="organization_id" value={organizationId} />
        <input type="hidden" name="membership_id" value={membershipId} />
        <div className="grid gap-3 md:grid-cols-2">
          <select name="role" defaultValue={defaultRole} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
            <option value="member">Member</option>
            <option value="owner">Owner</option>
            <option value="analyst">Analyst</option>
            <option value="operator">Operator</option>
          </select>
          <select name="is_default" defaultValue={String(defaultIsDefault)} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
            <option value="false">Not default</option>
            <option value="true">Default</option>
          </select>
        </div>
        <StatusPill state={state} />
        <SubmitButton label="Update membership" pendingLabel="Saving..." />
      </form>
      <form action={adminDeleteMembershipAction}>
        <input type="hidden" name="organization_id" value={organizationId} />
        <input type="hidden" name="membership_id" value={membershipId} />
        <button type="submit" className="rounded-full border border-rose-400/30 bg-rose-500/10 px-4 py-2 text-sm text-rose-200 transition hover:bg-rose-500/20">
          Remove
        </button>
      </form>
    </div>
  );
}

export function SuperadminSubscriptionForm({
  organizationId,
  subscription,
  fallbackPlan
}: {
  organizationId: string;
  subscription?: {
    plan?: string;
    status?: string;
    seats?: number;
    search_quota?: number;
    export_quota?: number;
    crawl_quota?: number;
  } | null;
  fallbackPlan: string;
}) {
  const [state, action] = useFormState(adminUpdateSubscriptionAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input type="hidden" name="organization_id" value={organizationId} />
      <div className="grid gap-3 md:grid-cols-3">
        <select name="plan" defaultValue={subscription?.plan ?? fallbackPlan} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="starter">Starter</option>
          <option value="growth">Growth</option>
          <option value="enterprise">Enterprise</option>
        </select>
        <select name="status" defaultValue={subscription?.status ?? "active"} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="active">Active</option>
          <option value="trialing">Trialing</option>
          <option value="pending_payment">Pending Payment</option>
          <option value="past_due">Past Due</option>
          <option value="suspended">Suspended</option>
        </select>
        <input
          name="seats"
          type="number"
          defaultValue={subscription?.seats ?? 5}
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Seats"
        />
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <input
          name="search_quota"
          type="number"
          defaultValue={subscription?.search_quota ?? 2500}
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Search quota"
        />
        <input
          name="export_quota"
          type="number"
          defaultValue={subscription?.export_quota ?? 500}
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Export quota"
        />
        <input
          name="crawl_quota"
          type="number"
          defaultValue={subscription?.crawl_quota ?? 1000}
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Crawl quota"
        />
      </div>
      <StatusPill state={state} />
      <SubmitButton label="Update subscription" pendingLabel="Saving..." />
    </form>
  );
}

export function SuperadminOrganizationLifecycleForm({ organizationId }: { organizationId: string }) {
  return (
    <div className="flex flex-wrap gap-3">
      <form action={adminArchiveOrganizationAction}>
        <input type="hidden" name="organization_id" value={organizationId} />
        <button type="submit" className="rounded-full border border-amber-400/30 bg-amber-500/10 px-4 py-2 text-sm text-amber-200 transition hover:bg-amber-500/20">
          Archive client
        </button>
      </form>
      <form action={adminDeleteOrganizationAction}>
        <input type="hidden" name="organization_id" value={organizationId} />
        <button type="submit" className="rounded-full border border-rose-400/30 bg-rose-500/10 px-4 py-2 text-sm text-rose-200 transition hover:bg-rose-500/20">
          Delete client
        </button>
      </form>
    </div>
  );
}

export function SuperadminInvoiceStatusForm({
  invoiceId,
  defaultStatus
}: {
  invoiceId: string;
  defaultStatus: string;
}) {
  const [state, action] = useFormState(adminUpdateInvoiceAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input type="hidden" name="invoice_id" value={invoiceId} />
      <select name="status" defaultValue={defaultStatus} className="w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
        <option value="draft">Draft</option>
        <option value="open">Open</option>
        <option value="requires_payment">Requires Payment</option>
        <option value="paid">Paid</option>
        <option value="void">Void</option>
        <option value="payment_failed">Payment Failed</option>
      </select>
      <StatusPill state={state} />
      <SubmitButton label="Update invoice" pendingLabel="Saving..." />
    </form>
  );
}

export function SuperadminInvoiceCreateForm({
  organizations
}: {
  organizations: Array<{ id: string; name: string }>;
}) {
  const [state, action] = useFormState(adminCreateInvoiceAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <div className="grid gap-3 md:grid-cols-2">
        <select name="organization_id" defaultValue="" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="">Select client</option>
          {organizations.map((organization) => (
            <option key={organization.id} value={organization.id}>{organization.name}</option>
          ))}
        </select>
        <input name="amount" type="number" step="0.01" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Amount" />
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <input name="seats" type="number" defaultValue="1" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Seats" />
        <input name="currency" defaultValue="usd" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Currency" />
        <select name="status" defaultValue="open" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="draft">Draft</option>
          <option value="open">Open</option>
          <option value="requires_payment">Requires Payment</option>
        </select>
      </div>
      <StatusPill state={state} />
      <SubmitButton label="Generate invoice" pendingLabel="Creating..." />
    </form>
  );
}

export function SuperadminSupportTicketCreateForm({
  organizations,
  users
}: {
  organizations: Array<{ id: string; name: string }>;
  users: Array<{ id: string; name: string }>;
}) {
  const [state, action] = useFormState(adminCreateSupportTicketAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input
        name="title"
        className="w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        placeholder="Ticket title"
      />
      <div className="grid gap-3 md:grid-cols-3">
        <select name="organization_id" defaultValue="" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="">Platform-wide ticket</option>
          {organizations.map((organization) => (
            <option key={organization.id} value={organization.id}>{organization.name}</option>
          ))}
        </select>
        <select name="assignee_user_id" defaultValue="" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="">Unassigned</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>{user.name}</option>
          ))}
        </select>
        <select name="priority" defaultValue="medium" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <select name="status" defaultValue="open" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="open">Open</option>
          <option value="investigating">Investigating</option>
          <option value="blocked">Blocked</option>
          <option value="resolved">Resolved</option>
        </select>
        <input name="sla_label" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="SLA label (e.g. 24h response)" />
      </div>
      <textarea
        name="description"
        rows={4}
        className="w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        placeholder="Describe the issue, client impact, and next action"
      />
      <StatusPill state={state} />
      <SubmitButton label="Create ticket" pendingLabel="Creating..." />
    </form>
  );
}

export function SuperadminSupportTicketUpdateForm({
  ticketId,
  defaultPriority,
  defaultStatus,
  defaultDescription,
  defaultAssigneeUserId,
  defaultSlaLabel,
  users
}: {
  ticketId: string;
  defaultPriority: string;
  defaultStatus: string;
  defaultDescription: string;
  defaultAssigneeUserId?: string | null;
  defaultSlaLabel?: string | null;
  users: Array<{ id: string; name: string }>;
}) {
  const [state, action] = useFormState(adminUpdateSupportTicketAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input type="hidden" name="ticket_id" value={ticketId} />
      <div className="grid gap-3 md:grid-cols-3">
        <select name="assignee_user_id" defaultValue={defaultAssigneeUserId ?? ""} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="">Unassigned</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>{user.name}</option>
          ))}
        </select>
        <select name="priority" defaultValue={defaultPriority} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
        <select name="status" defaultValue={defaultStatus} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="open">Open</option>
          <option value="investigating">Investigating</option>
          <option value="blocked">Blocked</option>
          <option value="resolved">Resolved</option>
        </select>
      </div>
      <input
        name="sla_label"
        defaultValue={defaultSlaLabel ?? ""}
        className="w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        placeholder="SLA label"
      />
      <textarea
        name="description"
        defaultValue={defaultDescription}
        rows={4}
        className="w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
      />
      <StatusPill state={state} />
      <SubmitButton label="Update ticket" pendingLabel="Saving..." />
    </form>
  );
}

export function SuperadminPaymentMethodCreateForm({
  organizations
}: {
  organizations: Array<{ id: string; name: string }>;
}) {
  const [state, action] = useFormState(adminCreatePaymentMethodAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <div className="grid gap-3 md:grid-cols-2">
        <select name="organization_id" defaultValue="" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="">Select client</option>
          {organizations.map((organization) => (
            <option key={organization.id} value={organization.id}>{organization.name}</option>
          ))}
        </select>
        <input name="provider" defaultValue="manual" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Provider" />
      </div>
      <div className="grid gap-3 md:grid-cols-4">
        <input name="brand" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Brand" />
        <input name="last4" maxLength={4} className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Last 4" />
        <input name="exp_month" type="number" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Exp month" />
        <input name="exp_year" type="number" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Exp year" />
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <select name="is_default" defaultValue="true" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="true">Default</option>
          <option value="false">Not default</option>
        </select>
      </div>
      <StatusPill state={state} />
      <SubmitButton label="Add payment method" pendingLabel="Creating..." />
    </form>
  );
}

export function SuperadminPaymentMethodActions({
  paymentMethodId,
  organizationId,
  isDefault
}: {
  paymentMethodId: string;
  organizationId: string;
  isDefault: boolean;
}) {
  return (
    <div className="flex flex-wrap gap-3">
      {!isDefault ? (
        <form action={adminSetDefaultPaymentMethodAction}>
          <input type="hidden" name="payment_method_id" value={paymentMethodId} />
          <input type="hidden" name="organization_id" value={organizationId} />
          <button type="submit" className="rounded-full border border-emerald-400/30 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-200 transition hover:bg-emerald-500/20">
            Make default
          </button>
        </form>
      ) : null}
      <form action={adminDeletePaymentMethodAction}>
        <input type="hidden" name="payment_method_id" value={paymentMethodId} />
        <input type="hidden" name="organization_id" value={organizationId} />
        <button type="submit" className="rounded-full border border-rose-400/30 bg-rose-500/10 px-4 py-2 text-sm text-rose-200 transition hover:bg-rose-500/20">
          Delete method
        </button>
      </form>
    </div>
  );
}

export function SuperadminSupportNoteForm({ ticketId }: { ticketId: string }) {
  const [state, action] = useFormState(adminCreateSupportNoteAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input type="hidden" name="ticket_id" value={ticketId} />
      <textarea
        name="body"
        rows={3}
        className="w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        placeholder="Add an internal support note, next step, or customer follow-up"
      />
      <StatusPill state={state} />
      <SubmitButton label="Add note" pendingLabel="Saving..." />
    </form>
  );
}

export function SuperadminCrawlerPresetForm() {
  const [state, action] = useFormState(adminCreateCrawlerPresetAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <div className="grid gap-3 md:grid-cols-2">
        <input
          name="name"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Preset name"
        />
        <select name="mode" defaultValue="discovery" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="discovery">Discovery</option>
          <option value="geo">Geo grid</option>
        </select>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <input name="query" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Discovery query" />
        <input name="city" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="City" />
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <input name="region" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Region" />
        <input name="country" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Country" />
        <input name="source" defaultValue="hybrid" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Source" />
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <input name="keywords" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Keywords comma separated" />
        <input name="industries" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Industries comma separated" />
      </div>
      <div className="grid gap-3 md:grid-cols-4">
        <input name="employee_range" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Employee range" />
        <input name="min_reviews" type="number" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Min reviews" />
        <input name="max_rating" type="number" step="0.1" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Max rating" />
        <select name="has_website" defaultValue="" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none">
          <option value="">Website filter</option>
          <option value="true">Has website</option>
          <option value="false">No website</option>
        </select>
      </div>
      <div className="grid gap-3 md:grid-cols-4">
        <input name="latitude" type="number" step="0.0001" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Latitude" />
        <input name="longitude" type="number" step="0.0001" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Longitude" />
        <input name="radius_km" type="number" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Radius km" />
        <input name="keyword_set" className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none" placeholder="Geo keywords comma separated" />
      </div>
      <StatusPill state={state} />
      <SubmitButton label="Save preset" pendingLabel="Saving..." />
    </form>
  );
}

export function SuperadminCrawlerPresetActions({
  presetId,
  canDelete = true
}: {
  presetId: string;
  canDelete?: boolean;
}) {
  return (
    <div className="flex flex-wrap gap-3">
      <form action={adminRunCrawlerPresetAction}>
        <input type="hidden" name="preset_id" value={presetId} />
        <button type="submit" className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10">
          Run preset
        </button>
      </form>
      {canDelete ? (
        <form action={adminDeleteCrawlerPresetAction}>
          <input type="hidden" name="preset_id" value={presetId} />
          <button type="submit" className="rounded-full border border-rose-400/30 bg-rose-500/10 px-4 py-2 text-sm text-rose-200 transition hover:bg-rose-500/20">
            Delete preset
          </button>
        </form>
      ) : null}
    </div>
  );
}
