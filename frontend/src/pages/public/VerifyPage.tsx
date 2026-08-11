import * as React from "react";
import { useLocation } from "react-router-dom";
import {
  ShieldCheck,
  SealCheck,
  WarningCircle,
  CircleNotch,
  MagnifyingGlass,
  FileText,
  X,
} from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { apiFetch, unwrap } from "@/lib/api";
import { appConfig } from "@/config";

const CERT_RE = /^AGR-[A-Z]{3}-\d{6}-\d{2}$/;
const API = appConfig.api.baseUrl;
const SAMPLE_NUMBER = "AGR-ZMD-000015-26";

const STR = {
  id: {
    eyebrow: "Verifikasi Sertifikat",
    title: "Verifikasi Keaslian Sertifikat AGR",
    subtitle:
      "Pindai kode QR pada kartu sertifikat, atau masukkan nomor registrasi untuk membuka sampul sertifikat resmi Azuris Gemological Research.",
    searchLabel: "Nomor Registrasi Sertifikat",
    searchPlaceholder: "AGR-ZMD-000015-26",
    searchBtn: "Verifikasi Sertifikat",
    formatError: "Sertifikat tidak ditemukan.",
    notFound: "Sertifikat tidak ditemukan.",
    authentic: "Sertifikat ini asli dan diterbitkan oleh Azuris Gemological Research (AGR).",
    coverHeading: "Sampul Sertifikat",
    viewDetails: "Lihat Detail Sertifikat",
    loading: "Memeriksa…",
    close: "Tutup",
    pdfTitle: "Sertifikat (4 Halaman)",
    sampleBanner: "SAMPLE CERTIFICATE FOR DESIGN REVIEW — NOT A VALID CERTIFICATE.",
  },
  en: {
    eyebrow: "Certificate Verification",
    title: "Verify AGR Certificate Authenticity",
    subtitle:
      "Scan the QR code on the certificate card, or enter the registration number to open the official Azuris Gemological Research certificate cover.",
    searchLabel: "Certificate Registration Number",
    searchPlaceholder: "AGR-ZMD-000015-26",
    searchBtn: "Verify Certificate",
    formatError: "Certificate not found.",
    notFound: "Certificate not found.",
    authentic: "This certificate is authentic and issued by Azuris Gemological Research (AGR).",
    coverHeading: "Certificate Cover",
    viewDetails: "View Certificate Details",
    loading: "Checking…",
    close: "Close",
    pdfTitle: "4-Page Certificate",
    sampleBanner: "SAMPLE CERTIFICATE FOR DESIGN REVIEW — NOT A VALID CERTIFICATE.",
  },
};

