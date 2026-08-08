import * as React from "react";
import { ShieldCheck, Certificate, Info, CircleNotch, SealCheck, WarningCircle, X, MagnifyingGlassPlus } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiFetch } from "@/lib/api";
import { appConfig } from "@/config";

const CERT_RE = /^AZR-GEM-\d{6}-\d{2}$/;

interface VerifyResult {
  status: string; // valid | archived | revoked | expired | not_found
  certificate?: any;
}

interface Props {
  initialCert?: string;
  qrToken?: string;
}

const STATUS_META: Record<string, { title: string; body: string; tone: "ok" | "warn" | "bad" }> = {
  valid: { title: "verifyResult.validTitle", body: "verifyResult.valid", tone: "ok" },
  archived: { title: "verifyResult.archivedTitle", body: "verifyResult.archived", tone: "warn" },
  revoked: { title: "verifyResult.revokedTitle", body: "verifyResult.revoked", tone: "bad" },
  expired: { title: "verifyResult.expiredTitle", body: "verifyResult.expired", tone: "warn" },
  not_found: { title: "verifyResult.notFoundTitle", body: "verifyResult.notFound", tone: "bad" },
};

export default function VerificationForm({ initialCert, qrToken }: Props) {
  const { t } = useLanguage();
  const [cert, setCert] = React.useState(initialCert || "");
  const [code, setCode] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [result, setResult] = React.useState<VerifyResult | null>(null);
  const [previewError, setPreviewError] = React.useState(false);
  const [viewerOpen, setViewerOpen] = React.useState(false);

  React.useEffect(() => {
    if (initialCert) setCert(initialCert);
  }, [initialCert]);

  const runManual = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setPreviewError(false);
    setViewerOpen(false);
    const normalized = cert.trim().toUpperCase();
    if (!CERT_RE.test(normalized)) {
      setError(t("verify.formatError"));
      return;
    }
    if (!code.trim()) {
      setError(t("verify.codeRequired"));
      return;
    }
    setLoading(true);
    try {
      const res = await apiFetch("/api/verify", {
        method: "POST",
        body: JSON.stringify({ certificate_number: normalized, security_code: code.trim() }),
      });
      if (!res.ok) throw new Error("err");
      setResult((await res.json()) as VerifyResult);
    } catch {
      setResult({ status: "error" });
    } finally {
      setLoading(false);
    }
  };

  const runQr = async () => {
    if (!qrToken) return;
    setError(null);
    setResult(null);
    setPreviewError(false);
    setViewerOpen(false);
    setLoading(true);
    try {
      const res = await apiFetch("/api/verify/qr", { method: "POST", body: JSON.stringify({ token: qrToken }) });
      if (!res.ok) throw new Error("err");
      setResult((await res.json()) as VerifyResult);
    } catch {
      setResult({ status: "error" });
    } finally {
      setLoading(false);
    }
  };

  const meta = result ? STATUS_META[result.status] : null;
  const toneClass =
    meta?.tone === "ok"
      ? "border-emerald-300 bg-emerald-50"
      : meta?.tone === "warn"
      ? "border-gold/50 bg-secondary"
      : "border-red-200 bg-red-50";

  const c = result?.certificate;
  const previewUrl =
    c?.preview_token
      ? `${appConfig.api.baseUrl}/api/verify/preview?t=${encodeURIComponent(c.preview_token)}`
      : null;

  return (
    <div className="rounded-2xl border border-border bg-card p-7 shadow-[0_30px_70px_-45px_rgba(13,27,42,0.4)] md:p-9">
      {qrToken && (
        <div className="mb-5 flex items-start gap-3 rounded-lg border border-gold/40 bg-secondary p-4">
          <Info size={18} weight="regular" className="mt-0.5 shrink-0 text-gold" />
          <p className="text-sm text-muted-foreground">{t("verifyResult.qrDetected")}</p>
        </div>
      )}

      {qrToken ? (
        <button
          type="button"
          data-testid={TEST_IDS.verify.submit}
          onClick={runQr}
          disabled={loading}
          className="inline-flex w-full items-center justify-center gap-3 rounded-lg bg-primary px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground transition-shadow duration-300 hover:shadow-xl disabled:opacity-70"
        >
          {loading ? <CircleNotch size={16} weight="bold" className="animate-spin" /> : <ShieldCheck size={16} weight="regular" className="text-gold" />}
          {loading ? t("verify.submitting") : t("verifyResult.showDetails")}
        </button>
      ) : (
        <form data-testid={TEST_IDS.verify.form} onSubmit={runManual} noValidate className="space-y-5">
          <div>
            <label htmlFor="verify-cert" className="mb-2 block text-[0.62rem] uppercase tracking-[0.22em] text-muted-foreground">
              {t("verify.certLabel")}
            </label>
            <div className="flex items-center gap-3 rounded-lg border border-border bg-background px-4 py-3 focus-within:border-gold">
              <Certificate size={18} weight="regular" className="shrink-0 text-gold" />
              <input
                id="verify-cert"
                data-testid={TEST_IDS.verify.certInput}
                value={cert}
                onChange={(e) => setCert(e.target.value)}
                placeholder={t("verify.certPlaceholder")}
                autoComplete="off"
                spellCheck={false}
                className="w-full bg-transparent text-sm uppercase tracking-wide text-foreground outline-none placeholder:text-muted-foreground/60"
              />
            </div>
          </div>
          <div>
            <label htmlFor="verify-code" className="mb-2 block text-[0.62rem] uppercase tracking-[0.22em] text-muted-foreground">
              {t("verify.codeLabel")}
            </label>
            <div className="flex items-center gap-3 rounded-lg border border-border bg-background px-4 py-3 focus-within:border-gold">
              <ShieldCheck size={18} weight="regular" className="shrink-0 text-gold" />
              <input
                id="verify-code"
                data-testid={TEST_IDS.verify.codeInput}
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder={t("verify.codePlaceholder")}
                autoComplete="off"
                className="w-full bg-transparent text-sm tracking-wide text-foreground outline-none placeholder:text-muted-foreground/60"
              />
            </div>
          </div>
          {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            data-testid={TEST_IDS.verify.submit}
            disabled={loading}
            className="inline-flex w-full items-center justify-center gap-3 rounded-lg bg-primary px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground transition-shadow duration-300 hover:shadow-xl disabled:opacity-70"
          >
            {loading ? <CircleNotch size={16} weight="bold" className="animate-spin" /> : <ShieldCheck size={16} weight="regular" className="text-gold" />}
            {loading ? t("verify.submitting") : t("verify.submit")}
          </button>
        </form>
      )}

      <div data-testid={TEST_IDS.verify.result} aria-live="polite" className="mt-5">
        {!result && !loading && (
          <p className="text-xs leading-relaxed text-muted-foreground/80">{t("verify.emptyHint")}</p>
        )}
        {result && (result.status === "error" ? (
          <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-5">
            <WarningCircle size={20} weight="regular" className="mt-0.5 shrink-0 text-red-600" />
            <div>
              <p className="text-sm font-medium text-foreground">{t("verifyResult.errorTitle")}</p>
              <p className="mt-1 text-sm text-muted-foreground">{t("verifyResult.error")}</p>
            </div>
          </div>
        ) : (
          <div className={`rounded-lg border p-5 ${toneClass}`}>
            <div className="flex items-start gap-3">
              {meta?.tone === "ok" ? (
                <SealCheck size={22} weight="fill" className="mt-0.5 shrink-0 text-emerald-600" />
              ) : (
                <WarningCircle size={22} weight="regular" className="mt-0.5 shrink-0 text-gold" />
              )}
              <div>
                <p className="text-sm font-semibold text-foreground">{meta ? t(meta.title) : ""}</p>
                <p className="mt-1 text-sm text-muted-foreground">{meta ? t(meta.body) : ""}</p>
              </div>
            </div>

            {c && result.status === "valid" && (
              <div className="mt-6 grid gap-6 border-t border-black/5 pt-6 lg:grid-cols-5">
                {/* Certificate front-cover preview — left column (~42%) */}
                <div className="lg:col-span-2">
                  <PreviewCard
                    url={previewUrl}
                    error={previewError}
                    onError={() => setPreviewError(true)}
                    onView={() => previewUrl && !previewError && setViewerOpen(true)}
                    label={t("verifyResult.certificatePreview")}
                    unavailable={t("verifyResult.previewUnavailable")}
                  />
                </div>

                {/* Certificate information — right column (~58%) */}
                <div className="space-y-5 lg:col-span-3">
                  <div>
                    <SectionLabel>{t("verifyResult.sectionBasic")}</SectionLabel>
                    <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
                      <Field label={t("verifyResult.fields.number")} value={c.certificate_number} />
                      <Field label={t("verifyResult.fields.issue")} value={c.issue_date} />
                      <Field label={t("verifyResult.fields.version")} value={c.version} />
                      <Field label={t("verifyResult.validTitle")} value={t("verifyResult.verifiedCertificate")} />
                    </dl>
                  </div>

                  <div>
                    <SectionLabel>{t("verifyResult.sectionGemstone")}</SectionLabel>
                    <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
                      <Field label={t("verifyResult.fields.species")} value={c.gemstone?.species} />
                      <Field label={t("verifyResult.fields.carat")} value={c.gemstone?.carat} />
                      <Field label={t("verifyResult.fields.color")} value={c.gemstone?.color} />
                      <Field label={t("verifyResult.fields.clarity")} value={c.gemstone?.clarity} />
                      <Field label={t("verifyResult.fields.cut")} value={c.gemstone?.cut} />
                      <Field label={t("verifyResult.fields.shape")} value={c.gemstone?.shape} />
                      <Field label={t("verifyResult.fields.origin")} value={c.gemstone?.origin} />
                      <Field label={t("verifyResult.fields.treatment")} value={c.gemstone?.treatment} />
                    </dl>
                  </div>

                  {c.conclusion && (
                    <div>
                      <SectionLabel>{t("verifyResult.sectionResult")}</SectionLabel>
                      <p className="text-sm leading-relaxed text-foreground">{c.conclusion}</p>
                    </div>
                  )}

                  {c.owner_masked && (
                    <div>
                      <SectionLabel>{t("verifyResult.sectionOwner")}</SectionLabel>
                      <p className="text-sm text-foreground">{c.owner_masked}</p>
                    </div>
                  )}

                  {c.gemstone?.photo_url && (
                    <img
                      src={`${appConfig.api.baseUrl}${c.gemstone.photo_url}`}
                      alt={c.gemstone?.name || "Gemstone"}
                      loading="lazy"
                      className="h-44 w-full rounded-lg border border-black/5 object-cover"
                    />
                  )}

                  {previewUrl && !previewError && (
                    <button
                      type="button"
                      data-testid={TEST_IDS.verify.viewDigital}
                      onClick={() => setViewerOpen(true)}
                      className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-gold bg-primary px-6 py-3.5 text-[0.68rem] uppercase tracking-[0.2em] text-primary-foreground transition-shadow duration-300 hover:shadow-xl"
                    >
                      <SealCheck size={16} weight="fill" className="text-gold" />
                      {t("verifyResult.viewDigitalCertificate")}
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {viewerOpen && previewUrl && !previewError && (
        <div
          data-testid={TEST_IDS.verify.viewerModal}
          onClick={() => setViewerOpen(false)}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-primary/85 p-6 backdrop-blur-sm"
        >
          <div className="relative max-h-[90vh]" onClick={(e) => e.stopPropagation()}>
            <img
              src={previewUrl}
              alt={t("verifyResult.certificatePreview")}
              className="max-h-[90vh] w-auto rounded-xl object-contain shadow-2xl ring-1 ring-gold/40"
            />
            <button
              type="button"
              data-testid={TEST_IDS.verify.viewerClose}
              onClick={() => setViewerOpen(false)}
              aria-label="Close"
              className="absolute -right-3 -top-3 flex h-10 w-10 items-center justify-center rounded-full bg-background text-foreground shadow-lg transition-transform hover:scale-105"
            >
              <X size={18} weight="bold" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function PreviewCard({
  url,
  error,
  onError,
  onView,
  label,
  unavailable,
}: {
  url: string | null;
  error: boolean;
  onError: () => void;
  onView: () => void;
  label: string;
  unavailable: string;
}) {
  const [loaded, setLoaded] = React.useState(false);
  React.useEffect(() => {
    setLoaded(false);
  }, [url]);

  return (
    <div
      data-testid={TEST_IDS.verify.preview}
      className="rounded-xl border border-gold/40 bg-secondary/60 p-3 shadow-[0_20px_50px_-35px_rgba(13,27,42,0.6)]"
    >
      <p className="mb-2.5 text-center text-[0.56rem] uppercase tracking-[0.28em] text-gold">
        {label}
      </p>
      <div
        className="relative overflow-hidden rounded-lg bg-primary/5"
        style={{ aspectRatio: "74 / 105" }}
      >
        {url && !error ? (
          <>
            {!loaded && <div className="absolute inset-0 animate-pulse bg-black/5" />}
            <img
              src={url}
              alt={label}
              data-testid={TEST_IDS.verify.previewImage}
              loading="lazy"
              onLoad={() => setLoaded(true)}
              onError={onError}
              onClick={onView}
              className="h-full w-full cursor-zoom-in object-contain"
            />
            {loaded && (
              <span className="pointer-events-none absolute bottom-2 right-2 flex h-7 w-7 items-center justify-center rounded-full bg-primary/70 text-primary-foreground">
                <MagnifyingGlassPlus size={14} weight="bold" />
              </span>
            )}
          </>
        ) : (
          <div
            data-testid={TEST_IDS.verify.previewFallback}
            className="flex h-full items-center justify-center p-6 text-center text-xs text-muted-foreground"
          >
            {unavailable}
          </div>
        )}
      </div>
    </div>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="mb-3 flex items-center gap-3">
      <span className="h-px w-6 bg-gold" />
      <span className="text-[0.6rem] uppercase tracking-[0.24em] text-gold">{children}</span>
    </div>
  );
}

function Field({ label, value, full }: { label: string; value?: any; full?: boolean }) {
  if (value === undefined || value === null || value === "") return null;
  return (
    <div className={full ? "col-span-2" : ""}>
      <dt className="text-[0.58rem] uppercase tracking-[0.16em] text-muted-foreground">{label}</dt>
      <dd className="mt-0.5 text-foreground">{String(value)}</dd>
    </div>
  );
}
