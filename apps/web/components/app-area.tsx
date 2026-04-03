import Link from "next/link";
import { ArrowRight, CheckCircle2, Globe2, Radar, ShieldCheck, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";

const pricingTiers = [
  {
    name: "Starter",
    price: "$99",
    subtitle: "Prospecting teams validating new segments",
    features: ["AI search", "company explorer", "saved leads", "basic exports"]
  },
  {
    name: "Growth",
    price: "$199",
    subtitle: "Revenue teams running repeatable outbound programs",
    features: ["Signals and alerts", "insights", "workspace controls", "higher quotas"]
  },
  {
    name: "Enterprise",
    price: "$499",
    subtitle: "Multi-market teams with machine access and governance",
    features: ["API keys", "billing ops", "advanced quotas", "enterprise workflows"]
  }
];

export function MarketingPage() {
  const featureHighlights = [
    { label: "Global company discovery", Icon: Globe2 },
    { label: "Signals, intent, and opportunity scoring", Icon: Radar },
    { label: "Secure workspaces with machine access", Icon: ShieldCheck }
  ];

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="mesh" />
      <div className="mx-auto max-w-[1480px] px-4 py-6 lg:px-6">
        <header className="glass flex items-center justify-between rounded-[30px] px-6 py-5">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-accent">Global Intelligence</p>
            <h1 className="mt-2 font-display text-3xl text-white">AtlasBI</h1>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10">
              Login
            </Link>
            <Button asChild>
              <Link href="/login">Book Demo</Link>
            </Button>
          </div>
        </header>

        <section className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="glass rounded-[34px] p-8 lg:p-10">
            <p className="text-xs uppercase tracking-[0.35em] text-accent">AI Business Intelligence Platform</p>
            <h2 className="mt-4 max-w-4xl font-display text-6xl leading-[1.05] text-white">
              Discover companies, map opportunities, and search markets with AI-native intelligence.
            </h2>
            <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300">
              AtlasBI gives revenue, product, and strategy teams a live intelligence system for company discovery,
              enrichment, opportunity scoring, buyer intent, and vector search.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild>
                <Link href="/login">
                  Start Free Workflow
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Link href="#pricing" className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10">
                View Pricing
              </Link>
            </div>
            <div className="mt-10 grid gap-4 md:grid-cols-3">
              {featureHighlights.map(({ label, Icon }) => (
                <div key={String(label)} className="rounded-3xl border border-white/10 bg-black/20 p-5">
                  <Icon className="h-5 w-5 text-accent" />
                  <p className="mt-4 text-sm text-slate-200">{label}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="glass rounded-[34px] p-8">
            <p className="text-xs uppercase tracking-[0.35em] text-accent">Product Flow</p>
            <div className="mt-6 space-y-4">
              {[
                "Land on the AtlasBI website",
                "Sign in from the login page",
                "Enter the customer dashboard",
                "Search companies, save leads, export, and monitor alerts",
                "Superadmins manage crawl seeds, geographies, and ingestion separately"
              ].map((step, index) => (
                <div key={step} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                  <p className="text-xs uppercase tracking-[0.24em] text-accent">Step {index + 1}</p>
                  <p className="mt-2 text-white">{step}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-6 grid gap-6 xl:grid-cols-3">
          {[
            {
              title: "Search everything",
              copy: "Natural-language retrieval across companies, industries, signals, and opportunities.",
              Icon: Sparkles
            },
            {
              title: "Act on live intelligence",
              copy: "Move from discovery to exportable lead lists, alerts, and company intelligence profiles.",
              Icon: CheckCircle2
            },
            {
              title: "Keep operations separate",
              copy: "Customer users never see crawler controls. Superadmins manage ingestion in a dedicated control center.",
              Icon: ShieldCheck
            }
          ].map(({ title, copy, Icon }) => (
            <div key={title} className="glass rounded-[30px] p-6">
              <Icon className="h-6 w-6 text-accent" />
              <h3 className="mt-4 font-display text-2xl text-white">{title}</h3>
              <p className="mt-3 text-sm leading-7 text-slate-300">{copy}</p>
            </div>
          ))}
        </section>

        <section id="pricing" className="mt-6 glass rounded-[34px] p-8 lg:p-10">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-accent">Pricing</p>
              <h3 className="mt-3 font-display text-4xl text-white">Feature-gated plans for every stage</h3>
            </div>
            <p className="max-w-2xl text-sm text-slate-400">
              Search and explorer access start immediately. Signals, exports, API access, and governance expand by package.
            </p>
          </div>
          <div className="mt-8 grid gap-6 lg:grid-cols-3">
            {pricingTiers.map((tier) => (
              <div key={tier.name} className="rounded-[28px] border border-white/10 bg-white/5 p-6">
                <p className="text-xs uppercase tracking-[0.24em] text-accent">{tier.name}</p>
                <div className="mt-3 flex items-end gap-2">
                  <p className="font-display text-5xl text-white">{tier.price}</p>
                  <p className="pb-2 text-sm text-slate-400">/ month</p>
                </div>
                <p className="mt-3 text-sm text-slate-300">{tier.subtitle}</p>
                <div className="mt-6 space-y-3">
                  {tier.features.map((feature) => (
                    <div key={feature} className="flex items-center gap-3 text-sm text-slate-200">
                      <CheckCircle2 className="h-4 w-4 text-accent" />
                      {feature}
                    </div>
                  ))}
                </div>
                <Button asChild className="mt-6 w-full">
                  <Link href="/login">Choose {tier.name}</Link>
                </Button>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
