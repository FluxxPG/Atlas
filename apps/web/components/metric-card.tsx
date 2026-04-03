import { ArrowUpRight } from "lucide-react";

import { Card } from "@/components/ui/card";

export function MetricCard({
  label,
  value,
  delta,
  meta
}: {
  label: string;
  value: string | number;
  delta?: number | null;
  meta?: Record<string, unknown>;
}) {
  return (
    <Card className="relative overflow-hidden">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-accent/70 to-transparent" />
      <p className="text-sm text-slate-300">{label}</p>
      <div className="mt-4 flex items-end justify-between gap-4">
        <h3 className="font-display text-3xl font-semibold tracking-tight text-white">{value}</h3>
        {typeof delta === "number" ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-400/10 px-3 py-1 text-xs text-emerald-300">
            <ArrowUpRight className="h-3.5 w-3.5" />
            {delta}%
          </span>
        ) : null}
      </div>
      {meta ? <p className="mt-3 text-xs text-slate-400">{JSON.stringify(meta)}</p> : null}
    </Card>
  );
}

