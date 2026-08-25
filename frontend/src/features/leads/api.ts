import { API_URL, apiRequest } from "@/lib/api/client";
import type {
  CreateLeadInput,
  Lead,
  LeadCreateResult,
  LeadList,
  LeadStatus,
  LeadUpdate,
} from "./types";

export function createLead(input: CreateLeadInput): Promise<LeadCreateResult> {
  const formData = new FormData();
  formData.append("first_name", input.first_name);
  formData.append("last_name", input.last_name);
  formData.append("email", input.email);
  formData.append("resume", input.resume);

  return apiRequest<LeadCreateResult>("/api/leads", {
    method: "POST",
    body: formData,
  });
}

export function listLeads(status?: LeadStatus): Promise<LeadList> {
  const query = status
    ? `?${new URLSearchParams({ status_filter: status }).toString()}`
    : "";
  return apiRequest<LeadList>(`/api/leads${query}`, {
    cache: "no-store",
    credentials: "include",
  });
}

export function listLeadsByEmail(email: string): Promise<LeadList> {
  const query = new URLSearchParams({ email }).toString();
  return apiRequest<LeadList>(`/api/leads/by-email?${query}`, {
    cache: "no-store",
    credentials: "include",
  });
}

export function getLead(id: string): Promise<Lead> {
  return apiRequest<Lead>(`/api/leads/${id}`, {
    cache: "no-store",
    credentials: "include",
  });
}

export function updateLead(id: string, changes: LeadUpdate): Promise<Lead> {
  return apiRequest<Lead>(`/api/leads/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(changes),
  });
}

export function resumeUrl(id: string): string {
  return `${API_URL}/api/leads/${id}/resume`;
}
