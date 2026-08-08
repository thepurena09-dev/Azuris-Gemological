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

export async function apiFetch(path: string, opts: RequestInit = {}): Promise<Response> {
  const headers = new Headers(opts.headers || {});
  const tok = getToken();
  if (tok) headers.set("Authorization", `Bearer ${tok}`);
  if (opts.body && !(opts.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  return fetch(`${API_BASE}${path}`, { ...opts, headers });
}

export async function apiJson<T = any>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await apiFetch(path, opts);
  if (!res.ok) throw new Error(String(res.status));
  return (await res.json()) as T;
}
