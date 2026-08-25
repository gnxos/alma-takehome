"use client";

import { useEffect, useState } from "react";

import {
  getCurrentAttorney,
  redirectToLogin,
} from "@/features/auth/api";
import { UnauthorizedError } from "@/lib/api/client";
import { listLeads, updateLead } from "../api";
import type { Lead } from "../types";

export function useLeads() {
  const [attorneyEmail, setAttorneyEmail] = useState<string | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  useEffect(() => {
    getCurrentAttorney()
      .then((attorney) => setAttorneyEmail(attorney.email))
      .catch(() => {});
  }, []);

  useEffect(() => {
    let cancelled = false;
    listLeads()
      .then((data) => {
        if (!cancelled) setLeads(data.items);
      })
      .catch((requestError: unknown) => {
        if (cancelled) return;
        if (requestError instanceof UnauthorizedError) {
          redirectToLogin();
          return;
        }
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Couldn't load leads."
        );
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  function applyUpdate(updated: Lead) {
    setLeads((current) =>
      current.map((lead) => (lead.id === updated.id ? updated : lead))
    );
  }

  async function markReachedOut(lead: Lead) {
    setUpdatingId(lead.id);
    setError(null);
    try {
      applyUpdate(await updateLead(lead.id, { status: "REACHED_OUT" }));
    } catch (requestError) {
      if (requestError instanceof UnauthorizedError) {
        redirectToLogin();
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
    attorneyEmail,
    leads,
    loading,
    error,
    updatingId,
    applyUpdate,
    markReachedOut,
  };
}
