"use client";

import { useFormState, useFormStatus } from "react-dom";

import type { FormState } from "@/app/actions";
import { loginAction } from "@/app/actions";

const initialState: FormState = { status: "idle" };

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="inline-flex w-full items-center justify-center rounded-full bg-gradient-to-r from-glow to-accent px-4 py-3 text-sm font-medium text-ink transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-70"
    >
      {pending ? "Signing in..." : "Sign In"}
    </button>
  );
}

export function LoginForm() {
  const [state, formAction] = useFormState(loginAction, initialState);

  return (
    <form action={formAction} className="space-y-4">
      <div>
        <label htmlFor="email" className="text-xs uppercase tracking-[0.24em] text-slate-400">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          defaultValue="admin@atlasbi.local"
          className="mt-2 w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none placeholder:text-slate-500"
          placeholder="admin@atlasbi.local"
        />
      </div>
      <div>
        <label htmlFor="password" className="text-xs uppercase tracking-[0.24em] text-slate-400">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          defaultValue="AtlasBI-Admin-2026"
          className="mt-2 w-full rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none placeholder:text-slate-500"
          placeholder="••••••••"
        />
      </div>
      {state.status === "error" ? (
        <div className="rounded-3xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
          {state.message}
        </div>
      ) : null}
      <SubmitButton />
    </form>
  );
}
