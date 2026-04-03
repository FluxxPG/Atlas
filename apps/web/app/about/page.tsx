import { MarketingShell } from "@/components/marketing-shell";
import { Card } from "@/components/ui/card";

export default function AboutPage() {
  return (
    <MarketingShell
      eyebrow="About"
      title="Built for serious intelligence operations."
      description="AtlasBI is designed as a production-grade SaaS platform for discovering companies globally, building intelligence profiles, detecting opportunities, and delivering AI-native market search to customer teams."
    >
      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <h2 className="font-display text-3xl text-white">What makes AtlasBI different</h2>
          <div className="mt-5 space-y-4 text-sm leading-7 text-slate-400">
            <p>It combines crawling, enrichment, scoring, graph relationships, vector-ready search, and SaaS governance in one architecture.</p>
            <p>It does not mix internal operator controls with customer dashboards.</p>
            <p>It is built so the company operating the platform can manage clients, accounts, billing posture, and dataset growth from a separate superadmin environment.</p>
          </div>
        </Card>
        <Card>
          <h2 className="font-display text-3xl text-white">Who it is for</h2>
          <div className="mt-5 space-y-3">
            {[
              "Revenue and outbound teams",
              "Market research and strategy teams",
              "Agencies and operators finding whitespace",
              "Internal admins managing multi-client intelligence operations"
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
                {item}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </MarketingShell>
  );
}
