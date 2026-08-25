import { DownloadIcon, ExternalLinkIcon } from "@/components/ui/icons";
import { resumeUrl } from "../api";
import type { Lead, LeadStatus } from "../types";
import { StatusBadge, StatusSelect } from "./StatusBadge";

interface LeadsTableProps {
  leads: Lead[];
  updatingId: string | null;
  onOpen: (leadId: string) => void;
  onOpenEmail: (email: string) => void;
  onChangeStatus: (lead: Lead, status: LeadStatus) => void;
}

export function LeadsTable({
  leads,
  updatingId,
  onOpen,
  onOpenEmail,
  onChangeStatus,
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
                {lead.resolved_by && lead.status === "REACHED_OUT" && (
                  <span className="ml-2 font-mono-alma text-xs text-navy-600">
                    • resolved by {lead.resolved_by.split("@")[0]}
                  </span>
                )}
              </p>
            </button>
            <button
              onClick={() => onOpenEmail(lead.email)}
              className="mt-2 font-mono-alma text-mono-sm text-navy-600 underline decoration-navy-600/30 underline-offset-2 hover:decoration-navy-600"
              aria-label={`Open all tickets for ${lead.email}`}
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
                    onClick={() => onOpenEmail(lead.email)}
                    className="font-mono-alma text-mono-sm text-navy-600 underline decoration-navy-600/30 underline-offset-2 hover:decoration-navy-600"
                    aria-label={`Open all tickets for ${lead.email}`}
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
                <td className="whitespace-nowrap px-4" onClick={(event) => event.stopPropagation()}>
                  <StatusSelect
                    status={lead.status}
                    disabled={updatingId === lead.id}
                    onChange={(status) => onChangeStatus(lead, status)}
                  />
                  {lead.resolved_by && lead.status === "REACHED_OUT" && (
                    <p className="mt-0.5 font-mono-alma text-[11px] text-ink-500 truncate max-w-[140px]" title={`Resolved by ${lead.resolved_by}`}>
                      by {lead.resolved_by.split("@")[0]}
                    </p>
                  )}
                </td>
                <td className="whitespace-nowrap px-4 text-ink-400">
                  {new Date(lead.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
