import * as React from "react";
import { CircleNotch, WhatsappLogo } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiFetch, apiJson } from "@/lib/api";
import { useBusiness } from "@/lib/settings";

export default function SettingsPage() {
  const { t } = useLanguage();
  const { refresh } = useBusiness();
  const [number, setNumber] = React.useState("");
  const [label, setLabel] = React.useState("");
  const [enabled, setEnabled] = React.useState(true);
  const [msg, setMsg] = React.useState<string | null>(null);
  const [err, setErr] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);

  React.useEffect(() => {
    apiJson<any>("/api/admin/settings").then((s) => {
      setNumber(s.whatsapp_number || "");
      setLabel(s.whatsapp_label || "");
      setEnabled(!!s.whatsapp_enabled);
    });
  }, []);

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg(null);
    setErr(null);
    setBusy(true);
    try {
      const res = await apiFetch("/api/admin/settings", {
        method: "PUT",
        body: JSON.stringify({ whatsapp_number: number, whatsapp_label: label, whatsapp_enabled: enabled }),
      });
      if (!res.ok) {
        setErr(t("adminSettings.invalid"));
        return;
      }
      const data = await res.json();
      setNumber(data.whatsapp_number);
      setMsg(t("adminSettings.saved"));
      refresh();
    } finally {
      setBusy(false);
    }
  };

  return (
    <section data-testid={TEST_IDS.page.adminSettings} className="px-6 py-10 md:px-10 md:py-12">
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">{t("admin.title")}</p>
      <h1 className="mt-3 font-serif text-4xl font-normal tracking-tight">{t("adminSettings.title")}</h1>
      <p className="mt-3 max-w-2xl text-sm text-muted-foreground">{t("adminSettings.subtitle")}</p>

      <form onSubmit={save} className="mt-8 max-w-lg rounded-2xl border border-border bg-card p-7">
        <div>
          <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">
            {t("adminSettings.whatsapp")}
          </label>
          <div className="flex items-center gap-3 rounded-lg border border-border bg-background px-4 py-3 focus-within:border-gold">
            <WhatsappLogo size={18} weight="fill" className="text-gold" />
            <input
              data-testid="settings-whatsapp"
              value={number}
              onChange={(e) => setNumber(e.target.value)}
              className="w-full bg-transparent text-sm outline-none"
            />
          </div>
          <p className="mt-2 text-xs text-muted-foreground/80">{t("adminSettings.hint")}</p>
        </div>

        <div className="mt-4">
          <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">
            {t("adminSettings.label")}
          </label>
          <input
            data-testid="settings-label"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm outline-none focus:border-gold"
          />
        </div>

        <label className="mt-4 flex items-center gap-2 text-sm text-foreground">
          <input
            data-testid="settings-enabled"
            type="checkbox"
            checked={enabled}
            onChange={(e) => setEnabled(e.target.checked)}
          />
          {t("adminSettings.enabled")}
        </label>

        <div className="mt-6 flex items-center gap-4">
          <button
            type="submit"
            data-testid="settings-save"
            disabled={busy}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-70"
          >
            {busy ? <CircleNotch size={14} className="animate-spin" /> : null}
            {t("adminSettings.save")}
          </button>
          {msg && <span className="text-sm text-emerald-600">{msg}</span>}
          {err && <span className="text-sm text-red-600">{err}</span>}
        </div>
      </form>
    </section>
  );
}
