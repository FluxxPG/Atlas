import { BarChart3, BrainCircuit, Globe2, Network, Radar, Search, ShieldCheck, Telescope } from "lucide-react";

import { MarketingShell } from "@/components/marketing-shell";
import { Card } from "@/components/ui/card";

export default function ProductPage() {
  return (
    <MarketingShell
      eyebrow="Product"
      title="A full-stack intelligence operating system, not just a lead list."
      description="AtlasBI is built to discover companies, enrich them, model relationships, rank opportunities, and make the result searchable for customer teams while keeping ingestion and operations in a separate superadmin layer."
    >
      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <h2 className="font-display text-3xl text-white">Client Product Surface</h2>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {[
              { label: "AI Search", Icon: Search },
              { label: "Company Explorer", Icon: Globe2 },
              { label: "Saved Leads", Icon: BarChart3 },
              { label: "Alerts and Insights", Icon: Radar }
            ].map(({ label, Icon }) => (
              <div key={label} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                <Icon className="h-5 w-5 text-accent" />
                <p className="mt-4 text-white">{label}</p>
              </div>
            ))}
          </div>
          <p className="mt-5 text-sm leading-7 text-slate-400">
            Customers get a clean revenue-facing workspace that lets them search the dataset, inspect intelligence profiles, monitor market signals, and export action-ready leads according to their package.
          </p>
        </Card>

        <Card>
          <h2 className="font-display text-3xl text-white">Superadmin Product Surface</h2>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {[
              { label: "Client Management", Icon: ShieldCheck },
              { label: "Account Oversight", Icon: BrainCircuit },
              { label: "Crawler Operations", Icon: Telescope },
              { label: "Platform Statistics", Icon: Network }
            ].map(({ label, Icon }) => (
              <div key={label} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                <Icon className="h-5 w-5 text-accent" />
                <p className="mt-4 text-white">{label}</p>
              </div>
            ))}
          </div>
          <p className="mt-5 text-sm leading-7 text-slate-400">
            Superadmins manage the company itself: clients, organizations, accounts, crawler jobs, dataset growth, geographies, seed ingestion, logs, and platform-wide analytics.
          </p>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        {[
          ["Discovery Engine", "Search-led discovery, website extraction, related-company expansion, and location-based crawl grids."],
          ["Intelligence Engine", "Enrichment, signals, scoring, buyer intent, opportunities, and knowledge graph relationships."],
          ["Delivery Engine", "Natural-language search, exports, alerts, workspace access, and machine APIs."]
        ].map(([title, body]) => (
          <Card key={title}>
            <h3 className="font-display text-2xl text-white">{title}</h3>
            <p className="mt-3 text-sm leading-7 text-slate-400">{body}</p>
          </Card>
        ))}
      </div>
    </MarketingShell>
  );
}
