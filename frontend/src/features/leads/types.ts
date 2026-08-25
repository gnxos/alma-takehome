export type LeadStatus = "PENDING" | "REACHED_OUT";
export type LeadFilter = LeadStatus | "ALL";
export type EmailDeliveryStatus = "PENDING" | "SENT" | "FAILED";

export interface Lead {
  id: string;
  reference_number: string;
  first_name: string;
  last_name: string;
  email: string;
  status: LeadStatus;
  resume_filename: string;
  phone?: string | null;
  message?: string | null;
  prospect_email_status: EmailDeliveryStatus;
  attorney_email_status: EmailDeliveryStatus;
  resolved_by?: string | null;
  resolved_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface LeadCreateResult extends Lead {
  already_exists: boolean;
}

export interface LeadList {
  total: number;
  items: Lead[];
}

export interface CreateLeadInput {
  first_name: string;
  last_name: string;
  email: string;
  resume: File;
  phone?: string;
  message?: string;
}

export type LeadUpdate = Partial<
  Pick<
    Lead,
    "first_name" | "last_name" | "email" | "status" | "phone" | "message"
  >
>;
