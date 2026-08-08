import * as React from "react";
import { apiJson } from "@/lib/api";

const FALLBACK_WHATSAPP = "6287812128884";

export interface Visuals {
  login_image_url: string;
  login_image_alt_id: string | null;
  login_image_alt_en: string | null;
  process_image_url: string;
  process_image_alt_id: string | null;
  process_image_alt_en: string | null;
  process_image_show: boolean;
  membership_show: boolean;
  membership_title_id: string | null;
  membership_title_en: string | null;
  membership_desc_id: string | null;
  membership_desc_en: string | null;
  membership_cta_id: string | null;
  membership_cta_en: string | null;
  membership_link: string;
  dashboard_bg_enabled: boolean;
  dashboard_bg_url: string;
  dashboard_bg_opacity: number;
}

interface BusinessSettings extends Partial<Visuals> {
  whatsapp_number: string;
  whatsapp_label: string | null;
  whatsapp_enabled: boolean;
}

interface BusinessContextValue {
  whatsappNumber: string;
  whatsappEnabled: boolean;
  whatsappHref: (message?: string) => string;
  visuals: Visuals | null;
  refresh: () => void;
}

const BusinessContext = React.createContext<BusinessContextValue | undefined>(undefined);

export const BusinessSettingsProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [settings, setSettings] = React.useState<BusinessSettings>({
    whatsapp_number: FALLBACK_WHATSAPP,
    whatsapp_label: null,
    whatsapp_enabled: true,
  });

  const load = React.useCallback(() => {
    apiJson<BusinessSettings>("/api/settings/public")
      .then((s) => {
        if (s && s.whatsapp_number) setSettings(s);
      })
      .catch(() => {
        /* keep centralized fallback */
      });
  }, []);

  React.useEffect(() => {
    load();
  }, [load]);

  const value = React.useMemo<BusinessContextValue>(() => {
    const number = settings.whatsapp_number || FALLBACK_WHATSAPP;
    const visuals =
      settings.login_image_url !== undefined ? (settings as Visuals) : null;
    return {
      whatsappNumber: number,
      whatsappEnabled: settings.whatsapp_enabled,
      whatsappHref: (message?: string) =>
        `https://wa.me/${number}${message ? `?text=${encodeURIComponent(message)}` : ""}`,
      visuals,
      refresh: load,
    };
  }, [settings, load]);

  return <BusinessContext.Provider value={value}>{children}</BusinessContext.Provider>;
};

export function useBusiness(): BusinessContextValue {
  const ctx = React.useContext(BusinessContext);
  if (!ctx) throw new Error("useBusiness must be used within BusinessSettingsProvider");
  return ctx;
}
