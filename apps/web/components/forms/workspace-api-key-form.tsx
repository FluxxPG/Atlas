"use client";

import { useFormState, useFormStatus } from "react-dom";

import type { FormState } from "@/app/actions";
import { createApiKeyAction } from "@/app/actions";

const initialState: FormState = { status: "idle" };

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-glow to-accent px-4 py-2 text-sm font-medium text-ink transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70"
    >
      {pending ? "Creating..." : "Create API Key"}
    </button>
  );
}

export function WorkspaceApiKeyForm({ organizationId }: { organizationId: string }) {
  const [state, action] = useFormState(createApiKeyAction, initialState);

  return (
    <form action={action} className="space-y-3">
      <input type="hidden" name="organization_id" value={organizationId} />
      <input
        name="name"
        defaultValue="Automation Worker"
        className="w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        placeholder="API key name"
      />
      <input
        name="scopes"
        defaultValue="search:read,company:read,exports:create"
        className="w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none"
        placeholder="Comma-separated scopes"
      />
      {state.message ? (
        <div
          className={`rounded-3xl px-4 py-3 text-sm ${
            state.status === "success"
              ? "border border-emerald-400/30 bg-emerald-500/10 text-emerald-200"
              : "border border-rose-400/30 bg-rose-500/10 text-rose-200"
          }`}
        >
          <p>{state.message}</p>
          {state.token ? <p className="mt-2 break-all font-mono text-xs text-white">{state.token}</p> : null}
        </div>
      ) : null}
      <SubmitButton />
    </form>
  );
}
