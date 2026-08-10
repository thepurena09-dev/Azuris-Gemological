import id from "@/i18n/locales/id";
import en from "@/i18n/locales/en";
import type { Locale } from "@/config";

export const dictionaries = { id, en } as const;

export type Dictionary = typeof id;

export const defaultLocale: Locale = "en";
