/**
 * Azuris Gemological — application configuration.
 * Sprint 1: base config + default locale only.
 * The full environment/config layer arrives in Sprint 2.
 */

export type Locale = "id" | "en";

export const appConfig = {
  name: "Azuris Gemological",
  version: "0.1.0",
  sprint: 1,
  defaultLocale: "id" as Locale,
  supportedLocales: ["id", "en"] as Locale[],
  api: {
    baseUrl: process.env.REACT_APP_BACKEND_URL ?? "",
    prefix: "/api",
  },
} as const;

export const apiBase = `${appConfig.api.baseUrl}${appConfig.api.prefix}`;
