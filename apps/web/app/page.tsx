import Link from "next/link";
import { ArrowRight, BrainCircuit, Building2, Globe2, Radar, ShieldCheck, Telescope, Workflow } from "lucide-react";

import { MarketingShell } from "@/components/marketing-shell";
import { OrbScene } from "@/components/orb-scene";
import { Card } from "@/components/ui/card";

export default function HomePage() {
  return (
    <MarketingShell
      eyebrow="Global Company Intelligence"
      title="Discover, understand, and convert global business opportunities with AI."
      description="AtlasBI combines autonomous discovery, enrichment, buyer-intent detection, opportunity scoring, and natural-language search into a production-grade intelligence platform for modern go-to-market teams."
    >
      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <section className="glass relative min-h-[420px] overflow-hidden rounded-[34px] p-8 lg:p-10">
          <OrbScene />
          <div className="relative z-10 max-w-3xl">
            <p className="text-xs uppercase tracking-[0.35em] text-accent">From Website to Workspace</p>
            <div className="mt-5 space-y-4">
              {[
                "Visitors land on a polished marketing website and understand the product clearly.",
                "Customers click login, authenticate, and enter a client-only intelligence dashboard.",
                "Superadmins separately manage crawlers, clients, accounts, and platform operations."
              ].map((line) => (
                <div key={line} className="rounded-3xl border border-white/10 bg-black/20 px-5 py-4 text-sm leading-7 text-slate-200">
                  {line}
                </div>
              ))}
            </div>
            <div className="mt-8">
              <Link href="/login" className="inline-flex items-center gap-2 text-sm text-accent transition hover:text-white">
                Login to the platform
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>

        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Core Capabilities</p>
          <div className="mt-5 space-y-3">
            {[
              ["Global discovery", "Continuously expand company coverage using search discovery, websites, and geo-grid crawling."],
              ["AI search", "Ask for fast growing startups, CRM whitespace, or restaurants with bad reviews."],
              ["Signals and scoring", "Turn raw data into health, growth, and opportunity scores with buyer-intent clues."],
              ["Governed SaaS", "Separate public website, client dashboard, and superadmin operations with package gating."]
            ].map(([title, body]) => (
              <div key={title} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                <p className="text-white">{title}</p>
                <p className="mt-2 text-sm leading-6 text-slate-400">{body}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {[
          { title: "Company discovery", copy: "Hybrid discovery across websites, geo scans, and connectors.", Icon: Globe2 },
          { title: "Deep intelligence", copy: "Profiles with enrichment, signals, relationships, and opportunities.", Icon: BrainCircuit },
          { title: "Client workspaces", copy: "Package-aware dashboards for search, leads, alerts, and exports.", Icon: Building2 },
          { title: "Superadmin ops", copy: "Full control over clients, accounts, crawlers, and platform telemetry.", Icon: ShieldCheck }
        ].map(({ title, copy, Icon }) => (
          <Card key={title}>
            <Icon className="h-5 w-5 text-accent" />
            <h3 className="mt-4 font-display text-2xl text-white">{title}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-400">{copy}</p>
          </Card>
        ))}
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        {[
          { label: "Autonomous Crawling", value: "Search -> websites -> related companies -> repeat", Icon: Telescope },
          { label: "Opportunity Engine", value: "Marketing, software, and automation needs surfaced automatically", Icon: Radar },
          { label: "Platform Workflow", value: "Website, login, dashboard, package gating, and superadmin control", Icon: Workflow }
        ].map(({ label, value, Icon }) => (
          <Card key={label}>
            <Icon className="h-5 w-5 text-accent" />
            <p className="mt-4 text-sm uppercase tracking-[0.24em] text-slate-400">{label}</p>
            <p className="mt-3 font-display text-2xl text-white">{value}</p>
          </Card>
        ))}
      </div>
    </MarketingShell>
  );
}
