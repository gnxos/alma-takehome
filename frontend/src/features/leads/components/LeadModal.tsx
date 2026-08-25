"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { CloseIcon, DownloadIcon } from "@/components/ui/icons";
import { redirectToLogin } from "@/features/auth/api";
import { UnauthorizedError } from "@/lib/api/client";
import { getLead, resumeUrl, updateLead } from "../api";
import type { Lead } from "../types";
import { StatusBadge } from "./StatusBadge";

interface LeadModalProps {
  leadId: string;
  onClose: () => void;
  onUpdated: (lead: Lead) => void;
}

export function LeadModal({ leadId, onClose, onUpdated }: LeadModalProps) {
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
          redirectToLogin();
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
              {loading
                ? "Loading..."
                : lead
                  ? `${lead.first_name} ${lead.last_name}`
                  : "Lead"}
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
              <dd className="font-mono-alma text-mono-sm text-ink-900">
                {lead.email}
              </dd>

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
              <dd className="text-ink-900">
                {new Date(lead.created_at).toLocaleString()}
              </dd>

              <dt className="text-label-sm text-ink-400">Last updated</dt>
              <dd className="text-ink-900">
                {new Date(lead.updated_at).toLocaleString()}
              </dd>
            </dl>

            {lead.status === "PENDING" && (
              <div className="mt-6 border-t border-ink-200 pt-4">
                <Button
                  onClick={markReachedOut}
                  loading={saving}
                  fullWidth
                >
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
