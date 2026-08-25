"use client";

import Link from "next/link";

import { Button } from "@/components/ui/Button";
import { resumeUrl } from "../api";
import { useLead } from "../hooks/useLead";
import { StatusBadge } from "./StatusBadge";

export function LeadDetail({ leadId }: { leadId: string }) {
  const { lead, loading, error, saving, markReachedOut } = useLead(leadId);

  if (loading) {
    return <p className="mx-auto max-w-2xl px-6 py-12 text-sm">Loading...</p>;
  }

  if (error && !lead) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-12">
        <p className="text-sm text-red-600">{error}</p>
        <Link href="/leads" className="mt-4 inline-block text-sm underline">
          Back to leads
        </Link>
      </div>
    );
  }

  if (!lead) return null;

  return (
    <div className="mx-auto max-w-2xl px-6 py-12">
      <Link href="/leads" className="text-sm underline">
        Back to leads
      </Link>

      <div className="mt-4 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">
          {lead.first_name} {lead.last_name}
        </h1>
        <StatusBadge status={lead.status} />
      </div>

      <dl className="mt-6 grid grid-cols-[auto_1fr] gap-x-4 gap-y-3 text-sm">
        <dt className="text-black/60 dark:text-white/60">Email</dt>
        <dd>{lead.email}</dd>

        <dt className="text-black/60 dark:text-white/60">Resume / CV</dt>
        <dd>
          <a
            href={resumeUrl(lead.id)}
            target="_blank"
            rel="noreferrer"
            className="underline"
          >
            {lead.resume_filename}
          </a>
        </dd>

        <dt className="text-black/60 dark:text-white/60">Submitted</dt>
        <dd>{new Date(lead.created_at).toLocaleString()}</dd>

        <dt className="text-black/60 dark:text-white/60">Last updated</dt>
        <dd>{new Date(lead.updated_at).toLocaleString()}</dd>
      </dl>

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      {lead.status === "PENDING" && (
        <Button
          className="mt-8 text-sm"
          disabled={saving}
          onClick={markReachedOut}
        >
          {saving ? "Updating..." : "Mark as Reached Out"}
        </Button>
      )}
    </div>
  );
}
