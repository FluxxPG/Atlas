import Link from "next/link";
import { ChevronLeft, Download, Star } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { CompanyOverview } from "@/components/company/company-overview";
import { CompanySignals } from "@/components/company/company-signals";
import { Card } from "@/components/ui/card";
import { getCompanyBySlug } from "@/lib/data";

export default async function CompanyDetailPage({
  params
}: {
  params: { slug: string };
}) {
  const company: any = await getCompanyBySlug(params.slug);

  return (
    <AppShell eyebrow="Company Intelligence" title={company?.name ?? "Company not found"} feature="company">
      <Link href="/company" className="mb-6 inline-flex items-center gap-2 text-sm text-slate-300 hover:text-white">
        <ChevronLeft className="h-4 w-4" />
        Back to explorer
      </Link>

      {company ? (
        <>
          <CompanyOverview company={company} />
          <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_1fr]">
            <CompanySignals title="Detected Signals" items={company.signals} />
            <CompanySignals title="Generated Opportunities" items={company.opportunities.map((item: any) => ({ ...item, type: item.category }))} />
          </div>
          <div className="mt-6 grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
            <Card>
              <div className="flex items-center gap-2 text-white">
                <Star className="h-4 w-4 text-accent" />
                Relationship Graph Edges
              </div>
              <div className="mt-5 space-y-3">
                {company.relationships.length ? (
                  company.relationships.map((item: any) => (
                    <div key={item.id} className="rounded-2xl bg-white/5 p-4">
                      <p className="text-white">{item.relationship_type}</p>
                      <p className="mt-1 text-sm text-slate-400">{JSON.stringify(item.metadata)}</p>
                    </div>
                  ))
                ) : (
                  <div className="rounded-2xl bg-white/5 p-4 text-sm text-slate-400">Graph edges will appear after more crawl passes.</div>
                )}
              </div>
            </Card>
            <Card>
              <div className="flex items-center justify-between">
                <h2 className="font-display text-2xl text-white">Lead Actions</h2>
                <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">Action-ready</span>
              </div>
              <div className="mt-5 space-y-4 text-sm text-slate-300">
                <p>Use this profile to save the account, export intelligence, or trigger a deeper recrawl from the admin queue.</p>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-white">Export endpoints</p>
                  <p className="mt-2 break-all text-slate-400"><code>/api/v1/exports/csv/preview</code> and <code>/api/v1/exports/json/preview</code></p>
                </div>
                <button className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-glow to-accent px-4 py-2 font-medium text-ink">
                  <Download className="h-4 w-4" />
                  Queue export
                </button>
              </div>
            </Card>
          </div>
          <div className="mt-6">
            <Card>
              <div className="flex items-center gap-2 text-white">
                <Star className="h-4 w-4 text-accent" />
                Source Provenance
              </div>
              <div className="mt-5 grid gap-3 md:grid-cols-2">
                {company.sources?.length ? (
                  company.sources.map((item: any) => (
                    <div key={item.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                      <div className="flex items-center justify-between">
                        <p className="text-white">{item.source_type}</p>
                        <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">
                          {Math.round(Number(item.confidence) * 100)}%
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-slate-400">{item.source_key}</p>
                      {item.source_url ? (
                        <a href={item.source_url} target="_blank" rel="noreferrer" className="mt-2 inline-flex text-xs text-accent hover:text-white">
                          Open source record
                        </a>
                      ) : null}
                    </div>
                  ))
                ) : (
                  <div className="rounded-2xl bg-white/5 p-4 text-sm text-slate-400">
                    Source provenance will appear once vendor enrichment or discovery expansion records are attached.
                  </div>
                )}
              </div>
            </Card>
          </div>
        </>
      ) : (
        <Card>
          <p className="text-white">This company profile is not available yet.</p>
        </Card>
      )}
    </AppShell>
  );
}
