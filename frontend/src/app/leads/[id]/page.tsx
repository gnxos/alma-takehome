import { LeadDetail } from "@/features/leads/components/LeadDetail";

interface LeadDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function LeadDetailPage({ params }: LeadDetailPageProps) {
  const { id } = await params;
  return <LeadDetail leadId={id} />;
}
