import * as React from "react";
import { CircleNotch, Image as ImageIcon, IdentificationCard, SignIn } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiJson } from "@/lib/api";
import { useBusiness } from "@/lib/settings";
import { MembershipCardVisual } from "@/components/membership/MembershipCardVisual";

type Visuals = Record<string, any>;

function Field({
  label,
  value,
  onChange,
  testid,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  testid: string;
  placeholder?: string;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">
        {label}
      </label>
      <input
        data-testid={testid}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-gold"
      />
    </div>
  );
}

function SectionCard({
  icon,
  title,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-6">
      <div className="mb-5 flex items-center gap-3">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/5 text-primary">
          {icon}
        </span>
        <h2 className="text-[0.66rem] uppercase tracking-[0.22em] text-gold">{title}</h2>
      </div>
      {children}
    </div>
  );
}

export default function VisualsPage() {
  const { t } = useLanguage();
  const { refresh } = useBusiness();
  const [v, setV] = React.useState<Visuals | null>(null);
  const [busy, setBusy] = React.useState(false);
  const [msg, setMsg] = React.useState<string | null>(null);
  const [readOnly, setReadOnly] = React.useState(false);

  React.useEffect(() => {
    apiJson<Visuals>("/api/admin/settings/visuals")
      .then(setV)
      .catch(() => setReadOnly(true));
  }, []);

  const set = (k: string, val: any) => setV((s) => ({ ...(s || {}), [k]: val }));

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!v) return;
    setBusy(true);
    setMsg(null);
    try {
      const saved = await apiJson<Visuals>("/api/admin/settings/visuals", {
        method: "PUT",
        body: JSON.stringify(v),
      });
      setV(saved);
      setMsg(t("adminVisuals.saved"));
      refresh();
    } catch {
      setReadOnly(true);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section data-testid={TEST_IDS.page.adminVisuals} className="px-6 py-10 md:px-10 md:py-12">
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">
        {t("admin.title")}
      </p>
      <h1 className="mt-3 font-serif text-4xl font-normal tracking-tight">
        {t("adminVisuals.title")}
      </h1>
      <p className="mt-3 max-w-2xl text-sm text-muted-foreground">{t("adminVisuals.subtitle")}</p>

      {readOnly && (
        <p className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
          {t("adminVisuals.readOnly")}
        </p>
      )}

      {!v ? (
        <div className="mt-10 flex items-center gap-3 text-muted-foreground">
          <CircleNotch size={18} className="animate-spin" /> …
        </div>
      ) : (
        <form onSubmit={save} className="mt-8 space-y-6">
          {/* Login image */}
          <SectionCard icon={<SignIn size={18} />} title={t("adminVisuals.loginSection")}>
            <div className="grid gap-5 lg:grid-cols-[1fr_260px]">
              <div className="space-y-4">
                <Field label={t("adminVisuals.imageUrl")} value={v.login_image_url || ""} onChange={(x) => set("login_image_url", x)} testid="visuals-login-url" />
                <div className="grid gap-4 sm:grid-cols-2">
                  <Field label={t("adminVisuals.altId")} value={v.login_image_alt_id || ""} onChange={(x) => set("login_image_alt_id", x)} testid="visuals-login-alt-id" />
                  <Field label={t("adminVisuals.altEn")} value={v.login_image_alt_en || ""} onChange={(x) => set("login_image_alt_en", x)} testid="visuals-login-alt-en" />
                </div>
              </div>
              <div className="overflow-hidden rounded-xl border border-border bg-secondary">
                {v.login_image_url ? (
                  <img data-testid="visuals-login-preview" src={v.login_image_url} alt="preview" className="aspect-[4/3] h-full w-full object-cover" />
                ) : null}
              </div>
            </div>
          </SectionCard>

          {/* Process image */}
          <SectionCard icon={<ImageIcon size={18} />} title={t("adminVisuals.processSection")}>
            <label className="mb-4 flex items-center gap-2 text-sm text-foreground">
              <input data-testid="visuals-process-show" type="checkbox" checked={v.process_image_show !== false} onChange={(e) => set("process_image_show", e.target.checked)} />
              {t("adminVisuals.show")}
            </label>
            <div className="grid gap-5 lg:grid-cols-[1fr_260px]">
              <div className="space-y-4">
                <Field label={t("adminVisuals.imageUrl")} value={v.process_image_url || ""} onChange={(x) => set("process_image_url", x)} testid="visuals-process-url" />
                <div className="grid gap-4 sm:grid-cols-2">
                  <Field label={t("adminVisuals.altId")} value={v.process_image_alt_id || ""} onChange={(x) => set("process_image_alt_id", x)} testid="visuals-process-alt-id" />
                  <Field label={t("adminVisuals.altEn")} value={v.process_image_alt_en || ""} onChange={(x) => set("process_image_alt_en", x)} testid="visuals-process-alt-en" />
                </div>
              </div>
              <div className="overflow-hidden rounded-xl border border-border bg-secondary">
                {v.process_image_url ? (
                  <img data-testid="visuals-process-preview" src={v.process_image_url} alt="preview" className="aspect-[4/3] h-full w-full object-cover" />
                ) : null}
              </div>
            </div>
          </SectionCard>

          {/* Homepage membership */}
          <SectionCard icon={<IdentificationCard size={18} />} title={t("adminVisuals.membershipSection")}>
            <label className="mb-4 flex items-center gap-2 text-sm text-foreground">
              <input data-testid="visuals-membership-show" type="checkbox" checked={v.membership_show !== false} onChange={(e) => set("membership_show", e.target.checked)} />
              {t("adminVisuals.show")}
            </label>
            <div className="grid gap-5 lg:grid-cols-[1fr_260px]">
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label={t("adminVisuals.titleId")} value={v.membership_title_id || ""} onChange={(x) => set("membership_title_id", x)} testid="visuals-mem-title-id" />
                <Field label={t("adminVisuals.titleEn")} value={v.membership_title_en || ""} onChange={(x) => set("membership_title_en", x)} testid="visuals-mem-title-en" />
                <Field label={t("adminVisuals.descId")} value={v.membership_desc_id || ""} onChange={(x) => set("membership_desc_id", x)} testid="visuals-mem-desc-id" />
                <Field label={t("adminVisuals.descEn")} value={v.membership_desc_en || ""} onChange={(x) => set("membership_desc_en", x)} testid="visuals-mem-desc-en" />
                <Field label={t("adminVisuals.ctaId")} value={v.membership_cta_id || ""} onChange={(x) => set("membership_cta_id", x)} testid="visuals-mem-cta-id" />
                <Field label={t("adminVisuals.ctaEn")} value={v.membership_cta_en || ""} onChange={(x) => set("membership_cta_en", x)} testid="visuals-mem-cta-en" />
                <Field label={t("adminVisuals.link")} value={v.membership_link || ""} onChange={(x) => set("membership_link", x)} testid="visuals-mem-link" />
              </div>
              <div>
                <MembershipCardVisual side="front" cardNumber="AZR-MEM-••••••-26" memberName="Andi Pra****" memberSince="2026" status="active" />
              </div>
            </div>
          </SectionCard>

          <div className="flex items-center gap-4">
            <button
              type="submit"
              data-testid="visuals-save"
              disabled={busy || readOnly}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-60"
            >
              {busy ? <CircleNotch size={14} className="animate-spin" /> : null}
              {t("adminVisuals.save")}
            </button>
            {msg && <span className="text-sm text-emerald-600">{msg}</span>}
          </div>
        </form>
      )}
    </section>
  );
}
