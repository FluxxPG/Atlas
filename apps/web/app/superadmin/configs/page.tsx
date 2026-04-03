import { AppShell } from "@/components/app-shell";
import { SuperadminConfigForm } from "@/components/forms/superadmin-forms";
import { Card } from "@/components/ui/card";
import { getAdminData } from "@/lib/data";

export default async function SuperadminConfigsPage() {
  const admin = await getAdminData();

  return (
    <AppShell eyebrow="Superadmin Configs" title="Platform runtime configuration" mode="superadmin">
      <Card>
        <p className="text-xs uppercase tracking-[0.3em] text-accent">Editable Runtime Settings</p>
        <h3 className="mt-3 font-display text-3xl text-white">Tune platform behavior from the operations console</h3>
        <div className="mt-5">
          <SuperadminConfigForm configs={admin.configs} />
        </div>
      </Card>
    </AppShell>
  );
}
