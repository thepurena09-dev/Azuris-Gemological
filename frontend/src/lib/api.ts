import { appConfig } from "@/config";

const API_BASE = appConfig.api.baseUrl; // paths below already include the /api prefix

const ACCESS = "azuris_access";
const REFRESH = "azuris_refresh";
let refreshInFlight: Promise<string | null> | null = null;

export function getToken(): string | null {
  return localStorage.getItem(ACCESS);
}
function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH);
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

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;
  try {
    const res = await fetch(`${API_BASE}/api/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) {
      clearTokens();
      return null;
    }
    const json = await res.json().catch(() => null);
    const data = json && typeof json === "object" && "success" in json
      ? (json.success ? json.data : null)
      : json;
    if (!data?.access_token || !data?.refresh_token) {
      clearTokens();
      return null;
    }
    setTokens(data.access_token, data.refresh_token);
    return data.access_token as string;
  } catch {
    clearTokens();
    return null;
  }
}

export async function apiFetch(path: string, opts: RequestInit = {}): Promise<Response> {
  const run = (token: string | null) => {
    const headers = new Headers(opts.headers || {});
    if (token) headers.set("Authorization", `Bearer ${token}`);
    if (opts.body && !(opts.body instanceof FormData) && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }
    return fetch(`${API_BASE}${path}`, { ...opts, headers });
  };

  let res = await run(getToken());
  const isAuthBootstrap = path === "/api/auth/login" || path === "/api/auth/refresh";
  if (res.status === 401 && !isAuthBootstrap && getRefreshToken()) {
    if (!refreshInFlight) {
      refreshInFlight = refreshAccessToken().finally(() => {
        refreshInFlight = null;
      });
    }
    const access = await refreshInFlight;
    if (access) res = await run(access);
  }
  return res;
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
