"use client";

import { useEffect, useState } from "react";

import { CloseIcon, DownloadIcon } from "@/components/ui/icons";
import { redirectToLogin } from "@/features/auth/api";
import { UnauthorizedError } from "@/lib/api/client";
import { listLeadsByEmail, resumeUrl, updateLead } from "../api";
import type { Lead, LeadStatus } from "../types";
import { StatusSelect } from "./StatusBadge";

interface EmailTicketsDrawerProps {
  email: string;
  onClose: () => void;
  onUpdated: (lead: Lead) => void;
}

export function EmailTicketsDrawer({
  email,
  onClose,
  onUpdated,
}: EmailTicketsDrawerProps) {
  const [tickets, setTickets] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const frame = requestAnimationFrame(() => setVisible(true));
    return () => cancelAnimationFrame(frame);
  }, []);

  useEffect(() => {
    let cancelled = false;

    listLeadsByEmail(email)
      .then((data) => {
        if (!cancelled) setTickets(data.items);
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
            : "Failed to load tickets for this email."
        );
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [email]);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  async function changeStatus(ticket: Lead, newStatus: LeadStatus) {
    if (newStatus === ticket.status) return;
    setSavingId(ticket.id);
    setError(null);
    try {
      const updated = await updateLead(ticket.id, { status: newStatus });
      setTickets((current) =>
        current.map((item) => (item.id === updated.id ? updated : item))
      );
      onUpdated(updated);
    } catch (requestError) {
      if (requestError instanceof UnauthorizedError) {
        redirectToLogin();
        return;
      }
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Failed to update ticket."
      );
    } finally {
      setSavingId(null);
    }
  }

  return (
    <div
      className={`fixed inset-0 z-50 bg-ink-900/40 transition-opacity motion-reduce:transition-none ${
        visible ? "opacity-100" : "opacity-0"
      }`}
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="email-tickets-title"
        onClick={(event) => event.stopPropagation()}
        className={`fixed inset-y-0 right-0 flex w-full max-w-[min(560px,100vw)] flex-col overflow-y-auto border-l border-ink-200 bg-paper-0 p-6 shadow-modal transition-transform duration-200 ease-out motion-reduce:transition-none ${
          visible ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <p className="text-label-sm text-ink-400">Tickets for</p>
            <h2
              id="email-tickets-title"
              className="mt-1 break-all font-mono-alma text-heading-md text-ink-900"
            >
              {email}
            </h2>
            {!loading && !error && (
              <p className="mt-1 text-body-sm text-ink-400">
                {tickets.length} {tickets.length === 1 ? "ticket" : "tickets"}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className="shrink-0 rounded-input p-1 text-ink-400 hover:bg-paper-100"
          >
            <CloseIcon className="size-5" />
          </button>
        </div>

        {loading && <TicketsSkeleton />}

        {!loading && !error && tickets.length === 0 && (
          <p className="mt-8 text-body-md text-ink-700">
            No tickets found for this email.
          </p>
        )}

        {!loading && tickets.length > 0 && (
          <div className="mt-6 flex flex-col gap-4">
            {tickets.map((ticket) => (
              <article
                key={ticket.id}
                className="rounded-card border border-paper-100 bg-paper-50 p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="font-mono-alma text-mono-sm text-brass-500">
                      {ticket.reference_number}
                    </p>
                    <h3 className="mt-1 text-heading-md text-ink-900">
                      {ticket.first_name} {ticket.last_name}
                    </h3>
                  </div>
                  <StatusSelect
                    status={ticket.status}
                    disabled={savingId === ticket.id}
                    onChange={(status) => changeStatus(ticket, status)}
                  />
                </div>

                <dl className="mt-4 grid grid-cols-[auto_1fr] gap-x-4 gap-y-3 text-body-sm">
                  <dt className="text-label-sm text-ink-400">Resume / CV</dt>
                  <dd className="min-w-0">
                    <a
                      href={resumeUrl(ticket.id)}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex max-w-full items-center gap-1.5 text-ink-900 underline"
                      title="Download resume"
                    >
                      <span className="truncate">{ticket.resume_filename}</span>
                      <DownloadIcon className="size-3.5 shrink-0 text-ink-400" />
                    </a>
                  </dd>

                  {ticket.resolved_by && (
                    <>
                      <dt className="text-label-sm text-ink-400">Resolved by</dt>
                      <dd className="font-mono-alma text-mono-sm font-semibold text-navy-700">
                        {ticket.resolved_by}
                      </dd>
                    </>
                  )}

                  {ticket.resolved_at && (
                    <>
                      <dt className="text-label-sm text-ink-400">Resolved at</dt>
                      <dd className="text-ink-900">
                        {new Date(ticket.resolved_at).toLocaleString()}
                      </dd>
                    </>
                  )}

                  <dt className="text-label-sm text-ink-400">Submitted</dt>
                  <dd className="text-ink-900">
                    {new Date(ticket.created_at).toLocaleString()}
                  </dd>

                  <dt className="text-label-sm text-ink-400">Last updated</dt>
                  <dd className="text-ink-900">
                    {new Date(ticket.updated_at).toLocaleString()}
                  </dd>
                </dl>

                {savingId === ticket.id && (
                  <p className="mt-3 text-body-sm text-ink-400">Updating...</p>
                )}
              </article>
            ))}
          </div>
        )}

        {error && (
          <p className="mt-6 rounded-input bg-brick-50 px-4 py-3 text-body-sm text-brick-600">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}

function TicketsSkeleton() {
  return (
    <div className="mt-6 flex animate-pulse flex-col gap-4">
      {Array.from({ length: 3 }).map((_, index) => (
        <div
          key={index}
          className="rounded-card border border-paper-100 bg-paper-50 p-4"
        >
          <div className="h-3 w-28 rounded-input bg-paper-100" />
          <div className="mt-3 h-5 w-40 rounded-input bg-paper-100" />
          <div className="mt-5 h-3 w-full rounded-input bg-paper-100" />
          <div className="mt-3 h-3 w-3/4 rounded-input bg-paper-100" />
        </div>
      ))}
    </div>
  );
}
