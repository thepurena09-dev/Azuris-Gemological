import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  CaretRight,
  WhatsappLogo,
  ShieldCheck,
  Certificate,
  Sparkle,
} from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { SAMPLE_STONES } from "@/data/sampleGemstones";

const WHATSAPP_NUMBER = "6287812128884";

const FILTERS = [
  { key: "all", type: null },
  { key: "sapphire", type: "sapphire" },
  { key: "ruby", type: "ruby" },
  { key: "emerald", type: "emerald" },
  { key: "diamond", type: "diamond" },
] as const;

export default function CatalogPage() {
  const { t, locale } = useLanguage();
  const [active, setActive] = useState<string>("all");

  const stones = useMemo(() => {
    if (active === "all") return SAMPLE_STONES;
    return SAMPLE_STONES.filter((s) => s.type === active);
  }, [active]);

  return (
    <section
      data-testid={TEST_IDS.page.catalog}
      className="mx-auto max-w-7xl px-6 py-24 md:px-10 md:py-28"
    >
      {/* breadcrumb */}
      <nav
        data-testid={TEST_IDS.common.breadcrumb}
        className="mb-12 flex items-center text-[0.7rem] uppercase tracking-[0.25em] text-muted-foreground"
      >
        <Link to="/" className="transition-colors hover:text-foreground">
          {t("breadcrumbHome")}
        </Link>
        <span className="flex items-center">
          <CaretRight size={11} weight="bold" className="mx-3 text-gold" />
          <span className="text-foreground">{t("nav.catalog")}</span>
        </span>
      </nav>

      {/* header */}
      <div className="flex items-center gap-4">
        <span className="h-px w-10 bg-gold" />
        <span className="text-[0.7rem] uppercase tracking-[0.4em] text-gold">
          {t("catalog.eyebrow")}
        </span>
      </div>
      <h1 className="mt-6 max-w-3xl font-serif text-5xl font-normal leading-[1.05] tracking-tight text-foreground md:text-7xl">
        {t("catalog.title")}
      </h1>
      <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted-foreground">
        {t("catalog.subtitle")}
      </p>

      {/* sample notice */}
      <div
        data-testid={TEST_IDS.catalog.sampleNotice}
        className="mt-8 inline-flex items-center gap-2 rounded-full border border-gold/40 bg-secondary px-4 py-2 text-[0.62rem] uppercase tracking-[0.22em] text-gold"
      >
        <Sparkle size={13} weight="fill" />
        {t("catalog.sampleNotice")}
      </div>

      {/* filters */}
      <div
        data-testid={TEST_IDS.catalog.filters}
        className="mt-10 flex flex-wrap gap-3"
      >
        {FILTERS.map((f) => {
          const isActive = active === f.key;
          return (
            <button
              key={f.key}
              type="button"
              data-testid={`catalog-filter-${f.key}`}
              onClick={() => setActive(f.key)}
              className={`rounded-full border px-5 py-2 text-[0.62rem] uppercase tracking-[0.22em] transition-colors duration-300 ${
                isActive
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-border bg-card text-muted-foreground hover:border-gold hover:text-foreground"
              }`}
            >
              {t(`catalog.filter.${f.key}`)}
            </button>
          );
        })}
      </div>

      {/* grid */}
      <div
        data-testid={TEST_IDS.catalog.grid}
        className="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3"
      >
        {stones.map((stone) => {
          const waText = encodeURIComponent(
            `Halo Azuris, saya tertarik dengan ${stone.name[locale]} (${stone.certNumber}). Mohon informasinya.`
          );
          return (
            <article
              key={stone.id}
              data-testid={`catalog-card-${stone.id}`}
              className="group flex flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-[0_20px_50px_-40px_rgba(13,27,42,0.35)] transition-shadow duration-300 hover:shadow-[0_30px_70px_-40px_rgba(13,27,42,0.45)]"
            >
              <div className="relative aspect-[4/3] overflow-hidden bg-secondary">
                <img
                  src={stone.image}
                  alt={stone.name[locale]}
                  className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
                <span className="absolute left-4 top-4 inline-flex items-center gap-1.5 rounded-full bg-background/90 px-3 py-1 text-[0.55rem] uppercase tracking-[0.2em] text-foreground shadow-sm backdrop-blur">
                  <Certificate size={12} weight="fill" className="text-gold" />
                  {stone.certNumber}
                </span>
              </div>

              <div className="flex flex-1 flex-col p-6">
                <h3 className="font-serif text-2xl font-normal tracking-tight text-foreground">
                  {stone.name[locale]}
                </h3>

                <dl className="mt-5 grid grid-cols-2 gap-y-3 text-sm">
                  <Spec label={t("catalog.spec.carat")} value={stone.carat} />
                  <Spec label={t("catalog.spec.cut")} value={stone.cut[locale]} />
                  <Spec label={t("catalog.spec.color")} value={stone.color[locale]} />
                  <Spec label={t("catalog.spec.origin")} value={stone.origin[locale]} />
                </dl>

                <div className="mt-7 flex items-center gap-3 border-t border-border pt-5">
                  <a
                    href={`https://wa.me/${WHATSAPP_NUMBER}?text=${waText}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    data-testid={`catalog-whatsapp-${stone.id}`}
                    className="inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-primary px-4 py-3 text-[0.62rem] uppercase tracking-[0.2em] text-primary-foreground transition-shadow duration-300 hover:shadow-lg"
                  >
                    <WhatsappLogo size={16} weight="fill" className="text-gold" />
                    {t("catalog.whatsapp")}
                  </a>
                  <Link
                    to="/verification"
                    data-testid={`catalog-verify-${stone.id}`}
                    aria-label={t("nav.verification")}
                    className="inline-flex items-center justify-center rounded-lg border border-gold px-4 py-3 text-foreground transition-shadow duration-300 hover:shadow-md"
                  >
                    <ShieldCheck size={18} weight="regular" className="text-gold" />
                  </Link>
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function Spec({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-[0.58rem] uppercase tracking-[0.18em] text-muted-foreground">
        {label}
      </dt>
      <dd className="mt-0.5 text-foreground">{value}</dd>
    </div>
  );
}
