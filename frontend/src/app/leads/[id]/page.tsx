"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { UnauthorizedError, getLead, resumeUrl, updateLead } from "@/lib/api";
import type { Lead } from "@/lib/types";
import { StatusBadge } from "../page";

export default function LeadDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [lead, setLead] = useState<Lead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getLead(params.id)
      .then((data) => {
        if (!cancelled) setLead(data);
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof UnauthorizedError) {
          router.push("/login");
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to load lead.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [params.id, router]);

  async function markReachedOut() {
    if (!lead) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await updateLead(lead.id, { status: "REACHED_OUT" });
      setLead(updated);
    } catch (err) {
      if (err instanceof UnauthorizedError) {
        router.push("/login");
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to update lead.");
    } finally {
      setSaving(false);
    }
  }

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
        <button
          onClick={markReachedOut}
          disabled={saving}
          className="mt-8 rounded-md bg-black px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-white dark:text-black"
        >
          {saving ? "Updating..." : "Mark as Reached Out"}
        </button>
      )}
    </div>
  );
}
