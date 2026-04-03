"use client";

import { useFormState, useFormStatus } from "react-dom";

import type { FormState } from "@/app/actions";
import { createOrganizationAction } from "@/app/actions";

const initialState: FormState = { status: "idle" };

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-glow to-accent px-4 py-2 text-sm font-medium text-ink transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70"
    >
      {pending ? "Creating..." : "Create Workspace"}
    </button>
  );
}

export function WorkspaceOrganizationForm() {
  const [state, action] = useFormState(createOrganizationAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input
        name="name"
        defaultValue="AtlasBI Enterprise"
        className="w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        placeholder="Workspace name"
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
