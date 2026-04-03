import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { getAdminData } from "@/lib/data";

export default async function SuperadminLogsPage() {
  const admin = await getAdminData();

  return (
    <AppShell eyebrow="Superadmin Logs" title="Platform logs and operational history" mode="superadmin">
      <div className="grid gap-4">
        {admin.logs.length ? (
          admin.logs.map((log: any) => (
            <Card key={log.id}>
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-accent">{log.level}</p>
                  <h3 className="mt-3 font-display text-2xl text-white">{log.message}</h3>
                  <p className="mt-2 text-sm text-slate-400">{log.source}</p>
                </div>
                <p className="text-sm text-slate-500">{new Date(log.created_at).toLocaleString()}</p>
              </div>
            </Card>
          ))
        ) : (
          <Card>
            <p className="text-white">No logs are available yet.</p>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
