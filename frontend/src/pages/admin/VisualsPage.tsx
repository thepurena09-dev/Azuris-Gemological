import * as React from "react";
import {
  CircleNotch,
  Image as ImageIcon,
  SignIn,
  UploadSimple,
  ImagesSquare,
  ArrowCounterClockwise,
  Gauge,
  House,
  Diamond,
  Megaphone,
  X,
} from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiJson, mediaUrl } from "@/lib/api";
import { useBusiness } from "@/lib/settings";
import { useAuth } from "@/lib/auth";

type Visuals = Record<string, any>;
interface MediaItem {
  uuid: string;
  url: string;
  alt_text_id?: string | null;
  alt_text_en?: string | null;
}

const LOGIN_DEFAULT =
  "https://images.unsplash.com/photo-1783771686998-0af6c0efec6e?crop=entropy&cs=srgb&fm=jpg&q=90&w=1400";
const PROCESS_DEFAULT =
  "https://images.unsplash.com/photo-1628058494685-6c2f796ac24a?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200";
const GEM_DEFAULT = {
  diamond:
    "https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
  ruby: "https://images.unsplash.com/photo-1705575490492-4e91fd97bbb4?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
  sapphire:
    "https://static.prod-images.emergentagent.com/jobs/0d8170c5-08d6-45ed-9937-114710780b07/images/11e5956f874718e6db198dda556242a9e59a93fb2ea1cd0b3fe0d77cc5e02724.jpeg",
  emerald:
    "https://static.prod-images.emergentagent.com/jobs/6572b450-f0e7-4d20-83da-0f44a5e44dfd/images/8138fec9a0cfedc223c4896ebd58852071928246a1875cecdb3ce5aaebe929ad.jpeg",
};
const FALLBACK =
  "data:image/svg+xml;utf8," +
  encodeURIComponent(
    "<svg xmlns='http://www.w3.org/2000/svg' width='200' height='150'><rect width='100%' height='100%' fill='%23eee'/><text x='50%' y='50%' fill='%23999' font-size='12' text-anchor='middle' dominant-baseline='middle'>image</text></svg>"
  );

function Field({
  label, value, onChange, testid, placeholder, disabled,
}: {
  label: string; value: string; onChange: (v: string) => void; testid: string;
  placeholder?: string; disabled?: boolean;
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
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-gold disabled:opacity-60"
      />
    </div>
  );
}

function SectionCard({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-border bg-card p-6">
      <div className="mb-5 flex items-center gap-3">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/5 text-primary">{icon}</span>
        <h2 className="text-[0.66rem] uppercase tracking-[0.22em] text-gold">{title}</h2>
      </div>
      {children}
    </div>
  );
}

