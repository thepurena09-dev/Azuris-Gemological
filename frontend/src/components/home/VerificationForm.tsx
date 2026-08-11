import * as React from "react";
import {
  ShieldCheck,
  Certificate,
  Info,
  CircleNotch,
  SealCheck,
  WarningCircle,
  FileText,
  X,
} from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiFetch, unwrap } from "@/lib/api";

const CERT_RE = /^AGR-[A-Z]{3}-\d{6}-\d{2}$/;

interface Props {
  initialCert?: string;
  qrToken?: string;
}

export default function VerificationForm({ initialCert, qrToken }: Props) {
  const { t } = useLanguage();
  const [cert, setCert] = React.useState(initialCert || "");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [notFound, setNotFound] = React.useState(false);

  const [resultNumber, setResultNumber] = React.useState<string | null>(null);
  const [coverUrl, setCoverUrl] = React.useState<string | null>(null);

  const [pdfUrl, setPdfUrl] = React.useState<string | null>(null);
  const [pdfErr, setPdfErr] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (initialCert) setCert(initialCert);
  }, [initialCert]);

  const showCover = async (number: string): Promise<boolean> => {
    const res = await apiFetch(`/api/verify/cover/${encodeURIComponent(number)}`);
    if (!res.ok) return false;
    const blob = await res.blob();
    setCoverUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return URL.createObjectURL(blob);
    });
    setResultNumber(number);
    return true;
  };

  // QR flow: resolve token -> certificate number -> cover
  React.useEffect(() => {
    if (!qrToken) return;
    setLoading(true);
    setNotFound(false);
    setError(null);
    apiFetch("/api/verify/qr", { method: "POST", body: JSON.stringify({ token: qrToken }) })
      .then((r) => unwrap(r))
      .then(async (data: any) => {
        const number = data?.status === "valid" && data?.certificate?.certificate_number;
        if (number && (await showCover(number))) return;
        setNotFound(true);
      })
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [qrToken]);

  const runManual = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setNotFound(false);
    const normalized = cert.trim().toUpperCase();
    if (!CERT_RE.test(normalized)) {
      setError(t("verify.formatError"));
      return;
    }
    setLoading(true);
    try {
      const ok = await showCover(normalized);
      if (!ok) {
        setResultNumber(null);
        setCoverUrl(null);
        setNotFound(true);
      }
    } catch {
      setNotFound(true);
    } finally {
      setLoading(false);
    }
  };

  const openPdf = async () => {
    if (!resultNumber) return;
    setPdfErr(null);
    try {
      const res = await apiFetch(`/api/verify/pdf/${encodeURIComponent(resultNumber)}`);
      if (!res.ok) {
        setPdfErr(t("verify.notFound"));
        return;
      }
      const blob = await res.blob();
      setPdfUrl(URL.createObjectURL(blob));
    } catch {
      setPdfErr(t("verify.notFound"));
    }
  };

  const closePdf = () => {
    if (pdfUrl) URL.revokeObjectURL(pdfUrl);
    setPdfUrl(null);
  };

  return (
    <div className="rounded-2xl border border-border bg-card p-7 shadow-[0_30px_70px_-45px_rgba(13,27,42,0.4)] md:p-9">
      {qrToken && (
        <div className="mb-5 flex items-start gap-3 rounded-lg border border-gold/40 bg-secondary p-4">
          <Info size={18} weight="regular" className="mt-0.5 shrink-0 text-gold" />
          <p className="text-sm text-muted-foreground">{t("verifyResult.qrDetected")}</p>
        </div>
      )}

      <form data-testid={TEST_IDS.verify.form} onSubmit={runManual} noValidate className="space-y-5">
        <div>
          <label
            htmlFor="verify-cert"
            className="mb-2 block text-[0.62rem] uppercase tracking-[0.22em] text-muted-foreground"
          >
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
        {error && (
          <p role="alert" className="text-sm text-red-600">
            {error}
          </p>
        )}
        <button
          type="submit"
          data-testid={TEST_IDS.verify.submit}
          disabled={loading}
          className="inline-flex w-full items-center justify-center gap-3 rounded-lg bg-primary px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground transition-shadow duration-300 hover:shadow-xl disabled:opacity-70"
        >
          {loading ? (
            <CircleNotch size={16} weight="bold" className="animate-spin" />
          ) : (
            <ShieldCheck size={16} weight="regular" className="text-gold" />
          )}
          {loading ? t("verify.submitting") : t("verify.submit")}
        </button>
      </form>

      <div data-testid={TEST_IDS.verify.result} aria-live="polite" className="mt-5">
        {!resultNumber && !notFound && !loading && (
          <p className="text-xs leading-relaxed text-muted-foreground/80">{t("verify.emptyHint")}</p>
        )}

        {notFound && (
          <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-5">
            <WarningCircle size={20} weight="regular" className="mt-0.5 shrink-0 text-red-600" />
            <p className="text-sm font-medium text-foreground">{t("verify.notFound")}</p>
          </div>
        )}

        {resultNumber && coverUrl && (
          <div className="rounded-lg border border-emerald-300 bg-emerald-50/60 p-5">
            <p className="flex items-center gap-2 text-sm font-semibold text-emerald-700">
              <SealCheck size={20} weight="fill" /> {t("verify.authentic")}
            </p>
            <div className="mt-5 grid gap-5 md:grid-cols-[minmax(0,200px)_1fr] md:items-center">
              <div className="mx-auto w-full max-w-[200px]">
                <p className="mb-2 text-center text-[0.56rem] uppercase tracking-[0.28em] text-gold">
                  {t("verify.coverHeading")}
                </p>
                <div
                  className="overflow-hidden rounded-xl border border-gold/40 bg-white shadow-[0_20px_50px_-35px_rgba(13,27,42,0.6)]"
                  style={{ aspectRatio: "148 / 210" }}
                >
                  <img
                    data-testid={TEST_IDS.verify.previewImage}
                    src={coverUrl}
                    alt={t("verify.coverHeading")}
                    className="h-full w-full object-contain"
                  />
                </div>
              </div>
              <div>
                <p className="text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground">
                  {t("verify.certLabel")}
                </p>
                <p className="mt-1 font-mono text-lg text-foreground">{resultNumber}</p>
                <button
                  type="button"
                  data-testid={TEST_IDS.verify.viewDigital}
                  onClick={openPdf}
                  className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-gold bg-primary px-6 py-3.5 text-[0.68rem] uppercase tracking-[0.2em] text-primary-foreground transition-shadow duration-300 hover:shadow-xl sm:w-auto"
                >
                  <FileText size={16} weight="regular" className="text-gold" />
                  {t("verify.viewDetails")}
                </button>
                {pdfErr && (
                  <p role="alert" className="mt-3 text-sm text-red-600">
                    {pdfErr}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {pdfUrl && (
        <div
          data-testid={TEST_IDS.verify.viewerModal}
          onClick={closePdf}
          className="fixed inset-0 z-[100] flex flex-col bg-primary/85 p-4 backdrop-blur-sm md:p-8"
        >
          <div
            className="mx-auto flex h-full w-full max-w-4xl flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between gap-4 border-b border-border p-4">
              <div className="flex items-center gap-2 text-sm">
                <ShieldCheck size={18} weight="fill" className="text-gold" />
                <span className="font-medium text-foreground">{t("verify.pdfTitle")}</span>
              </div>
              <button
                type="button"
                data-testid={TEST_IDS.verify.viewerClose}
                onClick={closePdf}
                className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-[0.62rem] uppercase tracking-[0.15em] text-primary-foreground"
              >
                <X size={14} /> {t("verify.close")}
              </button>
            </div>
            <iframe
              data-testid="verify-home-pdf-iframe"
              title="certificate-pdf"
              src={pdfUrl}
              className="w-full flex-1 bg-neutral-100"
            />
          </div>
        </div>
      )}
    </div>
  );
}
