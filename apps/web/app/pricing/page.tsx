import Link from "next/link";

import { MarketingShell } from "@/components/marketing-shell";
import { Card } from "@/components/ui/card";

const plans = [
  {
    name: "Starter",
    price: "$99",
    summary: "For focused teams that need AI search and core intelligence access.",
    features: ["AI search", "Company explorer", "Saved leads", "Workspace basics"],
    gate: "Search and explorer unlocked"
  },
  {
    name: "Growth",
    price: "$199",
    summary: "For teams that need exports, alerts, and strategic market visibility.",
    features: ["Everything in Starter", "Exports", "Alerts", "Insights"],
    gate: "Growth workflows unlocked"
  },
  {
    name: "Enterprise",
    price: "Custom",
    summary: "For larger clients needing scale, machine access, and advanced governance.",
    features: ["Everything in Growth", "API keys", "Enterprise billing", "Priority support"],
    gate: "Enterprise controls unlocked"
  }
];

export default function PricingPage() {
  return (
    <MarketingShell
      eyebrow="Pricing"
      title="Packages that control feature access cleanly."
      description="The customer dashboard is package-aware. Starter unlocks core intelligence workflows, Growth unlocks exports and insights, and Enterprise expands governance and platform access."
    >
      <div className="grid gap-6 xl:grid-cols-3">
        {plans.map((plan) => (
          <Card key={plan.name}>
            <p className="text-sm uppercase tracking-[0.24em] text-accent">{plan.name}</p>
            <p className="mt-4 font-display text-5xl text-white">{plan.price}</p>
            <p className="mt-4 text-sm leading-7 text-slate-400">{plan.summary}</p>
            <div className="mt-5 space-y-3">
              {plan.features.map((feature) => (
                <div key={feature} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
                  {feature}
                </div>
              ))}
            </div>
            <p className="mt-5 text-xs uppercase tracking-[0.24em] text-accent">{plan.gate}</p>
          </Card>
        ))}
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <h2 className="font-display text-3xl text-white">How gating works</h2>
          <div className="mt-5 space-y-3 text-sm leading-7 text-slate-400">
            <p>Starter users can search, explore companies, and manage saved leads.</p>
            <p>Growth users also unlock exports, alerts, and market insights.</p>
            <p>Enterprise customers expand governance, API access, and larger quotas.</p>
            <p>Superadmin controls are not part of customer packages and stay segregated for internal platform operators only.</p>
          </div>
        </Card>
        <Card>
          <h2 className="font-display text-3xl text-white">Next step</h2>
          <p className="mt-5 text-sm leading-7 text-slate-400">
            Customers sign in to access their workspace. Internal operators sign in to a separate superadmin operations console that manages clients, accounts, and crawlers.
          </p>
          <Link href="/login" className="mt-6 inline-flex text-sm text-accent transition hover:text-white">
            Login
          </Link>
        </Card>
      </div>
    </MarketingShell>
  );
}
