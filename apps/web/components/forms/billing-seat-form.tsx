"use client";

import { useFormState, useFormStatus } from "react-dom";

import type { FormState } from "@/app/actions";
import { createSeatInviteAction } from "@/app/actions";

const initialState: FormState = { status: "idle" };

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-glow to-accent px-4 py-2 text-sm font-medium text-ink transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70"
    >
      {pending ? "Inviting..." : "Invite Seat"}
    </button>
  );
}

export function BillingSeatForm({ organizationId }: { organizationId: string }) {
  const [state, action] = useFormState(createSeatInviteAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input type="hidden" name="organization_id" value={organizationId} />
      <div className="grid gap-3 md:grid-cols-[1fr_180px]">
        <input
          name="email"
          type="email"
          defaultValue="ops@atlasbi.local"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
          placeholder="teammate@company.com"
        />
        <select
          name="role"
          defaultValue="analyst"
          className="rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        >
          <option value="member">Member</option>
          <option value="analyst">Analyst</option>
          <option value="operator">Operator</option>
          <option value="admin">Admin</option>
        </select>
      </div>
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
