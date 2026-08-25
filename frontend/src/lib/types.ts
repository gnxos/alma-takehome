export type LeadStatus = "PENDING" | "REACHED_OUT";

export interface Lead {
  id: string;
  reference_number: string;
  first_name: string;
  last_name: string;
  email: string;
  status: LeadStatus;
  resume_filename: string;
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

export interface Attorney {
  email: string;
}
