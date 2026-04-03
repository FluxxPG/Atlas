import { ArrowRight, Network, Orbit, Radar, Rows3 } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { MetricCard } from "@/components/metric-card";
import { MotionIn } from "@/components/motion-in";
import { OrbScene } from "@/components/orb-scene";
import { RealtimeFeed } from "@/components/realtime-feed";
import { SearchConsole } from "@/components/search-console";
import { Card } from "@/components/ui/card";
import { getDashboardData } from "@/lib/data";

export default async function DashboardPage() {
  const dashboard = await getDashboardData();

  return (
    <AppShell eyebrow="Client Dashboard" title="Intelligence that compounds itself" feature="dashboard">
      <MotionIn>
        <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
          <section className="glass relative min-h-[360px] overflow-hidden rounded-[34px] p-8">
            <OrbScene />
            <div className="relative z-10 max-w-2xl">
              <p className="text-xs uppercase tracking-[0.35em] text-accent">Autonomous Growth Engine</p>
              <h3 className="mt-4 font-display text-5xl font-semibold leading-tight text-white">
                Discover, enrich, rank, and convert business opportunities in every market.
              </h3>
              <p className="mt-5 max-w-xl text-base text-slate-300">
                AtlasBI continuously maps companies, surfaces AI-ranked opportunities, and lets customer teams search the intelligence graph without exposing crawler controls.
              </p>
              <div className="mt-8 grid gap-3 text-sm text-slate-200 md:grid-cols-3">
                <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <Network className="mb-3 h-5 w-5 text-accent" />
                  Knowledge graph over companies, industries, and technologies
                </div>
                <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <Radar className="mb-3 h-5 w-5 text-accent" />
                  Intent detection from hiring, expansion, and tech adoption
                </div>
                <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <Orbit className="mb-3 h-5 w-5 text-accent" />
                  Search, saved leads, exports, and alerts aligned to package access
                </div>
              </div>
            </div>
          </section>
          <RealtimeFeed />
        </div>
      </MotionIn>

      <MotionIn delay={0.08}>
        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {dashboard.metrics.map((item: any) => (
            <MetricCard key={item.label} {...item} />
          ))}
        </div>
      </MotionIn>

      <MotionIn delay={0.16}>
        <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <SearchConsole />
          <Card>
            <div className="mb-5 flex items-center justify-between">
              <h3 className="font-display text-2xl text-white">Market Pulse</h3>
              <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-slate-400">Live aggregation</span>
            </div>
            <div className="space-y-3">
              {dashboard.heatmap.map((city: any) => (
                <div key={city.city} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center justify-between">
                    <p className="text-white">{city.city}</p>
                    <p className="text-sm text-accent">{city.score}</p>
                  </div>
                  <div className="mt-3 h-2 rounded-full bg-white/5">
                    <div className="h-full rounded-full bg-gradient-to-r from-glow to-accent" style={{ width: `${city.score}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </MotionIn>

      <MotionIn delay={0.24}>
        <div className="mt-6 grid gap-6 xl:grid-cols-2">
          <Card>
            <div className="mb-5 flex items-center gap-2 text-white">
              <Rows3 className="h-4 w-4 text-accent" />
              Top Opportunity Lanes
            </div>
            <div className="space-y-3">
              {[
                ["CRM modernization", "486 whitespace accounts", "82% median confidence"],
                ["Review recovery", "223 consumer brands", "74% median confidence"],
                ["Operations automation", "221 hiring-led teams", "79% median confidence"]
              ].map(([title, subtitle, meta]) => (
                <div key={title} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-white">{title}</p>
                      <p className="mt-1 text-sm text-slate-400">{subtitle}</p>
                    </div>
                    <span className="inline-flex items-center gap-1 text-sm text-accent">
                      {meta}
                      <ArrowRight className="h-4 w-4" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <div className="mb-5 flex items-center gap-2 text-white">
              <Network className="h-4 w-4 text-accent" />
              Relationship Graph Focus
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {dashboard.market_map.map((cluster: any) => (
                <div key={cluster.label} className="rounded-2xl border border-white/10 bg-white/5 p-5">
                  <p className="text-sm text-slate-400">{cluster.label}</p>
                  <p className="mt-3 font-display text-3xl text-white">{cluster.value}%</p>
                  <p className="mt-2 text-sm text-slate-400">
                    Cross-linked by technology overlap, regional expansion, and market demand.
                  </p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </MotionIn>
    </AppShell>
  );
}
