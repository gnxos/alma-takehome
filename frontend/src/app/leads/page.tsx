"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import {
  UnauthorizedError,
  getLead,
  getMe,
  listLeads,
  logout,
  redirectToLogin,
  resumeUrl,
  updateLead,
} from "@/lib/api";
import { CloseIcon, DownloadIcon, ExternalLinkIcon } from "@/components/icons";
import { Button, buttonClasses } from "@/components/Button";
import type { Lead, LeadStatus } from "@/lib/types";

const STATUS_FILTERS: { label: string; value: LeadStatus | "ALL" }[] = [
  { label: "All", value: "ALL" },
  { label: "Pending", value: "PENDING" },
  { label: "Reached Out", value: "REACHED_OUT" },
];

export default function LeadsPage() {
  return (
    <Suspense fallback={null}>
      <LeadsPageContent />
    </Suspense>
  );
}

function LeadsPageContent() {
  const searchParams = useSearchParams();
  const [attorneyEmail, setAttorneyEmail] = useState<string | null>(null);
  const [allLeads, setAllLeads] = useState<Lead[]>([]);
  const [filter, setFilter] = useState<LeadStatus | "ALL">("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [viewLeadId, setViewLeadId] = useState<string | null>(null);

  useEffect(() => {
    getMe()
      .then((attorney) => setAttorneyEmail(attorney.email))
      .catch(() => {});
  }, []);

  useEffect(() => {
    let cancelled = false;
    listLeads()
      .then((data) => {
        if (!cancelled) setAllLeads(data.items);
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof UnauthorizedError) {
          redirectToLogin();
          return;
        }
        setError(err instanceof Error ? err.message : "Couldn't load leads.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Deep-link support (?ref=INT-2026-7473): open that lead once the list has
  // loaded. A render-time state adjustment (React's documented alternative to
  // an effect for "sync once when data arrives"), guarded by state so it only
  // fires once and a user closing the modal isn't immediately reopened.
  const [deepLinkConsumed, setDeepLinkConsumed] = useState(false);
  if (!deepLinkConsumed && allLeads.length > 0) {
    setDeepLinkConsumed(true);
    const ref = searchParams.get("ref");
    const match = ref ? allLeads.find((l) => l.reference_number === ref) : undefined;
    if (match) setViewLeadId(match.id);
  }

  const visibleLeads =
    filter === "ALL" ? allLeads : allLeads.filter((l) => l.status === filter);
  const pendingCount = allLeads.filter((l) => l.status === "PENDING").length;
  const reachedOutCount = allLeads.length - pendingCount;

  function applyLeadUpdate(updated: Lead) {
    setAllLeads((current) => current.map((l) => (l.id === updated.id ? updated : l)));
  }

  async function markReachedOut(lead: Lead) {
    setUpdatingId(lead.id);
    setError(null);
    try {
      const updated = await updateLead(lead.id, { status: "REACHED_OUT" });
      applyLeadUpdate(updated);
    } catch (err) {
      if (err instanceof UnauthorizedError) {
        redirectToLogin();
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to update lead.");
    } finally {
      setUpdatingId(null);
    }
  }

  async function handleLogout() {
    await logout();
    redirectToLogin();
  }

  return (
    <div className="min-h-screen bg-paper-50 font-sans">
      <header className="flex h-14 items-center justify-between border-b border-ink-200 bg-paper-0 px-6">
        <span className="text-heading-md font-bold tracking-tight text-ink-900">
          alma
        </span>
        <div className="flex items-center gap-4">
          {attorneyEmail && (
            <span className="hidden text-body-sm text-ink-700 sm:inline">
              {attorneyEmail}
            </span>
          )}
          <button
            onClick={handleLogout}
            className="text-body-sm font-medium text-ink-700 hover:text-ink-900"
          >
            Sign out
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-[1280px] px-6 py-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-heading-lg text-ink-900">Manage Leads</h1>
            <p className="mt-1 text-body-sm text-ink-400">
              {allLeads.length} total &middot; {pendingCount} pending
            </p>
          </div>
          <Link href="/" className={buttonClasses()}>
            + Add Lead
          </Link>
        </div>

        {!loading && allLeads.length > 0 && (
          <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <StatCard label="Total leads" value={allLeads.length} />
            <StatCard label="Pending" value={pendingCount} tone="ochre" />
            <StatCard label="Reached out" value={reachedOutCount} tone="sage" />
          </div>
        )}

        <div className="mt-6 flex gap-2">
          {STATUS_FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setFilter(f.value)}
              className={`rounded-pill px-3 py-1 text-body-sm font-medium ${
                filter === f.value
                  ? "bg-navy-600 text-paper-0"
                  : "bg-paper-100 text-ink-700 hover:bg-paper-100/70"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {error && (
          <p className="mt-6 rounded-input bg-brick-50 px-4 py-3 text-body-sm text-brick-600">
            {error}
          </p>
        )}

        {loading && <SkeletonTable />}

        {!loading && !error && allLeads.length === 0 && (
          <div className="mt-10 text-center">
            <p className="text-body-md text-ink-700">No applications yet.</p>
            <p className="mt-1 text-body-sm text-ink-400">
              New submissions from the intake form will show up here.
            </p>
          </div>
        )}

        {!loading && !error && allLeads.length > 0 && visibleLeads.length === 0 && (
          <p className="mt-10 text-center text-body-md text-ink-700">
            No leads match this filter.
          </p>
        )}

        {!loading && visibleLeads.length > 0 && (
          <>
            {/* Compact: stacked cards */}
            <div className="mt-6 flex flex-col gap-3 sm:hidden">
              {visibleLeads.map((lead) => (
                <button
                  key={lead.id}
                  onClick={() => setViewLeadId(lead.id)}
                  className="rounded-card bg-paper-0 p-4 text-left shadow-card"
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
                    {lead.email} &middot; {new Date(lead.created_at).toLocaleDateString()}
                  </p>
                </button>
              ))}
            </div>

            {/* Regular/Wide: table */}
            <div className="mt-6 hidden overflow-x-auto rounded-card border border-paper-100 sm:block">
              <table className="w-full text-left text-body-md">
                <thead className="bg-paper-100">
                  <tr>
                    <th className="h-11 px-4 text-label-sm text-ink-700">Id</th>
                    <th className="h-11 px-4 text-label-sm text-ink-700">Name</th>
                    <th className="h-11 px-4 text-label-sm text-ink-700">Email</th>
                    <th className="h-11 px-4 text-label-sm text-ink-700">Resume</th>
                    <th className="h-11 px-4 text-label-sm text-ink-700">Status</th>
                    <th className="h-11 px-4 text-label-sm text-ink-700">Submitted</th>
                    <th className="h-11 px-4 text-label-sm text-ink-700">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleLeads.map((lead) => (
                    <tr
                      key={lead.id}
                      onClick={() => setViewLeadId(lead.id)}
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
                      <td className="px-4 font-mono-alma text-mono-sm text-ink-700">
                        {lead.email}
                      </td>
                      <td className="px-4" onClick={(e) => e.stopPropagation()}>
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
                      <td className="whitespace-nowrap px-4" onClick={(e) => e.stopPropagation()}>
                        {lead.status === "PENDING" ? (
                          <Button
                            variant="secondary"
                            className="!h-8 !px-3 !text-body-sm"
                            disabled={updatingId === lead.id}
                            onClick={() => markReachedOut(lead)}
                          >
                            {updatingId === lead.id ? "Updating..." : "Mark Reached Out"}
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
        )}
      </div>

      {viewLeadId && (
        <LeadModal
          leadId={viewLeadId}
          onClose={() => setViewLeadId(null)}
          onUpdated={applyLeadUpdate}
        />
      )}
    </div>
  );
}

function StatCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone?: "ochre" | "sage";
}) {
  const numberColor =
    tone === "ochre" ? "text-ochre-600" : tone === "sage" ? "text-sage-600" : "text-ink-900";
  return (
    <div className="rounded-card border border-paper-100 bg-paper-0 p-5">
      <p className={`text-[28px] font-semibold leading-none ${numberColor}`}>{value}</p>
      <p className="mt-2 text-label-sm text-ink-400">{label}</p>
    </div>
  );
}

function SkeletonTable() {
  return (
    <div className="mt-6 hidden animate-pulse gap-px overflow-hidden rounded-card border border-paper-100 sm:flex sm:flex-col">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="flex h-14 items-center gap-6 bg-paper-0 px-4">
          <div className="h-3 w-32 rounded-input bg-paper-100" />
          <div className="h-3 w-40 rounded-input bg-paper-100" />
          <div className="h-3 w-24 rounded-input bg-paper-100" />
          <div className="h-3 w-20 rounded-input bg-paper-100" />
        </div>
      ))}
    </div>
  );
}

function LeadModal({
  leadId,
  onClose,
  onUpdated,
}: {
  leadId: string;
  onClose: () => void;
  onUpdated: (lead: Lead) => void;
}) {
  const [lead, setLead] = useState<Lead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getLead(leadId)
      .then((data) => {
        if (!cancelled) setLead(data);
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof UnauthorizedError) {
          redirectToLogin();
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
  }, [leadId]);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  async function markReachedOut() {
    if (!lead) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await updateLead(lead.id, { status: "REACHED_OUT" });
      setLead(updated);
      onUpdated(updated);
    } catch (err) {
      if (err instanceof UnauthorizedError) {
        redirectToLogin();
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to update lead.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink-900/40 px-4"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        onClick={(event) => event.stopPropagation()}
        className="w-full max-w-lg rounded-card bg-paper-0 p-6 shadow-modal"
      >
        <div className="flex items-start justify-between">
          <div>
            {lead && (
              <p className="font-mono-alma text-mono-sm text-brass-500">
                {lead.reference_number}
              </p>
            )}
            <h2 className="mt-1 text-heading-lg text-ink-900">
              {loading ? "Loading..." : lead ? `${lead.first_name} ${lead.last_name}` : "Lead"}
            </h2>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className="rounded-input p-1 text-ink-400 hover:bg-paper-100"
          >
            <CloseIcon className="size-5" />
          </button>
        </div>

        {loading && <p className="mt-4 text-body-md text-ink-700">Loading...</p>}

        {!loading && lead && (
          <>
            <div className="mt-2">
              <StatusBadge status={lead.status} />
            </div>

            <dl className="mt-5 grid grid-cols-[auto_1fr] gap-x-4 gap-y-3 text-body-md">
              <dt className="text-label-sm text-ink-400">Email</dt>
              <dd className="font-mono-alma text-mono-sm text-ink-900">{lead.email}</dd>

              <dt className="text-label-sm text-ink-400">Resume / CV</dt>
              <dd>
                <a
                  href={resumeUrl(lead.id)}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 text-ink-900 underline"
                  title="Download resume"
                >
                  {lead.resume_filename}
                  <DownloadIcon className="size-3.5 text-ink-400" />
                </a>
              </dd>

              <dt className="text-label-sm text-ink-400">Submitted</dt>
              <dd className="text-ink-900">{new Date(lead.created_at).toLocaleString()}</dd>

              <dt className="text-label-sm text-ink-400">Last updated</dt>
              <dd className="text-ink-900">{new Date(lead.updated_at).toLocaleString()}</dd>
            </dl>

            {lead.status === "PENDING" && (
              <div className="mt-6 border-t border-ink-200 pt-4">
                <Button onClick={markReachedOut} loading={saving} fullWidth>
                  {saving ? "Updating..." : "Mark as reached out"}
                </Button>
              </div>
            )}
          </>
        )}

        {error && <p className="mt-4 text-body-sm text-brick-600">{error}</p>}
      </div>
    </div>
  );
}

export function StatusBadge({ status }: { status: LeadStatus }) {
  const isPending = status === "PENDING";
  return (
    <span
      className={`inline-block whitespace-nowrap rounded-pill px-2 py-0.5 text-label-sm normal-case tracking-normal ${
        isPending ? "bg-ochre-50 text-ochre-600" : "bg-sage-50 text-sage-600"
      }`}
    >
      {isPending ? "Pending" : "Reached out"}
    </span>
  );
}
