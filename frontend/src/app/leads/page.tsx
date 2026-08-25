"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  UnauthorizedError,
  listLeads,
  logout,
  resumeUrl,
  updateLead,
} from "@/lib/api";
import type { Lead, LeadStatus } from "@/lib/types";

const STATUS_FILTERS: { label: string; value: LeadStatus | "ALL" }[] = [
  { label: "All", value: "ALL" },
  { label: "Pending", value: "PENDING" },
  { label: "Reached Out", value: "REACHED_OUT" },
];

export default function LeadsPage() {
  const router = useRouter();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [filter, setFilter] = useState<LeadStatus | "ALL">("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listLeads(filter === "ALL" ? undefined : filter)
      .then((data) => {
        if (!cancelled) setLeads(data.items);
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof UnauthorizedError) {
          router.push("/login");
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to load leads.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [filter, router]);

  async function markReachedOut(lead: Lead) {
    setUpdatingId(lead.id);
    setError(null);
    try {
      const updated = await updateLead(lead.id, { status: "REACHED_OUT" });
      setLeads((current) =>
        filter === "PENDING"
          ? current.filter((l) => l.id !== lead.id)
          : current.map((l) => (l.id === lead.id ? updated : l))
      );
    } catch (err) {
      if (err instanceof UnauthorizedError) {
        router.push("/login");
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to update lead.");
    } finally {
      setUpdatingId(null);
    }
  }

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
        <button
          onClick={handleLogout}
          className="rounded-md border border-black/10 px-3 py-1.5 text-sm font-medium hover:bg-black/5 dark:border-white/10 dark:hover:bg-white/10"
        >
          Log out
        </button>
      </div>

      <div className="mt-4 flex gap-2">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => {
              setFilter(f.value);
              setLoading(true);
            }}
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              filter === f.value
                ? "bg-black text-white dark:bg-white dark:text-black"
                : "bg-black/5 dark:bg-white/10"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {error && <p className="mt-6 text-sm text-red-600">{error}</p>}
      {loading && <p className="mt-6 text-sm text-black/60 dark:text-white/60">Loading...</p>}

      {!loading && !error && leads.length === 0 && (
        <p className="mt-6 text-sm text-black/60 dark:text-white/60">No leads yet.</p>
      )}

      {!loading && leads.length > 0 && (
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
                  <td className="px-4 py-2 whitespace-nowrap">
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
                  <td className="px-4 py-2 whitespace-nowrap text-black/60 dark:text-white/60">
                    {new Date(lead.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap">
                    {lead.status === "PENDING" ? (
                      <button
                        onClick={() => markReachedOut(lead)}
                        disabled={updatingId === lead.id}
                        className="rounded-md bg-black px-3 py-1 text-xs font-medium text-white disabled:opacity-50 dark:bg-white dark:text-black"
                      >
                        {updatingId === lead.id ? "Updating..." : "Mark Reached Out"}
                      </button>
                    ) : (
                      <span className="text-xs text-black/40 dark:text-white/40">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export function StatusBadge({ status }: { status: LeadStatus }) {
  const isPending = status === "PENDING";
  return (
    <span
      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
        isPending
          ? "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300"
          : "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300"
      }`}
    >
      {isPending ? "Pending" : "Reached Out"}
    </span>
  );
}
