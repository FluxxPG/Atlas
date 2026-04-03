import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { getExportPreview } from "@/lib/data";

export default async function ExportsPage() {
  const [csv, json] = await Promise.all([getExportPreview("csv"), getExportPreview("json")]);

  return (
    <AppShell eyebrow="Exports" title="CSV, Excel, and JSON delivery" feature="exports">
      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <h3 className="font-display text-2xl text-white">CSV Preview</h3>
          <pre className="mt-5 overflow-auto rounded-2xl bg-slate-950/50 p-4 text-xs text-slate-300">{csv}</pre>
        </Card>
        <Card>
          <h3 className="font-display text-2xl text-white">JSON Preview</h3>
          <pre className="mt-5 overflow-auto rounded-2xl bg-slate-950/50 p-4 text-xs text-slate-300">{json}</pre>
        </Card>
      </div>
    </AppShell>
  );
}