export default function VerifyPage() {
  const { locale } = useLanguage();
  const s = STR[locale === "en" ? "en" : "id"];
  const { search } = useLocation();
  const isSample = new URLSearchParams(search).get("sample") === "1";

  const [qrLoading, setQrLoading] = React.useState(false);

  const [num, setNum] = React.useState("");
  const [searchErr, setSearchErr] = React.useState<string | null>(null);
  const [searching, setSearching] = React.useState(false);

  // Cover-first verification result
  const [resultNumber, setResultNumber] = React.useState<string | null>(null);
  const [coverUrl, setCoverUrl] = React.useState<string | null>(null);
  const [notFound, setNotFound] = React.useState(false);

  // 2-page PDF modal (opened via "View Certificate Details")
  const [pdfUrl, setPdfUrl] = React.useState<string | null>(null);
  const [pdfErr, setPdfErr] = React.useState<string | null>(null);

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

  // QR flow: /verify?t=<token>
  React.useEffect(() => {
    const token = new URLSearchParams(search).get("t");
    if (!token) return;
    setQrLoading(true);
    setNotFound(false);
    apiFetch("/api/verify/qr", { method: "POST", body: JSON.stringify({ token }) })
      .then((r) => unwrap(r))
      .then(async (data: any) => {
        const number = data?.status === "valid" && data?.certificate?.certificate_number;
        if (number && (await showCover(number))) return;
        setNotFound(true);
      })
      .catch(() => setNotFound(true))
      .finally(() => setQrLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSearchErr(null);
    setNotFound(false);
    const normalized = num.trim().toUpperCase();
    if (!CERT_RE.test(normalized)) {
      setSearchErr(s.formatError);
      return;
    }
    setSearching(true);
    try {
      const ok = await showCover(normalized);
      if (!ok) {
        setResultNumber(null);
        setSearchErr(s.notFound);
      }
    } catch {
      setSearchErr(s.notFound);
    } finally {
      setSearching(false);
    }
  };

  const openPdf = async () => {
    if (!resultNumber) return;
    setPdfErr(null);
    try {
      const res = await apiFetch(`/api/verify/pdf/${encodeURIComponent(resultNumber)}`);
      if (!res.ok) {
        setPdfErr(s.notFound);
        return;
      }
      const blob = await res.blob();
      setPdfUrl(URL.createObjectURL(blob));
    } catch {
      setPdfErr(s.notFound);
    }
  };

  const closePdf = () => {
    if (pdfUrl) URL.revokeObjectURL(pdfUrl);
    setPdfUrl(null);
  };

  return (
    <div data-testid="verify-page" className="bg-background">
      <section className="border-b border-border bg-secondary/40">
        <div className="mx-auto max-w-4xl px-6 py-20 text-center md:px-10">
          <div className="mx-auto mb-6 flex w-fit items-center gap-4">
            <span className="h-px w-10 bg-gold" />
            <span className="text-[0.68rem] uppercase tracking-[0.4em] text-gold">{s.eyebrow}</span>
            <span className="h-px w-10 bg-gold" />
          </div>
          <h1 className="font-serif text-4xl font-normal leading-tight tracking-tight text-foreground md:text-6xl">
            {s.title}
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-muted-foreground">
            {s.subtitle}
          </p>
        </div>
      </section>

      <div className="mx-auto max-w-3xl px-6 py-16 md:px-10">
        {/* SAMPLE presentation (design review only — never hits the DB) */}
        {isSample && (
          <div data-testid="verify-sample" className="mb-10">
            <div
              data-testid="verify-sample-banner"
              className="mb-6 rounded-xl border-2 border-dashed border-red-400 bg-red-50 px-5 py-4 text-center text-sm font-bold uppercase tracking-[0.12em] text-red-700"
            >
              {s.sampleBanner}
            </div>
            <div className="overflow-hidden rounded-2xl border border-gold/40 bg-card shadow-[0_30px_70px_-45px_rgba(13,27,42,0.4)]">
              <div className="aspect-[16/10] w-full overflow-hidden bg-secondary">
                <img
                  data-testid="verify-sample-photo"
                  src="/sample-gemstone.png"
                  alt="Zamrud (Sample)"
                  className="h-full w-full object-cover"
                />
              </div>
              <div className="p-8">
                <p className="flex items-center gap-2 text-sm font-semibold text-emerald-700">
                  <SealCheck size={20} weight="fill" /> {s.authentic}
                </p>
                <dl className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <dt className="text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground">{s.searchLabel}</dt>
                    <dd data-testid="verify-sample-number" className="mt-1 font-mono text-base text-foreground">{SAMPLE_NUMBER}</dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        )}

        {/* Loading (QR) */}
        {qrLoading && (
          <div className="mb-8 flex items-center justify-center gap-3 rounded-2xl border border-border bg-card p-10 text-muted-foreground">
            <CircleNotch size={20} className="animate-spin text-gold" /> {s.loading}
          </div>
        )}

        {/* Cover-first verification result */}
        {resultNumber && coverUrl && (
          <div
            data-testid="verify-result"
            className="mb-10 overflow-hidden rounded-2xl border border-emerald-300 bg-emerald-50/60 p-6 shadow-[0_30px_70px_-45px_rgba(13,27,42,0.4)] md:p-8"
          >
            <p className="flex items-center gap-2 text-sm font-semibold text-emerald-700">
              <SealCheck size={20} weight="fill" /> {s.authentic}
            </p>
            <div className="mt-6 grid gap-6 md:grid-cols-[minmax(0,240px)_1fr] md:items-center">
              <div className="mx-auto w-full max-w-[240px]">
                <p className="mb-2 text-center text-[0.56rem] uppercase tracking-[0.28em] text-gold">
                  {s.coverHeading}
                </p>
                <div
                  className="overflow-hidden rounded-xl border border-gold/40 bg-white shadow-[0_20px_50px_-35px_rgba(13,27,42,0.6)]"
                  style={{ aspectRatio: "148 / 210" }}
                >
                  <img
                    data-testid="verify-cover-image"
                    src={coverUrl}
                    alt={s.coverHeading}
                    className="h-full w-full object-contain"
                  />
                </div>
              </div>
              <div>
                <p className="text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground">
                  {s.searchLabel}
                </p>
                <p data-testid="verify-result-number" className="mt-1 font-mono text-lg text-foreground">
                  {resultNumber}
                </p>
                <button
                  type="button"
                  data-testid="verify-view-details"
                  onClick={openPdf}
                  className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-gold bg-primary px-6 py-3.5 text-[0.68rem] uppercase tracking-[0.2em] text-primary-foreground transition-shadow duration-300 hover:shadow-xl sm:w-auto"
                >
                  <FileText size={16} weight="regular" className="text-gold" />
                  {s.viewDetails}
                </button>
                {pdfErr && (
                  <p data-testid="verify-pdf-error" role="alert" className="mt-3 text-sm text-red-600">
                    {pdfErr}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {notFound && (
          <div
            data-testid="verify-notfound"
            className="mb-10 flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-6"
          >
            <WarningCircle size={22} weight="regular" className="mt-0.5 shrink-0 text-red-600" />
            <p className="text-sm font-medium text-foreground">{s.notFound}</p>
          </div>
        )}

        {/* Registration-number search */}
        <div className="rounded-2xl border border-border bg-card p-8 shadow-[0_30px_70px_-45px_rgba(13,27,42,0.4)]">
          <form data-testid="verify-search-form" onSubmit={submit} noValidate className="space-y-5">
            <div>
              <label
                htmlFor="verify-number"
                className="mb-2 block text-[0.62rem] uppercase tracking-[0.22em] text-muted-foreground"
              >
                {s.searchLabel}
              </label>
              <div className="flex items-center gap-3 rounded-lg border border-border bg-background px-4 py-3 focus-within:border-gold">
                <MagnifyingGlass size={18} weight="regular" className="shrink-0 text-gold" />
                <input
                  id="verify-number"
                  data-testid="verify-search-input"
                  value={num}
                  onChange={(e) => setNum(e.target.value)}
                  placeholder={s.searchPlaceholder}
                  autoComplete="off"
                  spellCheck={false}
                  className="w-full bg-transparent text-sm uppercase tracking-wide text-foreground outline-none placeholder:text-muted-foreground/60"
                />
              </div>
            </div>
            {searchErr && (
              <p data-testid="verify-search-error" role="alert" className="text-sm text-red-600">
                {searchErr}
              </p>
            )}
            <button
              type="submit"
              data-testid="verify-search-submit"
              disabled={searching}
              className="inline-flex w-full items-center justify-center gap-3 rounded-lg bg-primary px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground transition-shadow duration-300 hover:shadow-xl disabled:opacity-70"
            >
              {searching ? (
                <CircleNotch size={16} weight="bold" className="animate-spin" />
              ) : (
                <ShieldCheck size={16} weight="regular" className="text-gold" />
              )}
              {searching ? s.loading : s.searchBtn}
            </button>
          </form>
        </div>
      </div>

      {/* 2-page PDF modal */}
      {pdfUrl && (
        <div
          data-testid="verify-pdf-modal"
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
                <span className="font-medium text-foreground">{s.pdfTitle}</span>
              </div>
              <button
                type="button"
                data-testid="verify-pdf-close"
                onClick={closePdf}
                className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-[0.62rem] uppercase tracking-[0.15em] text-primary-foreground"
              >
                <X size={14} /> {s.close}
              </button>
            </div>
            <iframe
              data-testid="verify-pdf-iframe"
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
