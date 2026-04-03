import Link from "next/link";
import { KeyRound, Radar, ShieldCheck } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { LoginForm } from "@/components/forms/login-form";
import { redirectIfAuthenticated } from "@/lib/access";

const featureCards: Array<{ label: string; Icon: LucideIcon }> = [
  { label: "Secure workspace sessions", Icon: ShieldCheck },
  { label: "Machine access and scoped API keys", Icon: KeyRound },
  { label: "Signals, trends, and discovery control", Icon: Radar }
];

export default async function LoginPage() {
  await redirectIfAuthenticated();

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="mesh" />
      <div className="mx-auto grid min-h-screen max-w-[1320px] gap-8 px-4 py-8 lg:grid-cols-[1.15fr_0.85fr] lg:px-6">
        <section className="glass relative overflow-hidden rounded-[34px] p-8 lg:p-10">
          <div className="absolute inset-0 bg-aurora opacity-50" />
          <div className="relative">
            <p className="text-xs uppercase tracking-[0.35em] text-accent">Global Intelligence</p>
            <h1 className="mt-4 font-display text-5xl text-white">AtlasBI Workspace Login</h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">
              Sign in to access your client dashboard or, if you are a superadmin, the separate crawler operations control surface.
            </p>
            <div className="mt-10 grid gap-4 md:grid-cols-3">
              {featureCards.map(({ label, Icon }) => (
                <div key={label} className="rounded-3xl border border-white/10 bg-black/20 p-5">
                  <Icon className="h-5 w-5 text-accent" />
                  <p className="mt-4 text-sm text-slate-200">{label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="glass rounded-[34px] p-8 lg:p-10">
          <p className="text-xs uppercase tracking-[0.35em] text-accent">Authentication</p>
          <h2 className="mt-4 font-display text-3xl text-white">Sign in to continue</h2>
          <p className="mt-3 text-sm text-slate-400">
            Use the seeded admin credentials to access the full platform locally.
          </p>
          <div className="mt-8">
            <LoginForm />
          </div>
          <div className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5 text-sm text-slate-300">
            <p className="text-white">Local bootstrap credentials</p>
            <p className="mt-2">Email: admin@atlasbi.local</p>
            <p className="mt-1">Password: AtlasBI-Admin-2026</p>
            <div className="mt-4 border-t border-white/10 pt-4">
              <p className="text-white">Client demo credentials</p>
              <p className="mt-2">Email: client@atlasbi.local</p>
              <p className="mt-1">Password: AtlasBI-Client-2026</p>
            </div>
          </div>
          <Link href="/" className="mt-6 inline-flex text-sm text-accent hover:text-white">
            Back to website
          </Link>
        </section>
      </div>
    </div>
  );
}
