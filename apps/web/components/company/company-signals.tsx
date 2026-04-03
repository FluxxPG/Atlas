import { AlertTriangle, BriefcaseBusiness, Workflow } from "lucide-react";

import { Card } from "@/components/ui/card";

const iconMap: Record<string, typeof AlertTriangle> = {
  low_rating: AlertTriangle,
  hiring_activity: BriefcaseBusiness,
  rapid_growth: Workflow,
  no_website: AlertTriangle
};

export function CompanySignals({ title, items }: { title: string; items: any[] }) {
  return (
    <Card>
      <h2 className="font-display text-2xl text-white">{title}</h2>
      <div className="mt-5 space-y-3">
        {items.length ? (
          items.map((item) => {
            const Icon = iconMap[item.type] ?? AlertTriangle;
            return (
              <div key={item.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3">
                  <Icon className="h-4 w-4 text-accent" />
                  <div>
                    <p className="text-white">{item.title}</p>
                    <p className="mt-1 text-sm text-slate-400">{item.description}</p>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div className="rounded-2xl bg-white/5 p-4 text-sm text-slate-400">No entries yet.</div>
        )}
      </div>
    </Card>
  );
}

