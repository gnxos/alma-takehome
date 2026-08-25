import { apiRequest } from "@/lib/api/client";
import type { Attorney } from "./types";

export function login(email: string, password: string): Promise<Attorney> {
  return apiRequest<Attorney>("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password }),
  });
}

export async function logout(): Promise<void> {
  await apiRequest<{ detail: string }>("/logout", {
    method: "POST",
    credentials: "include",
  });
}

export function getCurrentAttorney(): Promise<Attorney> {
  return apiRequest<Attorney>("/auth/me", {
    cache: "no-store",
    credentials: "include",
  });
}

export function redirectToLogin(): void {
  window.location.replace("/login");
}
