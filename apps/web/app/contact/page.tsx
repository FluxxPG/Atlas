import Link from "next/link";

import { MarketingShell } from "@/components/marketing-shell";
import { Card } from "@/components/ui/card";

export default function ContactPage() {
  return (
    <MarketingShell
      eyebrow="Contact"
      title="Talk to the team behind the intelligence platform."
      description="Use AtlasBI for customer intelligence workflows or operate it internally with a segregated superadmin console for clients, accounts, and crawler infrastructure."
    >
      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <h2 className="font-display text-3xl text-white">Contact channels</h2>
          <div className="mt-5 space-y-3">
            {[
              ["Sales", "sales@atlasbi.local"],
              ["Support", "support@atlasbi.local"],
              ["Operations", "ops@atlasbi.local"]
            ].map(([label, value]) => (
              <div key={label} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                <p className="text-sm uppercase tracking-[0.24em] text-accent">{label}</p>
                <p className="mt-2 text-white">{value}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <h2 className="font-display text-3xl text-white">Typical conversation</h2>
          <div className="mt-5 space-y-4 text-sm leading-7 text-slate-400">
            <p>We help teams decide which package fits their search, export, and governance needs.</p>
            <p>We also help internal platform operators understand the superadmin operating model for client management, account control, and crawl infrastructure.</p>
            <p>Existing customers can proceed directly to their workspace.</p>
          </div>
          <Link href="/login" className="mt-6 inline-flex text-sm text-accent transition hover:text-white">
            Login
          </Link>
        </Card>
      </div>
    </MarketingShell>
  );
}
