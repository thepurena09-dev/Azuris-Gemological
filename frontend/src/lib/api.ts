import { appConfig } from "@/config";

const API_BASE = appConfig.api.baseUrl; // paths below already include the /api prefix

const ACCESS = "azuris_access";
const REFRESH = "azuris_refresh";

export function getToken(): string | null {
  return localStorage.getItem(ACCESS);
}
export function setTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS, access);
  localStorage.setItem(REFRESH, refresh);
}
export function clearTokens(): void {
  localStorage.removeItem(ACCESS);
  localStorage.removeItem(REFRESH);
}

/** Resolve a stored image reference to a loadable URL (absolute passthrough;
 * relative `/api/media/..` gets the backend base prefixed). */
export function mediaUrl(url?: string | null): string {
  if (!url) return "";
  return url.startsWith("http") ? url : `${API_BASE}${url}`;
}

export async function apiFetch(path: string, opts: RequestInit = {}): Promise<Response> {
  const headers = new Headers(opts.headers || {});
  const tok = getToken();
  if (tok) headers.set("Authorization", `Bearer ${tok}`);
  if (opts.body && !(opts.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  return fetch(`${API_BASE}${path}`, { ...opts, headers });
}

/** Standardized API error carrying the backend's stable error code (Sprint 8). */
export class ApiError extends Error {
  code: string;
  status: number;
  details?: any[];
  constructor(code: string, message: string, status: number, details?: any[]) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

/**
 * Read + unwrap the Sprint 8 response envelope from a fetch Response.
 * - Success envelope `{success:true,data}`  -> returns `data`.
 * - Error envelope   `{success:false,error}` -> throws `ApiError`.
 * - Legacy/non-enveloped JSON (e.g. /api/health) -> returned as-is.
 */
export async function unwrap<T = any>(res: Response): Promise<T> {
  const json = await res.json().catch(() => null);
  if (json && typeof json === "object" && "success" in json) {
    if (json.success) return json.data as T;
    const err = json.error || {};
    throw new ApiError(err.code || "ERROR", err.message || "Request failed", res.status, err.details);
  }
  if (!res.ok) throw new ApiError("ERROR", String(res.status), res.status);
  return json as T;
}

export async function apiJson<T = any>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await apiFetch(path, opts);
  return unwrap<T>(res);
}
