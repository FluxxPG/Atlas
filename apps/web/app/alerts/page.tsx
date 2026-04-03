import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { getAlerts } from "@/lib/data";

export default async function AlertsPage() {
  const alerts = await getAlerts();

  return (
    <AppShell eyebrow="Alerts Center" title="Signals and opportunities in motion" feature="alerts">
      <div className="grid gap-4">
        {alerts.items.map((item: any) => (
          <Card key={item.id}>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-accent">{item.category}</p>
                <h3 className="mt-2 font-display text-2xl text-white">{item.title}</h3>
                <p className="mt-2 text-sm text-slate-400">{item.description}</p>
              </div>
              <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white">
                {item.severity}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </AppShell>
  );
}
