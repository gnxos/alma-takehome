import { Button } from "@/components/ui/Button";
import { DownloadIcon, ExternalLinkIcon } from "@/components/ui/icons";
import { resumeUrl } from "../api";
import type { Lead } from "../types";
import { StatusBadge } from "./StatusBadge";

interface LeadsTableProps {
  leads: Lead[];
  updatingId: string | null;
  onOpen: (leadId: string) => void;
  onSelectEmail: (email: string) => void;
  onMarkReachedOut: (lead: Lead) => void;
}

export function LeadsTable({
  leads,
  updatingId,
  onOpen,
  onSelectEmail,
  onMarkReachedOut,
}: LeadsTableProps) {
  return (
    <>
      <div className="mt-6 flex flex-col gap-3 sm:hidden">
        {leads.map((lead) => (
          <div key={lead.id} className="rounded-card bg-paper-0 p-4 shadow-card">
            <button
              onClick={() => onOpen(lead.id)}
              className="block w-full text-left"
            >
              <div className="flex items-start justify-between gap-2">
                <span className="text-heading-md text-ink-900">
                  {lead.first_name} {lead.last_name}
                </span>
                <StatusBadge status={lead.status} />
              </div>
              <p className="mt-1 font-mono-alma text-mono-sm text-brass-500">
                {lead.reference_number}
              </p>
              <p className="mt-1 text-body-sm text-ink-400">
                {new Date(lead.created_at).toLocaleDateString()}
              </p>
            </button>
            <button
              onClick={() => onSelectEmail(lead.email)}
              className="mt-2 font-mono-alma text-mono-sm text-navy-600 underline decoration-navy-600/30 underline-offset-2 hover:decoration-navy-600"
              aria-label={`Show all tickets for ${lead.email}`}
            >
              {lead.email}
            </button>
          </div>
        ))}
      </div>

      <div className="mt-6 hidden overflow-x-auto rounded-card border border-paper-100 sm:block">
        <table className="w-full text-left text-body-md">
          <thead className="bg-paper-100">
            <tr>
              <th className="h-11 px-4 text-label-sm text-ink-700">Id</th>
              <th className="h-11 px-4 text-label-sm text-ink-700">Name</th>
              <th className="h-11 px-4 text-label-sm text-ink-700">Email</th>
              <th className="h-11 px-4 text-label-sm text-ink-700">Resume</th>
              <th className="h-11 px-4 text-label-sm text-ink-700">Status</th>
              <th className="h-11 px-4 text-label-sm text-ink-700">
                Submitted
              </th>
              <th className="h-11 px-4 text-label-sm text-ink-700">Action</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr
                key={lead.id}
                onClick={() => onOpen(lead.id)}
                className="h-14 cursor-pointer border-t border-paper-100 hover:bg-paper-50"
              >
                <td className="whitespace-nowrap px-4">
                  <span className="inline-flex items-center gap-1.5 font-mono-alma text-mono-sm text-brass-500">
                    {lead.reference_number}
                    <ExternalLinkIcon className="size-3.5 text-ink-400" />
                  </span>
                </td>
                <td className="whitespace-nowrap px-4 text-ink-900">
                  {lead.first_name} {lead.last_name}
                </td>
                <td
                  className="px-4"
                  onClick={(event) => event.stopPropagation()}
                >
                  <button
                    onClick={() => onSelectEmail(lead.email)}
                    className="font-mono-alma text-mono-sm text-navy-600 underline decoration-navy-600/30 underline-offset-2 hover:decoration-navy-600"
                    aria-label={`Show all tickets for ${lead.email}`}
                  >
                    {lead.email}
                  </button>
                </td>
                <td className="px-4" onClick={(event) => event.stopPropagation()}>
                  <a
                    href={resumeUrl(lead.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 text-ink-700 hover:underline"
                    title="Download resume"
                  >
                    {lead.resume_filename}
                    <DownloadIcon className="size-3.5 text-ink-400" />
                  </a>
                </td>
                <td className="whitespace-nowrap px-4">
                  <StatusBadge status={lead.status} />
                </td>
                <td className="whitespace-nowrap px-4 text-ink-400">
                  {new Date(lead.created_at).toLocaleDateString()}
                </td>
                <td
                  className="whitespace-nowrap px-4"
                  onClick={(event) => event.stopPropagation()}
                >
                  {lead.status === "PENDING" ? (
                    <Button
                      variant="secondary"
                      className="!h-8 !px-3 !text-body-sm"
                      disabled={updatingId === lead.id}
                      onClick={() => onMarkReachedOut(lead)}
                    >
                      {updatingId === lead.id
                        ? "Updating..."
                        : "Mark Reached Out"}
                    </Button>
                  ) : (
                    <span className="text-body-sm text-ink-400">&mdash;</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
