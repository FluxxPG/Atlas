import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import { Card } from "@/components/ui/card";

export function SearchResults({ data }: { data: any }) {
  const appliedFilters = Object.entries(data.applied_filters ?? {}).filter(([, value]) => value !== null && value !== undefined && value !== "");
  const bestOpportunity = data.results.reduce((max: number, item: any) => Math.max(max, Number(item.opportunity_score || 0)), 0);
  const websiteGapCount = data.results.filter((item: any) => !item.website).length;

  return (
    <div className="space-y-4">
      <Card>
        <div className="grid gap-4 xl:grid-cols-[0.9fr_1.1fr]">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-accent">Search Summary</p>
            <h3 className="mt-3 font-display text-2xl text-white">{data.total} matched accounts</h3>
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              <div className="rounded-2xl bg-black/20 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Best opportunity</p>
                <p className="mt-2 text-xl text-white">{bestOpportunity.toFixed(1)}</p>
              </div>
              <div className="rounded-2xl bg-black/20 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">No-website leads</p>
                <p className="mt-2 text-xl text-white">{websiteGapCount}</p>
              </div>
              <div className="rounded-2xl bg-black/20 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Suggested plays</p>
                <p className="mt-2 text-xl text-white">{data.suggested_filters.length || 0}</p>
              </div>
            </div>
          </div>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-slate-400">Applied filters</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {appliedFilters.length ? (
                  appliedFilters.map(([key, value]) => (
                    <span key={key} className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white">
                      {key.replaceAll("_", " ")}: {String(value)}
                    </span>
                  ))
                ) : (
                  <span className="text-sm text-slate-500">No explicit filters applied.</span>
                )}
              </div>
            </div>
            <div>
              <p className="text-sm text-slate-400">Suggested filters</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {data.suggested_filters.length ? (
                  data.suggested_filters.map((filter: string) => (
                    <span key={filter} className="rounded-full bg-accent/10 px-3 py-1.5 text-xs text-accent">
                      {filter}
                    </span>
                  ))
                ) : (
                  <span className="text-sm text-slate-500">No suggested filters.</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </Card>
      {data.results.length ? (
        data.results.map((item: any) => {
          const leadSegments = item.enrichment?.lead_segments ?? [];
          const categories = item.enrichment?.categories ?? [];
          const directorySources = item.enrichment?.directory_sources ?? [];
          return (
            <Card key={item.id}>
              <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-accent/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-accent">
                      {item.industry ?? "Unknown industry"}
                    </span>
                    {!item.website ? (
                      <span className="rounded-full bg-amber-500/10 px-3 py-1 text-xs text-amber-200">Website gap</span>
                    ) : null}
                    {(item.enrichment?.has_social_presence === false) ? (
                      <span className="rounded-full bg-rose-500/10 px-3 py-1 text-xs text-rose-200">Weak social presence</span>
                    ) : null}
                  </div>
                  <h3 className="mt-3 font-display text-2xl text-white">{item.name}</h3>
                  <p className="mt-2 text-sm text-slate-400">{[item.city, item.country].filter(Boolean).join(", ")}</p>

                  <div className="mt-4 grid gap-3 md:grid-cols-3">
                    <div className="rounded-2xl bg-black/20 p-3 text-sm text-slate-300">
                      <p className="text-slate-500">Health</p>
                      <p className="mt-1 text-white">{Number(item.health_score || 0).toFixed(1)}</p>
                    </div>
                    <div className="rounded-2xl bg-black/20 p-3 text-sm text-slate-300">
                      <p className="text-slate-500">Growth</p>
                      <p className="mt-1 text-white">{Number(item.growth_score || 0).toFixed(1)}</p>
                    </div>
                    <div className="rounded-2xl bg-black/20 p-3 text-sm text-slate-300">
                      <p className="text-slate-500">Opportunity</p>
                      <p className="mt-1 text-white">{Number(item.opportunity_score || 0).toFixed(1)}</p>
                    </div>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-300">
                    {leadSegments.map((segment: string) => (
                      <span key={`${item.id}-${segment}`} className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
                        {segment.replaceAll("_", " ")}
                      </span>
                    ))}
                    {categories.slice(0, 4).map((category: string) => (
                      <span key={`${item.id}-${category}`} className="rounded-full bg-black/20 px-3 py-1 text-slate-400">
                        {category}
                      </span>
                    ))}
                  </div>

                  <div className="mt-4 grid gap-3 md:grid-cols-2">
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
                      <p className="text-slate-500">Lead rationale</p>
                      <p className="mt-2 text-white">
                        {!item.website
                          ? "No website detected, which makes this a strong website and digital presence prospect."
                          : item.enrichment?.has_social_presence === false
                            ? "Website exists but social presence is weak, making this a strong marketing and reputation prospect."
                            : "Digital footprint and enrichment signals suggest a workflow, CRM, or optimization opportunity."}
                      </p>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
                      <p className="text-slate-500">Source coverage</p>
                      <p className="mt-2 text-white">
                        {directorySources.length ? directorySources.join(", ") : "No directory sources attached yet"}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex w-full flex-col gap-3 md:w-auto">
                  <Link
                    href={`/company/${item.slug}`}
                    className="inline-flex items-center justify-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10"
                  >
                    Open profile
                    <ArrowUpRight className="h-4 w-4 text-accent" />
                  </Link>
                  {item.website ? (
                    <a
                      href={item.website}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center justify-center rounded-full border border-white/10 bg-black/20 px-4 py-2 text-sm text-slate-300 transition hover:text-white"
                    >
                      Visit website
                    </a>
                  ) : null}
                </div>
              </div>
            </Card>
          );
        })
      ) : (
        <Card>
          <p className="text-lg text-white">No companies matched this search yet.</p>
          <p className="mt-2 text-sm text-slate-400">
            Try a broader prompt, remove filters, or search by city, category, or need state like CRM, SEO, or website.
          </p>
        </Card>
      )}
    </div>
  );
}
