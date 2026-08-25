export type LeadStatus = "PENDING" | "REACHED_OUT";

export interface Lead {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  status: LeadStatus;
  resume_filename: string;
  created_at: string;
  updated_at: string;
}

export interface LeadList {
  total: number;
  items: Lead[];
}

export interface Attorney {
  email: string;
}
