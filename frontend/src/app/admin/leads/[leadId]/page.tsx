import { redirect } from "next/navigation";

export default async function AdminLeadPage({
  params,
}: {
  params: Promise<{ leadId: string }>;
}) {
  const { leadId } = await params;
  redirect(`/leads?ref=${encodeURIComponent(leadId)}`);
}
