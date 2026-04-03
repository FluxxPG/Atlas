import { rebuildEmbeddingsAction, rebuildInsightsAction, queueIndiaSeedAction } from "@/app/actions";
import { AppShell } from "@/components/app-shell";
import {
  SuperadminConfigForm,
  SuperadminCrawlerPresetActions,
  SuperadminCrawlerPresetForm
} from "@/components/forms/superadmin-forms";
import { AdminDiscoveryForm, AdminGeoGridForm } from "@/components/forms/admin-forms";
import { MetricCard } from "@/components/metric-card";
import { Card } from "@/components/ui/card";
import { getAdminConnectorDetail, getAdminConnectors, getAdminCrawlerPresets, getAdminData } from "@/lib/data";

export default async function SuperadminCrawlersPage() {
  const [admin, presets, connectors] = await Promise.all([getAdminData(), getAdminCrawlerPresets(), getAdminConnectors()]);
  const connectorDetails = await Promise.all(
    connectors.items.map((connector: any) => getAdminConnectorDetail(connector.provider))
  );

  return (
    <AppShell eyebrow="Superadmin Crawlers" title="Crawler operations and dataset seeding" mode="superadmin">
      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard label="Queue depth" value={admin.queue_depth} meta={{ queue: "crawl:jobs" }} />
        <MetricCard label="Active jobs" value={admin.active_jobs} meta={{ status: "running" }} />
        <MetricCard label="Dataset size" value={admin.dataset_size} meta={{ entity: "companies" }} />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Seed Dataset</p>
          <h3 className="mt-3 font-display text-3xl text-white">Manage crawl growth centrally</h3>
          <p className="mt-3 text-sm leading-7 text-slate-400">
            Set discovery keywords, choose geographies, seed crawled data, and rebuild downstream intelligence layers from the internal operations console.
          </p>
          <form action={queueIndiaSeedAction} className="mt-6">
            <button type="submit" className="rounded-full bg-gradient-to-r from-glow to-accent px-4 py-2 text-sm font-medium text-ink">
              Seed India crawl
            </button>
          </form>
        </Card>

        <Card>
          <h3 className="font-display text-2xl text-white">Crawler Configuration</h3>
          <div className="mt-5 space-y-3 text-sm text-slate-300">
            {Object.entries(admin.configs).map(([key, value]) => (
              <div key={key} className="rounded-2xl bg-white/5 p-4">
                <p className="text-slate-400">{key}</p>
                <p className="mt-1 text-white">{String(value)}</p>
              </div>
            ))}
          </div>
          <div className="mt-6 rounded-3xl border border-white/10 bg-black/20 p-5">
            <p className="text-sm uppercase tracking-[0.24em] text-accent">Runtime config</p>
            <div className="mt-4">
              <SuperadminConfigForm configs={admin.configs} />
            </div>
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card>
          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="font-display text-2xl text-white">Keyword Discovery</h3>
              <p className="mt-2 text-sm text-slate-400">Queue targeted discovery queries for selected cities, regions, and countries.</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <form action={rebuildInsightsAction}>
                <button type="submit" className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10">
                  Rebuild insights
                </button>
              </form>
              <form action={rebuildEmbeddingsAction}>
                <button type="submit" className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10">
                  Rebuild embeddings
                </button>
              </form>
            </div>
          </div>
          <div className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5">
            <AdminDiscoveryForm />
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-2xl text-white">Geography Scanner</h3>
          <p className="mt-2 text-sm text-slate-400">Launch geo-grid scans to seed specific cities, regions, and local market clusters.</p>
          <div className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5">
            <AdminGeoGridForm />
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Reusable Presets</p>
          <h3 className="mt-3 font-display text-3xl text-white">Save recurring crawl strategies</h3>
          <p className="mt-3 text-sm leading-7 text-slate-400">
            Build dynamic presets for onboarding new geographies, vertical sweeps, and recurring discovery campaigns. Presets can be run from the same internal operations console.
          </p>
          <div className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5">
            <SuperadminCrawlerPresetForm />
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-2xl text-white">Saved presets</h3>
          <div className="mt-5 space-y-3">
            {presets.items.length ? (
              presets.items.map((preset: any) => (
                <div key={preset.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div>
                      <p className="text-white">{preset.name}</p>
                      <p className="mt-1 text-sm text-slate-400">
                        {preset.mode} / {preset.config.source ?? "hybrid"} / {preset.config.country ?? preset.config.city ?? "global"}
                      </p>
                    </div>
                    <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">
                      {new Date(preset.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-400">
                    {preset.config.query ? <span className="rounded-full bg-black/20 px-3 py-1">Query: {preset.config.query}</span> : null}
                    {preset.config.keywords?.length ? <span className="rounded-full bg-black/20 px-3 py-1">Keywords: {preset.config.keywords.join(", ")}</span> : null}
                    {preset.config.industries?.length ? <span className="rounded-full bg-black/20 px-3 py-1">Industries: {preset.config.industries.join(", ")}</span> : null}
                    {preset.config.radius_km ? <span className="rounded-full bg-black/20 px-3 py-1">Radius: {preset.config.radius_km} km</span> : null}
                  </div>
                  <div className="mt-4">
                    <SuperadminCrawlerPresetActions presetId={preset.id} />
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                Save discovery and geo-grid filters here to build a reusable crawler playbook for the operations team.
              </div>
            )}
          </div>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-accent">Connector Health</p>
              <h3 className="mt-3 font-display text-3xl text-white">Source diagnostics and crawl quality</h3>
              <p className="mt-2 text-sm text-slate-400">
                Monitor which sources are producing parsed records, detail-enriched profiles, and higher data completeness so operations can tune crawl strategy confidently.
              </p>
            </div>
          </div>
          <div className="mt-6 grid gap-4 xl:grid-cols-2">
            {connectors.items.length ? (
              connectors.items.map((connector: any) => (
                <div key={connector.provider} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="text-white">{connector.provider}</p>
                      <p className="mt-1 text-sm text-slate-400">
                        Companies {connector.company_count} / Runs {connector.recent_runs} / Errors {connector.recent_errors}
                      </p>
                    </div>
                    <span className="rounded-full bg-black/20 px-3 py-1 text-xs text-accent">
                      Completeness {Math.round(connector.avg_completeness || 0)}
                    </span>
                  </div>
                  <div className="mt-4 grid gap-3 md:grid-cols-2">
                    <div className="rounded-2xl bg-black/20 p-3 text-sm text-slate-300">
                      <p className="text-slate-500">Parser coverage</p>
                      <p className="mt-1 text-white">{connector.parser_used_count}</p>
                    </div>
                    <div className="rounded-2xl bg-black/20 p-3 text-sm text-slate-300">
                      <p className="text-slate-500">Detail enriched</p>
                      <p className="mt-1 text-white">{connector.detail_enriched_count}</p>
                    </div>
                    <div className="rounded-2xl bg-black/20 p-3 text-sm text-slate-300 md:col-span-2">
                      <p className="text-slate-500">Average accepted results</p>
                      <p className="mt-1 text-white">{Number(connector.avg_accepted_results || 0).toFixed(1)}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                Connector diagnostics will appear here as source-specific crawls persist company metadata and worker logs.
              </div>
            )}
          </div>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Source Drilldown</p>
          <h3 className="mt-3 font-display text-3xl text-white">Coverage, categories, and recent source events</h3>
          <p className="mt-2 text-sm text-slate-400">
            Review what each connector is actually contributing to the graph so operations can tune source priority, parsing depth, and downstream enrichment rules.
          </p>
          <div className="mt-6 space-y-5">
            {connectorDetails.length ? (
              connectorDetails.map((detail: any) => (
                <div key={detail.provider} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div>
                      <p className="text-lg text-white">{detail.provider}</p>
                      <p className="mt-1 text-sm text-slate-400">
                        {detail.summary.company_count} companies / Avg rating {Number(detail.summary.avg_rating || 0).toFixed(1)} / Avg reviews{" "}
                        {Number(detail.summary.avg_reviews || 0).toFixed(0)}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2 text-xs text-slate-300">
                      {Object.entries(detail.field_coverage || {}).map(([field, value]: any) => (
                        <span key={field} className="rounded-full bg-black/20 px-3 py-1">
                          {field}: {value.count} ({Number(value.pct || 0).toFixed(0)}%)
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="mt-5 grid gap-4 xl:grid-cols-[0.7fr_1.3fr]">
                    <div className="space-y-4">
                      <div className="rounded-2xl bg-black/20 p-4">
                        <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Top categories</p>
                        <div className="mt-3 flex flex-wrap gap-2 text-sm text-slate-300">
                          {detail.top_categories?.length ? (
                            detail.top_categories.map((category: any) => (
                              <span key={`${detail.provider}-${category.label}`} className="rounded-full bg-white/5 px-3 py-1">
                                {category.label} ({category.count})
                              </span>
                            ))
                          ) : (
                            <span className="text-slate-500">No category breakdown yet.</span>
                          )}
                        </div>
                      </div>

                      <div className="rounded-2xl bg-black/20 p-4">
                        <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Recent worker events</p>
                        <div className="mt-3 space-y-2">
                          {detail.recent_logs?.length ? (
                            detail.recent_logs.map((log: any) => (
                              <div key={log.id} className="rounded-2xl border border-white/10 bg-white/5 p-3">
                                <p className="text-xs uppercase tracking-[0.2em] text-accent">{log.level}</p>
                                <p className="mt-2 text-sm text-white">{log.message}</p>
                                <p className="mt-1 text-xs text-slate-500">{new Date(log.created_at).toLocaleString()}</p>
                              </div>
                            ))
                          ) : (
                            <p className="text-sm text-slate-500">No recent events recorded for this source.</p>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="rounded-2xl bg-black/20 p-4">
                      <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Sample companies</p>
                      <div className="mt-3 grid gap-3 md:grid-cols-2">
                        {detail.sample_companies?.length ? (
                          detail.sample_companies.map((company: any) => (
                            <div key={company.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                              <p className="text-white">{company.name}</p>
                              <p className="mt-1 text-sm text-slate-400">
                                {company.city ?? "Unknown city"}{company.region ? `, ${company.region}` : ""} / {company.industry ?? "Unclassified"}
                              </p>
                              <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-300">
                                <span className="rounded-full bg-black/20 px-3 py-1">
                                  Rating {Number(company.rating || 0).toFixed(1)}
                                </span>
                                <span className="rounded-full bg-black/20 px-3 py-1">
                                  Reviews {company.reviews_count}
                                </span>
                                <span className="rounded-full bg-black/20 px-3 py-1">
                                  {company.website ? "Website found" : "No website"}
                                </span>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-500 md:col-span-2">
                            Sample companies will appear here once this connector has persisted records.
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                Connector drilldown will appear here as source-specific crawls produce persisted company records and worker events.
              </div>
            )}
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card>
          <h3 className="font-display text-2xl text-white">Job Monitor</h3>
          <div className="mt-5 space-y-3">
            {admin.jobs.length ? (
              admin.jobs.map((job: any) => (
                <div key={job.id} className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="text-white">{job.job_type}</p>
                      <p className="mt-1 text-sm text-slate-400">
                        Priority {job.priority} / Attempts {job.attempts}
                      </p>
                    </div>
                    <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{job.status}</span>
                  </div>
                  <p className="mt-3 break-all text-xs text-slate-500">{job.id}</p>
                </div>
              ))
            ) : (
              <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                Jobs will appear here when the crawler queue is active.
              </div>
            )}
          </div>
        </Card>

        <Card>
          <h3 className="font-display text-2xl text-white">Recent Logs</h3>
          <div className="mt-5 space-y-3">
            {admin.logs.length ? (
              admin.logs.map((log: any) => (
                <div key={log.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-accent">{log.level}</p>
                  <p className="mt-2 text-white">{log.message}</p>
                  <p className="mt-1 text-sm text-slate-400">
                    {log.source} / {new Date(log.created_at).toLocaleString()}
                  </p>
                </div>
              ))
            ) : (
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
                Logs will stream here as crawl and enrichment jobs execute.
              </div>
            )}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
