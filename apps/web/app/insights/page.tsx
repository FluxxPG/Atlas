import { AppShell } from "@/components/app-shell";
import { MetricCard } from "@/components/metric-card";
import { Card } from "@/components/ui/card";
import { getInsightsData } from "@/lib/data";

export default async function InsightsPage() {
  const insights = await getInsightsData();

  return (
    <AppShell eyebrow="Market Intelligence" title="Trend maps and sector signals" feature="insights">
      <div className="grid gap-4 md:grid-cols-3">
        {insights.trend_cards.map((item: any) => (
          <MetricCard key={item.label} {...item} />
        ))}
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <Card>
          <h3 className="font-display text-2xl text-white">Industry Trends</h3>
          <div className="mt-5 space-y-3">
            {insights.industry_trends.map((item: any) => (
              <div key={item.industry} className="rounded-2xl bg-white/5 p-4">
                <p className="text-white">{item.industry}</p>
                <p className="mt-1 text-sm text-slate-400">Growth {item.growth} / Opportunity {item.opportunity}</p>
              </div>
            ))}
          </div>
        </Card>
        <Card>
          <h3 className="font-display text-2xl text-white">City Heatmap</h3>
          <div className="mt-5 space-y-3">
            {insights.city_heatmap.map((item: any) => (
              <div key={item.city} className="rounded-2xl bg-white/5 p-4">
                <p className="text-white">{item.city}</p>
                <div className="mt-3 h-2 rounded-full bg-white/5">
                  <div className="h-full rounded-full bg-gradient-to-r from-warm to-accent" style={{ width: `${item.density}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
        <Card>
          <h3 className="font-display text-2xl text-white">Tech Adoption</h3>
          <div className="mt-5 space-y-3">
            {insights.tech_adoption.map((item: any) => (
              <div key={item.technology} className="rounded-2xl bg-white/5 p-4">
                <p className="text-white">{item.technology}</p>
                <p className="mt-1 text-sm text-slate-400">Adoption index {item.adoption}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
