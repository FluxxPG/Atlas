"use client";

import { useFormState, useFormStatus } from "react-dom";

import type { FormState } from "@/app/actions";
import { attachPaymentMethodAction } from "@/app/actions";

const initialState: FormState = { status: "idle" };

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-glow to-accent px-4 py-2 text-sm font-medium text-ink transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70"
    >
      {pending ? "Saving..." : "Attach Payment Method"}
    </button>
  );
}

export function BillingPaymentForm({ organizationId }: { organizationId: string }) {
  const [state, action] = useFormState(attachPaymentMethodAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input type="hidden" name="organization_id" value={organizationId} />
      <div className="grid gap-3 md:grid-cols-2">
        <input
          name="brand"
          defaultValue="Visa"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Brand"
        />
        <input
          name="last4"
          defaultValue="4242"
          maxLength={4}
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Last 4 digits"
        />
      </div>
      <div className="grid gap-3 md:grid-cols-4">
        <input
          name="exp_month"
          type="number"
          defaultValue="12"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Month"
        />
        <input
          name="exp_year"
          type="number"
          defaultValue={String(new Date().getFullYear() + 2)}
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Year"
        />
        <input
          name="provider_customer_id"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none md:col-span-2"
          placeholder="Stripe customer id (optional)"
        />
      </div>
      <input
        name="provider_payment_method_id"
        className="w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        placeholder="Stripe payment method id (optional)"
      />
      {state.message ? (
        <div
          className={`rounded-3xl px-4 py-3 text-sm ${
            state.status === "success"
              ? "border border-emerald-400/30 bg-emerald-500/10 text-emerald-200"
              : "border border-rose-400/30 bg-rose-500/10 text-rose-200"
          }`}
        >
          {state.message}
        </div>
      ) : null}
      <SubmitButton />
    </form>
  );
}
