import type { LeadStatus } from "../types";

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
