"use client";

import { useEffect, useRef, useState } from "react";

import {
  getCurrentAttorney,
  redirectToLogin,
} from "@/features/auth/api";
import { UnauthorizedError } from "@/lib/api/client";
import { listLeads, listLeadsByEmail, updateLead } from "../api";
import type { Lead } from "../types";

export function useLeads() {
  const [attorneyEmail, setAttorneyEmail] = useState<string | null>(null);
  const [allLeads, setAllLeads] = useState<Lead[]>([]);
  const [emailLeads, setEmailLeads] = useState<Lead[]>([]);
  const [selectedEmail, setSelectedEmail] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingEmail, setLoadingEmail] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const emailRequestId = useRef(0);

  useEffect(() => {
    getCurrentAttorney()
      .then((attorney) => setAttorneyEmail(attorney.email))
      .catch(() => {});
  }, []);

  useEffect(() => {
    let cancelled = false;
    listLeads()
      .then((data) => {
        if (!cancelled) setAllLeads(data.items);
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
    setAllLeads((current) =>
      current.map((lead) => (lead.id === updated.id ? updated : lead))
    );
    setEmailLeads((current) => {
      const updatedLeads = current.map((lead) =>
        lead.id === updated.id ? updated : lead
      );
      if (!selectedEmail) return updatedLeads;
      return updatedLeads.filter(
        (lead) => lead.email.toLowerCase() === selectedEmail.toLowerCase()
      );
    });
  }

  async function filterByEmail(email: string) {
    const requestId = ++emailRequestId.current;
    setSelectedEmail(email);
    setEmailLeads([]);
    setLoadingEmail(true);
    setError(null);

    try {
      const data = await listLeadsByEmail(email);
      if (requestId === emailRequestId.current) {
        setEmailLeads(data.items);
      }
    } catch (requestError) {
      if (requestId !== emailRequestId.current) return;
      if (requestError instanceof UnauthorizedError) {
        redirectToLogin();
        return;
      }
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Couldn't load tickets for this email."
      );
    } finally {
      if (requestId === emailRequestId.current) {
        setLoadingEmail(false);
      }
    }
  }

  function clearEmailFilter() {
    emailRequestId.current += 1;
    setSelectedEmail(null);
    setEmailLeads([]);
    setLoadingEmail(false);
    setError(null);
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
    leads: selectedEmail ? emailLeads : allLeads,
    selectedEmail,
    loading,
    loadingEmail,
    error,
    updatingId,
    applyUpdate,
    filterByEmail,
    clearEmailFilter,
    markReachedOut,
  };
}
