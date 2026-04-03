import { Globe, LineChart, Link2, MapPin, Sparkles } from "lucide-react";

import { Card } from "@/components/ui/card";

export function CompanyOverview({ company }: { company: any }) {
  const enrichmentEntries = Object.entries(company.enrichment ?? {}).filter(([, value]) => {
    if (Array.isArray(value)) {
      return value.length > 0;
    }

    return value !== null && value !== undefined && value !== "";
  });

  return (
    <div className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
      <Card className="relative overflow-hidden">
        <div className="absolute inset-0 bg-aurora opacity-60" />
        <div className="relative">
          <p className="text-xs uppercase tracking-[0.3em] text-accent">{company.industry ?? "Company"}</p>
          <h1 className="mt-3 font-display text-4xl text-white">{company.name}</h1>
          <div className="mt-4 flex flex-wrap gap-3 text-sm text-slate-300">
            <span className="inline-flex items-center gap-2"><MapPin className="h-4 w-4 text-accent" />{[company.city, company.country].filter(Boolean).join(", ")}</span>
            <span className="inline-flex items-center gap-2"><Globe className="h-4 w-4 text-accent" />{company.website ?? "Website not detected"}</span>
            <span className="inline-flex items-center gap-2"><Link2 className="h-4 w-4 text-accent" />Slug {company.slug}</span>
          </div>
          <p className="mt-6 max-w-3xl text-sm leading-7 text-slate-300">
            {company.ai_summary ?? company.description ?? "AI summary will appear here as crawl enrichment completes."}
          </p>
        </div>
      </Card>

      <Card>
        <div className="mb-5 flex items-center gap-2 text-white">
          <LineChart className="h-4 w-4 text-accent" />
          Scoring Stack
        </div>
        <div className="space-y-3">
          {[
            ["Health", company.health_score],
            ["Growth", company.growth_score],
            ["Opportunity", company.opportunity_score]
          ].map(([label, score]) => (
            <div key={label} className="rounded-2xl bg-white/5 p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm text-slate-400">{label}</p>
                <p className="font-display text-2xl text-white">{String(score)}</p>
              </div>
              <div className="mt-3 h-2 rounded-full bg-white/5">
                <div className="h-full rounded-full bg-gradient-to-r from-glow to-accent" style={{ width: `${Number(score)}%` }} />
              </div>
            </div>
          ))}
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
            <span className="inline-flex items-center gap-2 text-accent"><Sparkles className="h-4 w-4" />Enrichment fields</span>
            <div className="mt-3 space-y-3">
              {enrichmentEntries.map(([key, value]) => (
                <div key={key} className="rounded-2xl border border-white/10 bg-black/10 p-3">
                  <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">
                    {key.replaceAll("_", " ")}
                  </p>
                  {Array.isArray(value) ? (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {value.map((item) => (
                        <span key={`${key}-${item}`} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200">
                          {String(item)}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="mt-2 text-sm text-slate-200">{String(value)}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
