import { AppShell } from "@/components/app-shell";
import {
  SuperadminSupportNoteForm,
  SuperadminSupportTicketCreateForm,
  SuperadminSupportTicketUpdateForm
} from "@/components/forms/superadmin-forms";
import { Card } from "@/components/ui/card";
import { getAdminData, getAdminSupportNotes, getAdminSupportTickets } from "@/lib/data";

export default async function SuperadminSupportPage() {
  const [tickets, admin] = await Promise.all([getAdminSupportTickets(), getAdminData()]);
  const notesByTicket = Object.fromEntries(
    await Promise.all(
      tickets.items.map(async (ticket: any) => {
        const notes = await getAdminSupportNotes(ticket.id);
        return [ticket.id, notes.items];
      })
    )
  );

  return (
    <AppShell eyebrow="Superadmin Support" title="Internal support queue and client issues" mode="superadmin">
      <div className="mb-6">
        <Card>
          <p className="text-xs uppercase tracking-[0.3em] text-accent">Create Ticket</p>
          <h3 className="mt-3 font-display text-3xl text-white">Track platform or client issues internally</h3>
          <div className="mt-5">
            <SuperadminSupportTicketCreateForm
              organizations={admin.organizations.map((organization: any) => ({
                id: organization.id,
                name: organization.name
              }))}
              users={admin.users.map((user: any) => ({
                id: user.id,
                name: user.full_name
              }))}
            />
          </div>
        </Card>
      </div>

      <div className="grid gap-6">
        {tickets.items.length ? (
          tickets.items.map((ticket: any) => (
            <Card key={ticket.id}>
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-white">{ticket.title}</p>
                  <p className="mt-1 text-sm text-slate-400">{ticket.organization_id ?? "Platform-wide"}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    Assignee {ticket.assignee_user_id ?? "unassigned"} / SLA {ticket.sla_label ?? "none"}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    {ticket.notes_count ?? 0} internal notes {ticket.last_note_at ? `/ Last note ${new Date(ticket.last_note_at).toLocaleString()}` : ""}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-accent">{ticket.priority}</span>
                  <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-slate-200">{ticket.status}</span>
                </div>
              </div>
              <div className="mt-5 grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
                <div className="space-y-4">
                  <div className="rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
                    <p>{ticket.description}</p>
                    <p className="mt-4 text-xs text-slate-500">{new Date(ticket.created_at).toLocaleString()}</p>
                  </div>
                  <div className="rounded-3xl border border-white/10 bg-black/20 p-4">
                    <p className="text-xs uppercase tracking-[0.24em] text-accent">Internal notes</p>
                    <div className="mt-4 space-y-3">
                      {(notesByTicket[ticket.id] ?? []).length ? (
                        (notesByTicket[ticket.id] ?? []).map((note: any) => (
                          <div key={note.id} className="rounded-2xl border border-white/10 bg-white/5 p-3">
                            <p className="text-sm text-white">{note.body}</p>
                            <p className="mt-2 text-xs text-slate-500">
                              {note.author_label ?? note.author_user_id ?? "Internal team"} / {new Date(note.created_at).toLocaleString()}
                            </p>
                          </div>
                        ))
                      ) : (
                        <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-slate-400">
                          No internal notes yet.
                        </div>
                      )}
                    </div>
                    <div className="mt-4">
                      <SuperadminSupportNoteForm ticketId={ticket.id} />
                    </div>
                  </div>
                </div>
                <div className="rounded-3xl border border-white/10 bg-black/20 p-4">
                  <SuperadminSupportTicketUpdateForm
                    ticketId={ticket.id}
                    defaultPriority={ticket.priority}
                    defaultStatus={ticket.status}
                    defaultDescription={ticket.description}
                    defaultAssigneeUserId={ticket.assignee_user_id}
                    defaultSlaLabel={ticket.sla_label}
                    users={admin.users.map((user: any) => ({
                      id: user.id,
                      name: user.full_name
                    }))}
                  />
                </div>
              </div>
            </Card>
          ))
        ) : (
          <Card>
            <p className="text-white">No support tickets have been created yet.</p>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
