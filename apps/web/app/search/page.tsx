import { AppShell } from "@/components/app-shell";
import { SearchResults } from "@/components/search/search-results";
import { SearchConsole } from "@/components/search-console";
import { Card } from "@/components/ui/card";
import { getSearchResults } from "@/lib/data";

export default async function SearchPage({
  searchParams
}: {
  searchParams?: {
    q?: string;
    country?: string;
    industry?: string;
    sort_by?: "opportunity" | "growth";
  };
}) {
  const q = searchParams?.q ?? "companies needing CRM";
  const data = await getSearchResults({
    q,
    country: searchParams?.country,
    industry: searchParams?.industry,
    sortBy: searchParams?.sort_by ?? "opportunity"
  });

  return (
    <AppShell eyebrow="Vector Search" title="Natural-language intelligence retrieval" feature="search">
      <SearchConsole initialQuery={q} />
      <div className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <SearchResults data={data} />
        <Card>
          <h3 className="font-display text-2xl text-white">Query Guide</h3>
          <div className="mt-5 space-y-3 text-sm text-slate-300">
            <p>Use prompts like "restaurants with bad reviews in Mumbai" or "SaaS companies hiring ops managers in India".</p>
            <p>Advanced API route: `/api/v1/search/advanced?q=...&country=India&sort_by=growth`.</p>
            <p>Current query: <span className="text-accent">{q}</span></p>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-white">Live retrieval status</p>
              <p className="mt-2 text-slate-400">
                {data.total
                  ? `Found ${data.total} accounts with current filters and ranking.`
                  : "No live matches yet. Broaden the prompt or remove restrictive filters."}
              </p>
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
