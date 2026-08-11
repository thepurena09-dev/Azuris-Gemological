import * as React from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, Certificate, Info, FileDashed, DownloadSimple, SealCheck } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiJson } from "@/lib/api";
import { appConfig } from "@/config";

interface Credential {
  certificate_name: string;
  holder_name?: string;
  certificate_number?: string;
  issuer?: string;
  issue_date?: string;
  expiry_date?: string;
  status: string;
  short_description?: string;
  public_download_allowed?: boolean;
  updated_at?: string;
  document_url?: string;
  document_content_type?: string;
}

const STATUS_LABEL: Record<string, { id: string; en: string; ok?: boolean }> = {
  aktif: { id: "Terverifikasi dan Aktif", en: "Verified & Active", ok: true },
  tidak_aktif: { id: "Tidak Aktif", en: "Inactive" },
  kedaluwarsa: { id: "Kedaluwarsa", en: "Expired" },
  dalam_pembaruan: { id: "Dalam Pembaruan", en: "Being Updated" },
};

export default function LegalityPage() {
  const { t, locale } = useLanguage();
  const [rec, setRec] = React.useState<Credential | null>(null);
  const [loaded, setLoaded] = React.useState(false);

  React.useEffect(() => {
    apiJson<{ published: boolean; credential?: Credential }>("/api/legality")
      .then((d) => setRec(d.published && d.credential ? d.credential : null))
      .catch(() => setRec(null))
      .finally(() => setLoaded(true));
  }, []);

  const fields = rec
    ? [
        { l: locale === "id" ? "Nama Sertifikat" : "Certificate Name", v: rec.certificate_name },
        { l: locale === "id" ? "Pemegang / Institusi" : "Holder / Institution", v: rec.holder_name },
        { l: locale === "id" ? "Nomor Sertifikat" : "Certificate Number", v: rec.certificate_number },
        { l: locale === "id" ? "Penerbit" : "Issuer", v: rec.issuer },
        { l: locale === "id" ? "Tanggal Terbit" : "Issue Date", v: rec.issue_date },
        { l: locale === "id" ? "Berlaku Hingga" : "Valid Until", v: rec.expiry_date },
      ].filter((f) => f.v)
    : [];

  const status = rec ? STATUS_LABEL[rec.status] : undefined;
  const isImage = rec?.document_content_type?.startsWith("image/");
  const docHref = rec?.document_url ? `${appConfig.api.baseUrl}${rec.document_url}` : null;

  return (
    <div data-testid={TEST_IDS.legality.page} className="bg-background">
      {/* Hero */}
      <section className="border-b border-border bg-secondary">
        <div className="mx-auto max-w-5xl px-6 py-24 text-center md:px-10 md:py-28">
          <img
            src="/azuris-logo.png"
            alt="Azuris Gemological"
            width={72}
            height={72}
            className="mx-auto mb-7 h-18 w-18 object-contain"
            style={{ height: 72, width: 72 }}
            data-testid="legality-logo"
          />
          <div className="mb-6 flex items-center justify-center gap-4">
            <span className="h-px w-10 bg-gold" />
            <span className="text-[0.68rem] uppercase tracking-[0.4em] text-gold">{t("legalityTeaser.eyebrow")}</span>
            <span className="h-px w-10 bg-gold" />
          </div>
          <h1 className="mx-auto max-w-3xl font-serif text-4xl font-normal leading-[1.08] tracking-tight text-foreground md:text-6xl">
            {t("legality.title")}
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-muted-foreground">{t("legality.subtitle")}</p>
          <Link
            to="/verify"
            data-testid={TEST_IDS.legality.ctaVerify}
            className="mt-9 inline-flex items-center gap-3 rounded-lg bg-primary px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground transition-shadow duration-300 hover:shadow-xl"
          >
            <ShieldCheck size={16} weight="regular" className="text-gold" />
            {t("legality.ctaVerify")}
          </Link>
        </div>
      </section>

      {/* Viewer + info */}
      <section className="mx-auto max-w-6xl px-6 py-20 md:px-10 md:py-24">
        <div className="mb-8 flex items-center gap-4">
          <span className="h-px w-10 bg-gold" />
          <span className="text-[0.68rem] uppercase tracking-[0.4em] text-gold">{t("legality.viewerTitle")}</span>
        </div>

        {loaded && rec ? (
          <div className="grid gap-10 lg:grid-cols-[1.2fr_1fr]">
            {/* Document viewer */}
            <div data-testid={TEST_IDS.legality.viewer} className="rounded-2xl border border-border bg-card p-4 shadow-[0_30px_70px_-45px_rgba(13,27,42,0.4)]">
              {docHref ? (
                isImage ? (
                  <img src={docHref} alt={rec.certificate_name} className="mx-auto max-h-[560px] w-auto rounded-lg object-contain" />
                ) : (
                  <iframe title={rec.certificate_name} src={docHref} className="h-[560px] w-full rounded-lg" />
                )
              ) : (
                <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border bg-secondary/60 px-8 py-24 text-center">
                  <FileDashed size={30} weight="thin" className="text-gold" />
                  <p className="mt-4 text-sm text-muted-foreground">{t("legality.emptyTitle")}</p>
                </div>
              )}
              {docHref && rec.public_download_allowed && (
                <a
                  href={docHref}
                  target="_blank"
                  rel="noopener noreferrer"
                  download
                  data-testid="legality-download"
                  className="mt-4 inline-flex items-center gap-2 rounded-lg border border-gold px-5 py-2.5 text-[0.62rem] uppercase tracking-[0.2em] text-foreground"
                >
                  <DownloadSimple size={15} className="text-gold" />
                  {locale === "id" ? "Unduh Sertifikat" : "Download Certificate"}
                </a>
              )}
            </div>

            {/* Critical information */}
            <div>
              {status && (
                <span
                  data-testid="legality-status-badge"
                  className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-[0.62rem] uppercase tracking-[0.18em] ${
                    status.ok ? "bg-emerald-100 text-emerald-700" : "bg-secondary text-muted-foreground"
                  }`}
                >
                  {status.ok ? <SealCheck size={14} weight="fill" /> : <Info size={14} />}
                  {locale === "id" ? status.id : status.en}
                </span>
              )}
              <dl className="mt-6 space-y-4">
                {fields.map((f) => (
                  <div key={f.l} className="border-b border-border pb-3">
                    <dt className="text-[0.58rem] uppercase tracking-[0.18em] text-muted-foreground">{f.l}</dt>
                    <dd className="mt-1 text-base text-foreground">{f.v}</dd>
                  </div>
                ))}
              </dl>
              {rec.short_description && (
                <p className="mt-6 text-sm leading-relaxed text-muted-foreground">{rec.short_description}</p>
              )}
            </div>
          </div>
        ) : (
          <div
            data-testid={TEST_IDS.legality.viewer}
            className="relative overflow-hidden rounded-2xl border border-border bg-card p-10 shadow-[0_30px_70px_-45px_rgba(13,27,42,0.4)] md:p-16"
          >
            <div className="pointer-events-none absolute -right-24 -top-28 h-80 w-80 rounded-full bg-gold/10 blur-3xl" />
            <div className="relative flex flex-col items-center justify-center rounded-xl border border-dashed border-border bg-secondary/60 px-8 py-20 text-center">
              <span className="flex h-16 w-16 items-center justify-center rounded-full border border-gold/40 bg-background">
                <FileDashed size={30} weight="thin" className="text-gold" />
              </span>
              <p className="mt-7 font-serif text-2xl font-normal tracking-tight text-foreground">{t("legality.emptyTitle")}</p>
              <p className="mt-4 max-w-xl text-sm leading-relaxed text-muted-foreground">{t("legality.empty")}</p>
            </div>
          </div>
        )}
      </section>

      {/* Commitment + disclaimer */}
      <section className="border-t border-border bg-secondary/40">
        <div className="mx-auto grid max-w-5xl gap-10 px-6 py-20 md:grid-cols-2 md:px-10 md:py-24">
          <div>
            <div className="flex items-center gap-3">
              <Certificate size={20} weight="regular" className="text-gold" />
              <h2 className="text-xs uppercase tracking-[0.25em] text-foreground">{t("legality.copyTitle")}</h2>
            </div>
            <p className="mt-5 text-sm leading-relaxed text-muted-foreground">{t("legality.copy")}</p>
          </div>
          <div className="rounded-2xl border border-border bg-card p-7">
            <div className="flex items-center gap-3">
              <Info size={20} weight="regular" className="text-gold" />
              <h2 className="text-xs uppercase tracking-[0.25em] text-foreground">{t("legality.disclaimerTitle")}</h2>
            </div>
            <p className="mt-5 text-sm leading-relaxed text-muted-foreground">{t("legality.disclaimer")}</p>
          </div>
        </div>
      </section>
    </div>
  );
}
