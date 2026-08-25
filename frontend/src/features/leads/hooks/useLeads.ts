"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { UnauthorizedError } from "@/lib/api/client";
import { listLeads, updateLead } from "../api";
import type { Lead, LeadFilter } from "../types";

export function useLeads() {
  const router = useRouter();
  const [filter, setFilter] = useState<LeadFilter>("ALL");
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    listLeads(filter === "ALL" ? undefined : filter)
      .then((data) => {
        if (!cancelled) setLeads(data.items);
      })
      .catch((requestError: unknown) => {
        if (cancelled) return;
        if (requestError instanceof UnauthorizedError) {
          router.push("/login");
          return;
        }
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Failed to load leads."
        );
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [filter, router]);

  function selectFilter(nextFilter: LeadFilter) {
    setLoading(true);
    setError(null);
    setFilter(nextFilter);
  }

  async function markReachedOut(lead: Lead) {
    setUpdatingId(lead.id);
    setError(null);
    try {
      const updated = await updateLead(lead.id, { status: "REACHED_OUT" });
      setLeads((current) =>
        filter === "PENDING"
          ? current.filter((item) => item.id !== lead.id)
          : current.map((item) => (item.id === lead.id ? updated : item))
      );
    } catch (requestError) {
      if (requestError instanceof UnauthorizedError) {
        router.push("/login");
        return;
      }
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to update lead."
      );
    } finally {
      setUpdatingId(null);
    }
  }

  return {
    filter,
    leads,
    loading,
    error,
    updatingId,
    selectFilter,
    markReachedOut,
  };
}
