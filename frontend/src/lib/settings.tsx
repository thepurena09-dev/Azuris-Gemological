import * as React from "react";
import { apiJson } from "@/lib/api";

const FALLBACK_WHATSAPP = "6287812128884";

interface BusinessSettings {
  whatsapp_number: string;
  whatsapp_label: string | null;
  whatsapp_enabled: boolean;
}

interface BusinessContextValue {
  whatsappNumber: string;
  whatsappEnabled: boolean;
  whatsappHref: (message?: string) => string;
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
    return {
      whatsappNumber: number,
      whatsappEnabled: settings.whatsapp_enabled,
      whatsappHref: (message?: string) =>
        `https://wa.me/${number}${message ? `?text=${encodeURIComponent(message)}` : ""}`,
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
