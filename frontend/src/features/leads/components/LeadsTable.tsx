import Link from "next/link";

import { Button } from "@/components/ui/Button";
import { resumeUrl } from "../api";
import type { Lead } from "../types";
import { StatusBadge } from "./StatusBadge";

interface LeadsTableProps {
  leads: Lead[];
  updatingId: string | null;
  onMarkReachedOut: (lead: Lead) => void;
}

export function LeadsTable({
  leads,
  updatingId,
  onMarkReachedOut,
}: LeadsTableProps) {
  return (
    <div className="mt-6 overflow-x-auto rounded-lg border border-black/10 dark:border-white/10">
      <table className="w-full text-left text-sm">
        <thead className="bg-black/5 dark:bg-white/10">
          <tr>
            <th className="px-4 py-2 font-medium">Name</th>
            <th className="px-4 py-2 font-medium">Email</th>
            <th className="px-4 py-2 font-medium">Resume</th>
            <th className="px-4 py-2 font-medium">Status</th>
            <th className="px-4 py-2 font-medium">Submitted</th>
            <th className="px-4 py-2 font-medium">Action</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr
              key={lead.id}
              className="border-t border-black/10 dark:border-white/10"
            >
              <td className="whitespace-nowrap px-4 py-2">
                <Link href={`/leads/${lead.id}`} className="hover:underline">
                  {lead.first_name} {lead.last_name}
                </Link>
              </td>
              <td className="px-4 py-2">{lead.email}</td>
              <td className="px-4 py-2">
                <a
                  href={resumeUrl(lead.id)}
                  target="_blank"
                  rel="noreferrer"
                  className="underline"
                >
                  {lead.resume_filename}
                </a>
              </td>
              <td className="px-4 py-2">
                <StatusBadge status={lead.status} />
              </td>
              <td className="whitespace-nowrap px-4 py-2 text-black/60 dark:text-white/60">
                {new Date(lead.created_at).toLocaleDateString()}
              </td>
              <td className="whitespace-nowrap px-4 py-2">
                {lead.status === "PENDING" ? (
                  <Button
                    className="px-3 py-1 text-xs"
                    disabled={updatingId === lead.id}
                    onClick={() => onMarkReachedOut(lead)}
                  >
                    {updatingId === lead.id
                      ? "Updating..."
                      : "Mark Reached Out"}
                  </Button>
                ) : (
                  <span className="text-xs text-black/40 dark:text-white/40">
                    —
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