/** Visual image control: preview + Upload + Choose-from-Media + Reset + advanced URL. */
function ImageControl({
  slug, value, defaultUrl, onChange, onUpload, onOpenPicker, disabled,
}: {
  slug: string; value: string; defaultUrl: string;
  onChange: (v: string) => void;
  onUpload: (file: File) => Promise<void>;
  onOpenPicker: () => void;
  disabled: boolean;
}) {
  const { t } = useLanguage();
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = React.useState(false);
  const [err, setErr] = React.useState<string | null>(null);

  const pick = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setErr(t("adminVisuals.invalidType"));
      return;
    }
    setErr(null);
    setUploading(true);
    try {
      await onUpload(file);
    } catch {
      setErr(t("adminVisuals.uploadFailed"));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="grid gap-5 lg:grid-cols-[240px_1fr]">
      <div className="overflow-hidden rounded-xl border border-border bg-secondary">
        <img
          data-testid={`visuals-${slug}-preview`}
          src={mediaUrl(value) || FALLBACK}
          alt="preview"
          onError={(e) => ((e.target as HTMLImageElement).src = FALLBACK)}
          className="aspect-[4/3] h-full w-full object-cover"
        />
      </div>
      <div className="space-y-3">
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          data-testid={`visuals-${slug}-file`}
          onChange={pick}
        />
        <div className="flex flex-wrap gap-2.5">
          <button
            type="button"
            data-testid={`visuals-${slug}-upload`}
            disabled={disabled || uploading}
            onClick={() => inputRef.current?.click()}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-[0.64rem] uppercase tracking-[0.16em] text-primary-foreground transition-shadow hover:shadow-lg disabled:opacity-60"
          >
            {uploading ? <CircleNotch size={14} className="animate-spin" /> : <UploadSimple size={14} />}
            {uploading ? t("adminVisuals.uploading") : t("adminVisuals.uploadBtn")}
          </button>
          <button
            type="button"
            data-testid={`visuals-${slug}-pick`}
            disabled={disabled}
            onClick={onOpenPicker}
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2.5 text-[0.64rem] uppercase tracking-[0.16em] text-foreground transition-colors hover:border-gold disabled:opacity-60"
          >
            <ImagesSquare size={14} />
            {t("adminVisuals.pickBtn")}
          </button>
          <button
            type="button"
            data-testid={`visuals-${slug}-reset`}
            disabled={disabled}
            onClick={() => onChange(defaultUrl)}
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2.5 text-[0.64rem] uppercase tracking-[0.16em] text-muted-foreground transition-colors hover:border-gold disabled:opacity-60"
          >
            <ArrowCounterClockwise size={14} />
            {t("adminVisuals.reset")}
          </button>
        </div>
        {err && <p className="text-sm text-red-600">{err}</p>}
        <Field
          label={t("adminVisuals.advancedUrl")}
          value={value || ""}
          onChange={onChange}
          testid={`visuals-${slug}-url`}
          disabled={disabled}
        />
      </div>
    </div>
  );
}

