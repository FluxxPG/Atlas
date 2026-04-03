"use client";

import { useFormState, useFormStatus } from "react-dom";

import type { FormState } from "@/app/actions";
import { createCheckoutSessionAction } from "@/app/actions";

const initialState: FormState = { status: "idle" };

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-glow to-accent px-4 py-2 text-sm font-medium text-ink transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70"
    >
      {pending ? "Preparing..." : "Create Upgrade Checkout"}
    </button>
  );
}

export function BillingUpgradeForm({
  organizationId,
  currentPlan,
  currentSeats
}: {
  organizationId: string;
  currentPlan: string;
  currentSeats: number;
}) {
  const [state, action] = useFormState(createCheckoutSessionAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input type="hidden" name="organization_id" value={organizationId} />
      <div className="grid gap-3 md:grid-cols-2">
        <select
          name="plan"
          defaultValue={currentPlan}
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        >
          <option value="starter">Starter</option>
          <option value="growth">Growth</option>
          <option value="enterprise">Enterprise</option>
        </select>
        <input
          name="seats"
          type="number"
          min={1}
          defaultValue={String(currentSeats)}
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="Seats"
        />
      </div>
      {state.message ? (
        <div
          className={`rounded-3xl px-4 py-3 text-sm ${
            state.status === "success"
              ? "border border-emerald-400/30 bg-emerald-500/10 text-emerald-200"
              : "border border-rose-400/30 bg-rose-500/10 text-rose-200"
          }`}
        >
          <p>{state.message}</p>
          {state.token ? (
            <a href={state.token} target="_blank" rel="noreferrer" className="mt-2 inline-flex text-xs text-white underline">
              Open checkout
            </a>
          ) : null}
        </div>
      ) : null}
      <SubmitButton />
    </form>
  );
}
