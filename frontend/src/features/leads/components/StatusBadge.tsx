import type { EmailDeliveryStatus, LeadStatus } from "../types";

export function StatusBadge({ status }: { status: LeadStatus }) {
  const isPending = status === "PENDING";
  return (
    <span
      className={`inline-block whitespace-nowrap rounded-pill px-2 py-0.5 text-label-sm normal-case tracking-normal ${
        isPending
          ? "bg-ochre-50 text-ochre-600"
          : "bg-sage-50 text-sage-600"
      }`}
    >
      {isPending ? "Pending" : "Reached out"}
    </span>
  );
}

export function StatusSelect({
  status,
  disabled,
  onChange,
}: {
  status: LeadStatus;
  disabled?: boolean;
  onChange: (status: LeadStatus) => void;
}) {
  const isPending = status === "PENDING";
  return (
    <select
      value={status}
      disabled={disabled}
      onChange={(event) => onChange(event.target.value as LeadStatus)}
      className={`rounded-pill border-0 px-2 py-1 text-label-sm normal-case tracking-normal disabled:opacity-50 ${
        isPending ? "bg-ochre-50 text-ochre-600" : "bg-sage-50 text-sage-600"
      }`}
    >
      <option value="PENDING">Pending</option>
      <option value="REACHED_OUT">Reached out</option>
    </select>
  );
}

const EMAIL_STATUS_STYLES: Record<EmailDeliveryStatus, string> = {
  PENDING: "bg-paper-100 text-ink-400",
  SENT: "bg-sage-50 text-sage-600",
  FAILED: "bg-brick-50 text-brick-600",
};

const EMAIL_STATUS_LABELS: Record<EmailDeliveryStatus, string> = {
  PENDING: "Sending…",
  SENT: "Sent",
  FAILED: "Failed",
};

export function EmailStatusBadge({
  label,
  status,
}: {
  label: string;
  status: EmailDeliveryStatus;
}) {
  return (
    <span className="inline-flex items-center gap-1.5 text-body-sm text-ink-700">
      {label}:
      <span
        className={`inline-block whitespace-nowrap rounded-pill px-2 py-0.5 text-label-sm normal-case tracking-normal ${EMAIL_STATUS_STYLES[status]}`}
      >
        {EMAIL_STATUS_LABELS[status]}
      </span>
    </span>
  );
}
