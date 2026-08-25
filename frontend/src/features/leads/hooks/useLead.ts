"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { UnauthorizedError } from "@/lib/api/client";
import { getLead, updateLead } from "../api";
import type { Lead } from "../types";

export function useLead(leadId: string) {
  const router = useRouter();
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
      .catch((requestError: unknown) => {
        if (cancelled) return;
        if (requestError instanceof UnauthorizedError) {
          router.push("/login");
          return;
        }
        setError(
          requestError instanceof Error
            ? requestError.message
            : "Failed to load lead."
        );
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [leadId, router]);

  async function markReachedOut() {
    if (!lead) return;
    setSaving(true);
    setError(null);
    try {
      setLead(await updateLead(lead.id, { status: "REACHED_OUT" }));
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
      setSaving(false);
    }
  }

  return { lead, loading, error, saving, markReachedOut };
}
