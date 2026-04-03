import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { getCompaniesFiltered } from "@/lib/data";

export default async function CompanyPage() {
  const companies = await getCompaniesFiltered({ limit: 12 });

  return (
    <AppShell eyebrow="Company Explorer" title="Deep intelligence profiles" feature="company">
      <div className="grid gap-4 xl:grid-cols-2">
        {companies.items.length ? (
          companies.items.map((company: any) => (
            <Card key={company.id}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-accent">{company.industry ?? "Unknown industry"}</p>
                  <h3 className="mt-3 font-display text-2xl text-white">{company.name}</h3>
                  <p className="mt-2 text-sm text-slate-400">
                    {[company.city, company.country].filter(Boolean).join(", ")}
                  </p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-right">
                  <p className="text-xs text-slate-400">Opportunity</p>
                  <p className="font-display text-3xl text-white">{company.opportunity_score}</p>
                </div>
              </div>
              <div className="mt-6 grid gap-3 md:grid-cols-3">
                <div className="rounded-2xl bg-white/5 p-4 text-sm text-slate-300">Health {company.health_score}</div>
                <div className="rounded-2xl bg-white/5 p-4 text-sm text-slate-300">Growth {company.growth_score}</div>
                <div className="rounded-2xl bg-white/5 p-4 text-sm text-slate-300">
                  {company.website ?? "No website"}
                </div>
              </div>
              <Link
                href={`/company/${company.slug}`}
                className="mt-5 inline-flex rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10"
              >
                Open intelligence profile
              </Link>
            </Card>
          ))
        ) : (
          <Card className="xl:col-span-2">
            <h3 className="font-display text-2xl text-white">Awaiting crawled company records</h3>
            <p className="mt-3 max-w-2xl text-sm text-slate-400">
              Once the crawl and enrichment jobs run, this explorer surfaces profile cards, signals, opportunities, and knowledge graph links.
            </p>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
