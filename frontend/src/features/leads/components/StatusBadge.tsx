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
