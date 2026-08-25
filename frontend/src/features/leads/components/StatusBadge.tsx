import type { LeadStatus } from "../types";

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
