export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class UnauthorizedError extends Error {
  constructor() {
    super("Not authenticated");
    this.name = "UnauthorizedError";
  }
}

export async function apiRequest<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, options);
  return parseResponse<T>(response);
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 401) {
    throw new UnauthorizedError();
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(extractErrorDetail(body?.detail, response.statusText));
  }

  return response.json() as Promise<T>;
}

function extractErrorDetail(detail: unknown, fallback: string): string {
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((item: unknown) => {
        if (typeof item === "string") return item;
        if (hasMessage(item)) {
          return item.msg.replace(/^Value error,\s*/i, "");
        }
        return JSON.stringify(item);
      })
      .join("; ");
  }

  return JSON.stringify(detail ?? fallback);
}

function hasMessage(value: unknown): value is { msg: string } {
  return (
    typeof value === "object" &&
    value !== null &&
    "msg" in value &&
    typeof value.msg === "string"
  );
}
