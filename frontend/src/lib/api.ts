import type { Attorney, Lead, LeadList, LeadStatus } from "./types";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class UnauthorizedError extends Error {
  constructor() {
    super("Not authenticated");
    this.name = "UnauthorizedError";
  }
}

async function handle<T>(response: Response): Promise<T> {
  if (response.status === 401) {
    throw new UnauthorizedError();
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    let detail: string;
    if (typeof body?.detail === "string") {
      detail = body.detail;
    } else if (Array.isArray(body?.detail) && body.detail.length > 0) {
      detail = body.detail
        .map((item: { msg?: string }) => {
          if (typeof item === "string") return item;
          if (item && typeof item.msg === "string") {
            return item.msg.replace(/^Value error,\s*/i, "");
          }
          return JSON.stringify(item);
        })
        .join("; ");
    } else {
      detail = JSON.stringify(body?.detail ?? response.statusText);
    }
    throw new Error(detail);
  }
  return response.json();
}

export async function createLead(form: {
  first_name: string;
  last_name: string;
  email: string;
  resume: File;
}): Promise<Lead> {
  const formData = new FormData();
  formData.append("first_name", form.first_name);
  formData.append("last_name", form.last_name);
  formData.append("email", form.email);
  formData.append("resume", form.resume);

  const response = await fetch(`${API_URL}/api/leads`, {
    method: "POST",
    body: formData,
  });
  return handle<Lead>(response);
}

export async function listLeads(status?: LeadStatus): Promise<LeadList> {
  const url = new URL(`${API_URL}/api/leads`);
  if (status) url.searchParams.set("status_filter", status);

  const response = await fetch(url, { cache: "no-store", credentials: "include" });
  return handle<LeadList>(response);
}

export async function getLead(id: string): Promise<Lead> {
  const response = await fetch(`${API_URL}/api/leads/${id}`, {
    cache: "no-store",
    credentials: "include",
  });
  return handle<Lead>(response);
}

export async function updateLead(
  id: string,
  changes: Partial<Pick<Lead, "first_name" | "last_name" | "email" | "status">>
): Promise<Lead> {
  const response = await fetch(`${API_URL}/api/leads/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(changes),
  });
  return handle<Lead>(response);
}

export function resumeUrl(id: string): string {
  return `${API_URL}/api/leads/${id}/resume`;
}

export async function login(email: string, password: string): Promise<Attorney> {
  const response = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password }),
  });
  return handle<Attorney>(response);
}

export async function logout(): Promise<void> {
  await fetch(`${API_URL}/logout`, { method: "POST", credentials: "include" });
}

export async function getMe(): Promise<Attorney> {
  const response = await fetch(`${API_URL}/auth/me`, {
    cache: "no-store",
    credentials: "include",
  });
  return handle<Attorney>(response);
}
