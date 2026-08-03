/**
 * Azuris Gemological — centralized frontend configuration (Sprint 2).
 *
 * Single source of truth for environment-driven settings. Only variables
 * prefixed with REACT_APP_ are available in the browser (Create React App).
 * No secrets live here.
 */

export type Locale = "id" | "en";
export type Environment = "development" | "production";

function readBackendUrl(): string {
  const url = process.env.REACT_APP_BACKEND_URL;
  if (!url) {
    // Fail loudly in development so misconfiguration is obvious.
    // eslint-disable-next-line no-console
    console.error(
      "[config] REACT_APP_BACKEND_URL is not set. API calls will fail."
    );
    return "";
  }
  return url.replace(/\/+$/, ""); // strip trailing slashes
}

const backendUrl = readBackendUrl();

export const appConfig = {
  name: "Azuris Gemological",
  version: "0.1.0",
  sprint: 2,
  environment: (process.env.NODE_ENV === "production"
    ? "production"
    : "development") as Environment,

  // Internationalization
  defaultLocale: "id" as Locale,
  supportedLocales: ["id", "en"] as Locale[],

  // API
  api: {
    baseUrl: backendUrl,
    prefix: "/api",
    timeoutMs: 30_000,
  },
} as const;

/** Fully-qualified API base, e.g. https://host/api */
export const apiBase = `${appConfig.api.baseUrl}${appConfig.api.prefix}`;

/** Build a full API URL from a path (leading slash optional). */
export function apiUrl(path: string): string {
  const clean = path.startsWith("/") ? path : `/${path}`;
  return `${apiBase}${clean}`;
}
