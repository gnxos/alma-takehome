"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { ChevronDownIcon } from "@/components/ui/icons";
import { buttonClasses } from "@/components/ui/Button";
import { logout, redirectToLogin } from "@/features/auth/api";
import { useLeads } from "../hooks/useLeads";
import type { LeadFilter } from "../types";
import { EmailTicketsDrawer } from "./EmailTicketsDrawer";
import { LeadModal } from "./LeadModal";
import { LeadsTable } from "./LeadsTable";

const STATUS_FILTERS: { label: string; value: LeadFilter }[] = [
  { label: "All", value: "ALL" },
  { label: "Pending", value: "PENDING" },
  { label: "Reached Out", value: "REACHED_OUT" },
];

export function LeadsDashboard() {
  return (
    <Suspense fallback={null}>
      <LeadsDashboardContent />
    </Suspense>
  );
}

function LeadsDashboardContent() {
  const searchParams = useSearchParams();
  const [filter, setFilter] = useState<LeadFilter>("ALL");
  const [viewLeadId, setViewLeadId] = useState<string | null>(null);
  const [viewEmail, setViewEmail] = useState<string | null>(null);
  const [deepLinkConsumed, setDeepLinkConsumed] = useState(false);
  const {
    attorneyEmail,
    leads,
    loading,
    error,
    updatingId,
    applyUpdate,
    changeStatus,
  } = useLeads();

  if (!deepLinkConsumed && leads.length > 0) {
    setDeepLinkConsumed(true);
    const referenceNumber = searchParams.get("ref");
    const match = referenceNumber
      ? leads.find((lead) => lead.reference_number === referenceNumber)
      : undefined;
    if (match) setViewLeadId(match.id);
  }

  const visibleLeads =
    filter === "ALL"
      ? leads
      : leads.filter((lead) => lead.status === filter);
  const pendingCount = leads.filter((lead) => lead.status === "PENDING").length;
  const reachedOutCount = leads.length - pendingCount;

  async function handleLogout() {
    await logout();
    redirectToLogin();
  }

  function handleOpenLead(leadId: string) {
    setViewEmail(null);
    setViewLeadId(leadId);
  }

  function handleOpenEmail(email: string) {
    setViewLeadId(null);
    setViewEmail(email);
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
              {leads.length} total &middot; {pendingCount} pending
            </p>
          </div>
          <Link href="/" className={buttonClasses()}>
            + Add Lead
          </Link>
        </div>

        {!loading && leads.length > 0 && (
          <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <StatCard label="Total leads" value={leads.length} />
            <StatCard label="Pending" value={pendingCount} tone="ochre" />
            <StatCard label="Reached out" value={reachedOutCount} tone="sage" />
          </div>
        )}

        <div className="mt-6 flex items-center justify-end">
          <div className="flex items-center gap-2">
            <label
              htmlFor="status-filter"
              className="text-label-sm font-medium text-ink-700"
            >
              Status:
            </label>
            <div className="relative">
              <select
                id="status-filter"
                value={filter}
                onChange={(event) =>
                  setFilter(event.target.value as LeadFilter)
                }
                className="h-9 cursor-pointer appearance-none rounded-input border border-ink-200 bg-paper-0 py-1.5 pl-3 pr-8 text-body-sm font-medium text-ink-900 shadow-sm transition hover:border-ink-400 focus:border-navy-600 focus:outline-none focus:ring-2 focus:ring-navy-600/20"
              >
                {STATUS_FILTERS.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2.5 text-ink-400">
                <ChevronDownIcon className="size-4" />
              </div>
            </div>
          </div>
        </div>

        {error && (
          <p className="mt-6 rounded-input bg-brick-50 px-4 py-3 text-body-sm text-brick-600">
            {error}
          </p>
        )}

        {loading && <SkeletonTable />}

        {!loading && !error && leads.length === 0 && (
          <div className="mt-10 text-center">
            <p className="text-body-md text-ink-700">No applications yet.</p>
            <p className="mt-1 text-body-sm text-ink-400">
              New submissions from the intake form will show up here.
            </p>
          </div>
        )}

        {!loading && !error && leads.length > 0 && visibleLeads.length === 0 && (
          <p className="mt-10 text-center text-body-md text-ink-700">
            No leads match this filter.
          </p>
        )}

        {!loading && visibleLeads.length > 0 && (
          <LeadsTable
            leads={visibleLeads}
            updatingId={updatingId}
            onOpen={handleOpenLead}
            onOpenEmail={handleOpenEmail}
            onChangeStatus={changeStatus}
          />
        )}
      </div>

      {viewLeadId && (
        <LeadModal
          leadId={viewLeadId}
          onClose={() => setViewLeadId(null)}
          onUpdated={applyUpdate}
        />
      )}

      {viewEmail && (
        <EmailTicketsDrawer
          key={viewEmail}
          email={viewEmail}
          onClose={() => setViewEmail(null)}
          onUpdated={applyUpdate}
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
    tone === "ochre"
      ? "text-ochre-600"
      : tone === "sage"
        ? "text-sage-600"
        : "text-ink-900";
  return (
    <div className="rounded-card border border-paper-100 bg-paper-0 p-5">
      <p className={`text-[28px] font-semibold leading-none ${numberColor}`}>
        {value}
      </p>
      <p className="mt-2 text-label-sm text-ink-400">{label}</p>
    </div>
  );
}

function SkeletonTable() {
  return (
    <div className="mt-6 hidden animate-pulse gap-px overflow-hidden rounded-card border border-paper-100 sm:flex sm:flex-col">
      {Array.from({ length: 6 }).map((_, index) => (
        <div
          key={index}
          className="flex h-14 items-center gap-6 bg-paper-0 px-4"
        >
          <div className="h-3 w-32 rounded-input bg-paper-100" />
          <div className="h-3 w-40 rounded-input bg-paper-100" />
          <div className="h-3 w-24 rounded-input bg-paper-100" />
          <div className="h-3 w-20 rounded-input bg-paper-100" />
        </div>
      ))}
    </div>
  );
}
