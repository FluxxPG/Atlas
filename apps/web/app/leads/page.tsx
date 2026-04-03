import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { getSavedLeads } from "@/lib/data";

export default async function LeadsPage() {
  const leads = await getSavedLeads();

  return (
    <AppShell eyebrow="Saved Leads" title="Curated opportunity pipeline" feature="leads">
      <div className="grid gap-4">
        {leads.items.map((lead: any) => (
          <Card key={lead.id}>
            <p className="text-xs uppercase tracking-[0.24em] text-accent">Lead saved</p>
            <h3 className="mt-3 font-display text-2xl text-white">{lead.company_id}</h3>
            <p className="mt-2 text-sm text-slate-400">{lead.notes ?? "No notes yet."}</p>
            <p className="mt-4 text-xs text-slate-500">{lead.created_at}</p>
          </Card>
        ))}
      </div>
    </AppShell>
  );
}
