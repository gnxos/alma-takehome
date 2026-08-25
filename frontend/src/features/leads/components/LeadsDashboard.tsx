"use client";

import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/Button";
import { logout } from "@/features/auth/api";
import { useLeads } from "../hooks/useLeads";
import type { LeadFilter } from "../types";
import { LeadsTable } from "./LeadsTable";

const STATUS_FILTERS: { label: string; value: LeadFilter }[] = [
  { label: "All", value: "ALL" },
  { label: "Pending", value: "PENDING" },
  { label: "Reached Out", value: "REACHED_OUT" },
];

export function LeadsDashboard() {
  const router = useRouter();
  const {
    filter,
    leads,
    loading,
    error,
    updatingId,
    selectFilter,
    markReachedOut,
  } = useLeads();

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Leads</h1>
          <p className="mt-2 text-sm text-black/60 dark:text-white/60">
            Prospects who&apos;ve submitted the intake form. Mark a lead as
            reached out once you&apos;ve contacted them.
          </p>
        </div>
        <Button variant="secondary" className="text-sm" onClick={handleLogout}>
          Log out
        </Button>
      </div>

      <div className="mt-4 flex gap-2">
        {STATUS_FILTERS.map((item) => (
          <button
            key={item.value}
            onClick={() => selectFilter(item.value)}
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              filter === item.value
                ? "bg-black text-white dark:bg-white dark:text-black"
                : "bg-black/5 dark:bg-white/10"
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      {error && <p className="mt-6 text-sm text-red-600">{error}</p>}
      {loading && (
        <p className="mt-6 text-sm text-black/60 dark:text-white/60">
          Loading...
        </p>
      )}
      {!loading && !error && leads.length === 0 && (
        <p className="mt-6 text-sm text-black/60 dark:text-white/60">
          No leads yet.
        </p>
      )}
      {!loading && leads.length > 0 && (
        <LeadsTable
          leads={leads}
          updatingId={updatingId}
          onMarkReachedOut={markReachedOut}
        />
      )}
    </div>
  );
}