function MediaPicker({
  items, onSelect, onClose,
}: {
  items: MediaItem[]; onSelect: (url: string) => void; onClose: () => void;
}) {
  const { t } = useLanguage();
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" data-testid="visuals-media-picker">
      <div className="max-h-[80vh] w-full max-w-2xl overflow-hidden rounded-2xl border border-border bg-card shadow-2xl">
        <div className="flex items-center justify-between border-b border-border px-6 py-4">
          <h3 className="text-[0.7rem] uppercase tracking-[0.2em] text-gold">{t("adminVisuals.pickerTitle")}</h3>
          <button type="button" data-testid="visuals-picker-close" onClick={onClose} className="text-muted-foreground hover:text-foreground">
            <X size={18} />
          </button>
        </div>
        <div className="max-h-[64vh] overflow-y-auto p-6">
          {items.length === 0 ? (
            <p className="py-10 text-center text-sm text-muted-foreground">{t("adminVisuals.pickerEmpty")}</p>
          ) : (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
              {items.map((m) => (
                <button
                  key={m.uuid}
                  type="button"
                  data-testid="visuals-picker-item"
                  onClick={() => onSelect(m.url)}
                  className="group overflow-hidden rounded-xl border border-border transition-colors hover:border-gold"
                >
                  <img
                    src={mediaUrl(m.url)}
                    alt={m.alt_text_id || "media"}
                    onError={(e) => ((e.target as HTMLImageElement).src = FALLBACK)}
                    className="aspect-[4/3] w-full object-cover transition-transform group-hover:scale-105"
                  />
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/** Appearance controls (opacity + fit + blur) shared by background sections. */
function BgAppearance({
  slug, prefix, v, set, disabled,
}: {
  slug: string; prefix: string; v: Visuals; set: (k: string, val: any) => void; disabled: boolean;
}) {
  const { t } = useLanguage();
  const opacity = v[`${prefix}_opacity`] ?? 10;
  const fit = v[`${prefix}_fit`] || "cover";
  const blur = v[`${prefix}_blur`] ?? 0;
  return (
    <div className="mt-5 grid max-w-2xl gap-5 sm:grid-cols-2">
      <div>
        <label className="mb-1.5 flex items-center justify-between text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">
          <span>{t("adminVisuals.bgOpacity")}</span>
          <span data-testid={`visuals-${slug}-opacity-value`} className="font-mono text-foreground">{opacity}%</span>
        </label>
        <input
          data-testid={`visuals-${slug}-opacity`}
          type="range" min={0} max={100} step={1}
          value={opacity}
          disabled={disabled}
          onChange={(e) => set(`${prefix}_opacity`, parseInt(e.target.value, 10))}
          className="w-full accent-gold disabled:opacity-50"
        />
      </div>
      <div>
        <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">
          {t("adminVisuals.bgFit")}
        </label>
        <select
          data-testid={`visuals-${slug}-fit`}
          value={fit}
          disabled={disabled}
          onChange={(e) => set(`${prefix}_fit`, e.target.value)}
          className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-gold disabled:opacity-60"
        >
          <option value="cover">{t("adminVisuals.fitCover")}</option>
          <option value="center">{t("adminVisuals.fitCenter")}</option>
        </select>
      </div>
      <div className="sm:col-span-2">
        <label className="mb-1.5 flex items-center justify-between text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">
          <span>{t("adminVisuals.bgBlur")}</span>
          <span data-testid={`visuals-${slug}-blur-value`} className="font-mono text-foreground">{blur}px</span>
        </label>
        <input
          data-testid={`visuals-${slug}-blur`}
          type="range" min={0} max={12} step={1}
          value={blur}
          disabled={disabled}
          onChange={(e) => set(`${prefix}_blur`, parseInt(e.target.value, 10))}
          className="w-full accent-gold disabled:opacity-50"
        />
      </div>
    </div>
  );
}

export default function VisualsPage() {
  const { t } = useLanguage();
  const { refresh } = useBusiness();
  const { admin } = useAuth();
  const [v, setV] = React.useState<Visuals | null>(null);
  const [busy, setBusy] = React.useState(false);
  const [msg, setMsg] = React.useState<string | null>(null);
  const [readOnly, setReadOnly] = React.useState(false);
  const [picker, setPicker] = React.useState<{ field: string } | null>(null);
  const [media, setMedia] = React.useState<MediaItem[]>([]);

  // Presentational gate — roles with CMS_WRITE per the locked RBAC matrix.
  // Backend remains the source of truth (403 on any unauthorized mutation).
  const canWrite = ["SUPER_ADMIN", "ADMINISTRATOR", "CONTENT_MANAGER"].includes(admin?.role || "");
  React.useEffect(() => {
    if (admin && !canWrite) setReadOnly(true);
  }, [admin, canWrite]);

  React.useEffect(() => {
    apiJson<Visuals>("/api/admin/settings/visuals").then(setV).catch(() => setReadOnly(true));
  }, []);

  const set = (k: string, val: any) => setV((s) => ({ ...(s || {}), [k]: val }));

  const uploadFor = (key: string) => async (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await apiJson<{ uuid: string; url: string }>("/api/admin/settings/visuals/media", {
      method: "POST",
      body: fd,
    });
    set(key, res.url);
  };

  const openPicker = async (field: string) => {
    try {
      const data = await apiJson<{ items: MediaItem[] }>("/api/admin/settings/visuals/media");
      setMedia(data.items || []);
      setPicker({ field });
    } catch {
      setReadOnly(true);
    }
  };

  const applyPicked = (url: string) => {
    if (!picker) return;
    set(picker.field, url);
    setPicker(null);
  };

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
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">{t("admin.title")}</p>
      <h1 className="mt-3 font-serif text-4xl font-normal tracking-tight">{t("adminVisuals.title")}</h1>
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
          <SectionCard icon={<SignIn size={18} />} title={t("adminVisuals.loginSection")}>
            <ImageControl
              slug="login"
              value={v.login_image_url || ""}
              defaultUrl={LOGIN_DEFAULT}
              onChange={(x) => set("login_image_url", x)}
              onUpload={uploadFor("login_image_url")}
              onOpenPicker={() => openPicker("login_image_url")}
              disabled={readOnly}
            />
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <Field label={t("adminVisuals.altId")} value={v.login_image_alt_id || ""} onChange={(x) => set("login_image_alt_id", x)} testid="visuals-login-alt-id" disabled={readOnly} />
              <Field label={t("adminVisuals.altEn")} value={v.login_image_alt_en || ""} onChange={(x) => set("login_image_alt_en", x)} testid="visuals-login-alt-en" disabled={readOnly} />
            </div>
          </SectionCard>

          <SectionCard icon={<ImageIcon size={18} />} title={t("adminVisuals.processSection")}>
            <label className="mb-4 flex items-center gap-2 text-sm text-foreground">
              <input data-testid="visuals-process-show" type="checkbox" checked={v.process_image_show !== false} disabled={readOnly} onChange={(e) => set("process_image_show", e.target.checked)} />
              {t("adminVisuals.show")}
            </label>
            <ImageControl
              slug="process"
              value={v.process_image_url || ""}
              defaultUrl={PROCESS_DEFAULT}
              onChange={(x) => set("process_image_url", x)}
              onUpload={uploadFor("process_image_url")}
              onOpenPicker={() => openPicker("process_image_url")}
              disabled={readOnly}
            />
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <Field label={t("adminVisuals.altId")} value={v.process_image_alt_id || ""} onChange={(x) => set("process_image_alt_id", x)} testid="visuals-process-alt-id" disabled={readOnly} />
              <Field label={t("adminVisuals.altEn")} value={v.process_image_alt_en || ""} onChange={(x) => set("process_image_alt_en", x)} testid="visuals-process-alt-en" disabled={readOnly} />
            </div>
          </SectionCard>

          <SectionCard icon={<Megaphone size={18} />} title={t("adminVisuals.promoSection")}>
            <p className="mb-4 text-sm text-muted-foreground">{t("adminVisuals.promoHint")}</p>
            <label className="mb-5 flex items-center gap-2 text-sm text-foreground">
              <input
                data-testid="visuals-promo-show"
                type="checkbox"
                checked={v.promo_show !== false}
                disabled={readOnly}
                onChange={(e) => set("promo_show", e.target.checked)}
              />
              {t("adminVisuals.show")}
            </label>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label={t("adminVisuals.promoEyebrowId")} value={v.promo_eyebrow_id || ""} onChange={(x) => set("promo_eyebrow_id", x)} testid="visuals-promo-eyebrow-id" disabled={readOnly} />
              <Field label={t("adminVisuals.promoEyebrowEn")} value={v.promo_eyebrow_en || ""} onChange={(x) => set("promo_eyebrow_en", x)} testid="visuals-promo-eyebrow-en" disabled={readOnly} />
              <Field label={t("adminVisuals.promoHeadingId")} value={v.promo_heading_id || ""} onChange={(x) => set("promo_heading_id", x)} testid="visuals-promo-heading-id" disabled={readOnly} />
              <Field label={t("adminVisuals.promoHeadingEn")} value={v.promo_heading_en || ""} onChange={(x) => set("promo_heading_en", x)} testid="visuals-promo-heading-en" disabled={readOnly} />
              <Field label={t("adminVisuals.promoDescId")} value={v.promo_desc_id || ""} onChange={(x) => set("promo_desc_id", x)} testid="visuals-promo-desc-id" disabled={readOnly} />
              <Field label={t("adminVisuals.promoDescEn")} value={v.promo_desc_en || ""} onChange={(x) => set("promo_desc_en", x)} testid="visuals-promo-desc-en" disabled={readOnly} />
              <Field label={t("adminVisuals.promoCtaId")} value={v.promo_cta_id || ""} onChange={(x) => set("promo_cta_id", x)} testid="visuals-promo-cta-id" disabled={readOnly} />
              <Field label={t("adminVisuals.promoCtaEn")} value={v.promo_cta_en || ""} onChange={(x) => set("promo_cta_en", x)} testid="visuals-promo-cta-en" disabled={readOnly} />
            </div>
            <p className="mb-3 mt-6 text-[0.6rem] uppercase tracking-[0.22em] text-foreground">{t("adminVisuals.promoImage")}</p>
            <ImageControl
              slug="promo"
              value={v.promo_image_url || ""}
              defaultUrl=""
              onChange={(x) => set("promo_image_url", x)}
              onUpload={uploadFor("promo_image_url")}
              onOpenPicker={() => openPicker("promo_image_url")}
              disabled={readOnly}
            />
          </SectionCard>
          <SectionCard icon={<Gauge size={18} />} title={t("adminVisuals.dashboardSection")}>
            <p className="mb-4 text-sm text-muted-foreground">{t("adminVisuals.dashboardHint")}</p>
            <label className="mb-4 flex items-center gap-2 text-sm text-foreground">
              <input
                data-testid="visuals-dashboard-enabled"
                type="checkbox"
                checked={v.dashboard_bg_enabled === true}
                disabled={readOnly}
                onChange={(e) => set("dashboard_bg_enabled", e.target.checked)}
              />
              {t("adminVisuals.bgEnabled")}
            </label>
            <ImageControl
              slug="dashboard"
              value={v.dashboard_bg_url || ""}
              defaultUrl=""
              onChange={(x) => set("dashboard_bg_url", x)}
              onUpload={uploadFor("dashboard_bg_url")}
              onOpenPicker={() => openPicker("dashboard_bg_url")}
              disabled={readOnly || v.dashboard_bg_enabled !== true}
            />
            <BgAppearance slug="dashboard" prefix="dashboard_bg" v={v} set={set} disabled={readOnly || v.dashboard_bg_enabled !== true} />
            <button
              type="button"
              data-testid="visuals-dashboard-reset-marble"
              disabled={readOnly}
              onClick={() => {
                set("dashboard_bg_enabled", false);
                set("dashboard_bg_url", "");
                set("dashboard_bg_opacity", 10);
                set("dashboard_bg_fit", "cover");
                set("dashboard_bg_blur", 0);
              }}
              className="mt-5 inline-flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2.5 text-[0.64rem] uppercase tracking-[0.16em] text-muted-foreground transition-colors hover:border-gold disabled:opacity-60"
            >
              <ArrowCounterClockwise size={14} />
              {t("adminVisuals.resetMarble")}
            </button>
          </SectionCard>

          <SectionCard icon={<SignIn size={18} />} title={t("adminVisuals.loginSectionBg")}>
            <p className="mb-4 text-sm text-muted-foreground">{t("adminVisuals.loginBgHint")}</p>
            <label className="mb-4 flex items-center gap-2 text-sm text-foreground">
              <input
                data-testid="visuals-loginbg-enabled"
                type="checkbox"
                checked={v.login_bg_enabled === true}
                disabled={readOnly}
                onChange={(e) => set("login_bg_enabled", e.target.checked)}
              />
              {t("adminVisuals.bgEnabled")}
            </label>
            <ImageControl
              slug="loginbg"
              value={v.login_bg_url || ""}
              defaultUrl=""
              onChange={(x) => set("login_bg_url", x)}
              onUpload={uploadFor("login_bg_url")}
              onOpenPicker={() => openPicker("login_bg_url")}
              disabled={readOnly || v.login_bg_enabled !== true}
            />
            <BgAppearance slug="loginbg" prefix="login_bg" v={v} set={set} disabled={readOnly || v.login_bg_enabled !== true} />
            <button
              type="button"
              data-testid="visuals-loginbg-reset-all"
              disabled={readOnly}
              onClick={() => {
                set("login_bg_enabled", false);
                set("login_bg_url", "");
                set("login_bg_opacity", 10);
                set("login_bg_fit", "cover");
                set("login_bg_blur", 0);
              }}
              className="mt-5 inline-flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2.5 text-[0.64rem] uppercase tracking-[0.16em] text-muted-foreground transition-colors hover:border-gold disabled:opacity-60"
            >
              <ArrowCounterClockwise size={14} />
              {t("adminVisuals.resetLoginBg")}
            </button>
          </SectionCard>

          <SectionCard icon={<House size={18} />} title={t("adminVisuals.homeBgSection")}>
            <p className="mb-4 text-sm text-muted-foreground">{t("adminVisuals.homeBgHint")}</p>
            <label className="mb-4 flex items-center gap-2 text-sm text-foreground">
              <input
                data-testid="visuals-homebg-enabled"
                type="checkbox"
                checked={v.home_bg_enabled === true}
                disabled={readOnly}
                onChange={(e) => set("home_bg_enabled", e.target.checked)}
              />
              {t("adminVisuals.bgEnabled")}
            </label>
            <ImageControl
              slug="homebg"
              value={v.home_bg_url || ""}
              defaultUrl=""
              onChange={(x) => set("home_bg_url", x)}
              onUpload={uploadFor("home_bg_url")}
              onOpenPicker={() => openPicker("home_bg_url")}
              disabled={readOnly || v.home_bg_enabled !== true}
            />
            <BgAppearance slug="homebg" prefix="home_bg" v={v} set={set} disabled={readOnly || v.home_bg_enabled !== true} />
            <button
              type="button"
              data-testid="visuals-homebg-reset-all"
              disabled={readOnly}
              onClick={() => {
                set("home_bg_enabled", false);
                set("home_bg_url", "");
                set("home_bg_opacity", 20);
                set("home_bg_fit", "cover");
                set("home_bg_blur", 0);
              }}
              className="mt-5 inline-flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2.5 text-[0.64rem] uppercase tracking-[0.16em] text-muted-foreground transition-colors hover:border-gold disabled:opacity-60"
            >
              <ArrowCounterClockwise size={14} />
              {t("adminVisuals.resetHomeBg")}
            </button>
          </SectionCard>

          <SectionCard icon={<Diamond size={18} />} title={t("adminVisuals.homeGemsSection")}>
            <p className="mb-5 text-sm text-muted-foreground">{t("adminVisuals.homeGemsHint")}</p>
            <div className="space-y-8">
              {([
                ["diamond", "home_gem_diamond_url", GEM_DEFAULT.diamond, t("adminVisuals.gemDiamond")],
                ["ruby", "home_gem_ruby_url", GEM_DEFAULT.ruby, t("adminVisuals.gemRuby")],
                ["sapphire", "home_gem_sapphire_url", GEM_DEFAULT.sapphire, t("adminVisuals.gemSapphire")],
                ["emerald", "home_gem_emerald_url", GEM_DEFAULT.emerald, t("adminVisuals.gemEmerald")],
              ] as const).map(([slug, field, def, label]) => (
                <div key={slug}>
                  <p className="mb-3 text-[0.6rem] uppercase tracking-[0.22em] text-foreground">{label}</p>
                  <ImageControl
                    slug={`gem-${slug}`}
                    value={v[field] || ""}
                    defaultUrl={def}
                    onChange={(x) => set(field, x)}
                    onUpload={uploadFor(field)}
                    onOpenPicker={() => openPicker(field)}
                    disabled={readOnly}
                  />
                </div>
              ))}
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

      {picker && <MediaPicker items={media} onSelect={applyPicked} onClose={() => setPicker(null)} />}
    </section>
  );
}
