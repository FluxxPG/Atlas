import { revokeApiKeyAction } from "@/app/actions";
import { Code2, KeyRound, ShieldCheck, Users, Wallet } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { WorkspaceApiKeyForm } from "@/components/forms/workspace-api-key-form";
import { WorkspaceOrganizationForm } from "@/components/forms/workspace-organization-form";
import { Card } from "@/components/ui/card";
import { getWorkspaceData } from "@/lib/data";

export default async function WorkspacePage() {
  const workspace = await getWorkspaceData();
  const organization = workspace.default_organization;
  const subscription = workspace.subscription;
  const workspaceMetrics = [
    { label: "Plan", value: organization?.plan ?? "growth", Icon: Wallet },
    { label: "Status", value: organization?.status ?? "active", Icon: ShieldCheck },
    { label: "Members", value: String(organization?.member_count ?? 0), Icon: Users },
    { label: "API keys", value: String(workspace.usage.api_keys), Icon: KeyRound }
  ];

  return (
    <AppShell eyebrow="Enterprise Workspace" title={organization?.name ?? "Workspace"} feature="workspace">
      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Workspace Profile</p>
          <h3 className="mt-3 font-display text-3xl text-white">{organization?.name}</h3>
          <p className="mt-3 text-sm text-slate-400">
            Multi-tenant operating layer for memberships, subscription limits, API access, and audit visibility.
          </p>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {workspaceMetrics.map(({ label, value, Icon }) => (
              <div key={label} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                <Icon className="h-5 w-5 text-accent" />
                <p className="mt-4 text-sm text-slate-400">{label}</p>
                <p className="mt-2 font-display text-2xl text-white">{value}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Subscription Usage</p>
          <div className="mt-5 space-y-4">
            {[
              ["Searches", workspace.usage.searches, subscription?.search_quota ?? 0],
              ["Exports", workspace.usage.exports, subscription?.export_quota ?? 0],
              ["Crawls", workspace.usage.crawls, subscription?.crawl_quota ?? 0]
            ].map(([label, used, quota]) => {
              const percent = quota ? Math.min(100, Math.round((Number(used) / Number(quota)) * 100)) : 0;
              return (
                <div key={String(label)} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-slate-300">{label}</p>
                    <p className="text-sm text-white">{used} / {quota}</p>
                  </div>
                  <div className="mt-3 h-2 rounded-full bg-black/20">
                    <div className="h-full rounded-full bg-gradient-to-r from-glow to-accent" style={{ width: `${percent}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">API Keys</p>
          <p className="mt-3 text-sm text-slate-400">
            Create scoped machine credentials for search, exports, and company intelligence retrieval.
          </p>
          <div className="mt-5">
            <WorkspaceApiKeyForm organizationId={organization?.id ?? "org-1"} />
          </div>
          <div className="mt-5 space-y-3">
            {workspace.api_keys.map((item: any) => (
              <div key={item.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between">
                  <p className="text-white">{item.name}</p>
                  <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{item.key_prefix}</span>
                </div>
                <p className="mt-2 text-sm text-slate-400">{item.scopes.join(" / ")}</p>
                <div className="mt-4 flex items-center justify-between gap-4 text-xs text-slate-500">
                  <span>{item.last_used_at ? `Last used ${new Date(item.last_used_at).toLocaleString()}` : "Never used yet"}</span>
                  {item.revoked_at ? (
                    <span className="text-rose-300">Revoked</span>
                  ) : (
                    <form action={revokeApiKeyAction}>
                      <input type="hidden" name="organization_id" value={organization?.id ?? "org-1"} />
                      <input type="hidden" name="api_key_id" value={item.id} />
                      <button type="submit" className="text-accent transition hover:text-white">Revoke key</button>
                    </form>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Audit Trail</p>
          <div className="mt-5 space-y-3">
            {workspace.audit_events.map((item: any) => (
              <div key={item.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between">
                  <p className="text-white">{item.action}</p>
                  <span className="text-xs text-slate-500">{new Date(item.created_at).toLocaleString()}</span>
                </div>
                <p className="mt-2 text-sm text-slate-400">{item.resource_type} / {item.resource_id}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <div className="flex items-center gap-3">
            <Code2 className="h-5 w-5 text-accent" />
            <p className="text-xs uppercase tracking-[0.3em] text-accent">Machine Access</p>
          </div>
          <p className="mt-4 text-sm text-slate-400">
            Scoped API keys can search, retrieve company intelligence, and trigger exports from secure backend systems.
          </p>
          <pre className="mt-4 overflow-x-auto rounded-3xl border border-white/10 bg-black/30 p-4 text-sm text-slate-200">
{`curl -H "Authorization: Bearer atlas_live_key" \\
  "${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1"}/machine/search?q=fast%20growing%20startups"`}
          </pre>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Organization Expansion</p>
          <div className="mt-4 grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
            <div>
              <h3 className="font-display text-2xl text-white">Create another workspace</h3>
              <p className="mt-3 text-sm text-slate-400">
                Provision a second operating workspace for another business unit, geo, or customer pod.
              </p>
              <div className="mt-5">
                <WorkspaceOrganizationForm />
              </div>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
              <p className="text-white">Current memberships</p>
              <div className="mt-4 space-y-3">
                {workspace.memberships.map((item: any) => (
                  <div key={item.id} className="rounded-3xl border border-white/10 bg-black/20 p-4">
                    <div className="flex items-center justify-between">
                      <p className="text-white">{item.organization.name}</p>
                      <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">
                        {item.is_default ? "default" : item.role}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-slate-400">
                      {item.organization.slug} / {item.organization.plan} / {item.organization.status}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
