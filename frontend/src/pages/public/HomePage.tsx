import { Link } from "react-router-dom";
import { useState } from "react";
import {
  ShieldCheck,
  ArrowRight,
  Diamond,
  Medal,
  GlobeHemisphereWest,
  Shield,
  Eye,
  X,
} from "@phosphor-icons/react";
import type { Icon } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

const HERO_IMAGE =
  "https://static.prod-images.emergentagent.com/jobs/0d8170c5-08d6-45ed-9937-114710780b07/images/11e5956f874718e6db198dda556242a9e59a93fb2ea1cd0b3fe0d77cc5e02724.jpeg";

const MARBLE_BG =
  "https://static.prod-images.emergentagent.com/jobs/6572b450-f0e7-4d20-83da-0f44a5e44dfd/images/df3161b0cd73f56ca5ed2325b394244a0bc533006164f0b288a0bd38c33fcfef.jpeg";

const CERT_PREVIEW_IMAGE =
  "https://static.prod-images.emergentagent.com/jobs/0d8170c5-08d6-45ed-9937-114710780b07/images/0d47639e6e497245d458ccc63d3dfef83fa6bcc954a41cf25e2143e94cbeec9d.jpeg";

export default function HomePage() {
  const { t } = useLanguage();
  const [previewOpen, setPreviewOpen] = useState(false);

  const stats: { icon: Icon; k: string }[] = [
    { icon: Diamond, k: "home.stats.accurate" },
    { icon: ShieldCheck, k: "home.stats.global" },
    { icon: Medal, k: "home.stats.professional" },
    { icon: GlobeHemisphereWest, k: "home.stats.recognized" },
  ];

  const features: { icon: Icon; k: string }[] = [
    { icon: Shield, k: "home.features.trusted" },
    { icon: Diamond, k: "home.features.accurate" },
    { icon: Medal, k: "home.features.professional" },
    { icon: GlobeHemisphereWest, k: "home.features.global" },
  ];

  return (
    <div data-testid={TEST_IDS.page.home} className="bg-background">
      {/* Hero — balanced editorial two-column */}
      <section className="relative overflow-hidden bg-secondary">
          {/* marble vein texture — sharp, premium veins over the white background */}
          <div className="pointer-events-none absolute inset-0">
            <div
              className="absolute inset-0 bg-cover bg-center opacity-90 mix-blend-multiply contrast-150 saturate-150"
              style={{ backgroundImage: `url(${MARBLE_BG})` }}
            />
            <div className="absolute inset-0 bg-gradient-to-r from-secondary/55 via-secondary/10 to-transparent" />
            <div className="absolute -right-24 -top-32 h-96 w-96 rounded-full bg-gold/10 blur-3xl" />
          </div>

          <div className="relative mx-auto grid max-w-7xl items-center gap-14 px-6 pb-40 pt-20 md:px-10 md:pt-28 lg:grid-cols-[1.05fr_0.95fr] lg:gap-16 lg:pb-48">
            {/* Left — copy */}
            <div className="max-w-xl">
              <div className="mb-7 flex items-center gap-4">
                <span className="h-px w-10 bg-gold" />
                <span className="text-[0.68rem] uppercase tracking-[0.4em] text-gold">
                  {t("footer.established")}
                </span>
              </div>

              <h1 className="font-serif text-6xl font-normal leading-[0.98] tracking-tight text-foreground md:text-8xl">
                Azuris
                <span className="mt-1 block text-gold">Gemological</span>
              </h1>

              <p className="mt-8 font-serif text-2xl font-medium tracking-tight text-foreground md:text-3xl">
                {t("tagline")}
              </p>
              <p className="mt-5 max-w-md text-base leading-relaxed text-muted-foreground">
                {t("home.description")}
              </p>

              <div className="mt-10 flex flex-wrap items-center gap-4">
                <Link
                  to="/catalog"
                  data-testid={TEST_IDS.common.ctaHome}
                  className="group inline-flex items-center gap-3 rounded-lg bg-primary px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground shadow-sm transition-shadow duration-300 hover:shadow-xl"
                >
                  {t("nav.catalog")}
                  <ArrowRight size={16} weight="bold" />
                </Link>
                <Link
                  to="/verification"
                  data-testid={TEST_IDS.common.ctaVerify}
                  className="inline-flex items-center gap-3 rounded-lg border border-gold px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-foreground transition-shadow duration-300 hover:shadow-lg"
                >
                  <ShieldCheck size={18} weight="regular" className="text-gold" />
                  {t("nav.verification")}
                </Link>
                <button
                  type="button"
                  data-testid={TEST_IDS.common.ctaPreview}
                  onClick={() => setPreviewOpen(true)}
                  className="group inline-flex items-center gap-3 rounded-lg bg-gold px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary shadow-sm transition-shadow duration-300 hover:shadow-xl"
                >
                  <Eye size={18} weight="regular" className="text-primary transition-transform duration-300 group-hover:scale-110" />
                  {t("home.preview")}
                </button>
              </div>
            </div>

            {/* Right — framed sapphire with floating preview card */}
            <div className="relative mx-auto w-full max-w-sm lg:mr-0 lg:max-w-md">
              <div className="absolute -inset-3 rounded-[1.75rem] border border-gold/30" />
              <div className="relative overflow-hidden rounded-3xl shadow-[0_40px_90px_-45px_rgba(13,27,42,0.55)]">
                <img
                  src={HERO_IMAGE}
                  alt="Blue sapphire"
                  className="aspect-[4/5] h-full w-full object-cover object-center"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-secondary/40 via-transparent to-transparent" />
              </div>

              {/* Floating preview card — also opens modal */}
              <button
                type="button"
                onClick={() => setPreviewOpen(true)}
                aria-label={t("home.preview")}
                className="group absolute -bottom-6 -left-6 flex items-center gap-4 rounded-2xl border border-border bg-card/95 px-5 py-4 shadow-[0_24px_60px_-35px_rgba(13,27,42,0.5)] backdrop-blur transition-transform duration-300 hover:-translate-y-1"
              >
                <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-secondary">
                  <Eye size={22} weight="thin" className="text-gold" />
                </span>
                <span className="text-left">
                  <span className="block text-[0.6rem] uppercase tracking-[0.28em] text-muted-foreground">
                    {t("home.previewBadge")}
                  </span>
                  <span className="mt-1 flex items-center gap-1.5 text-[0.72rem] uppercase tracking-[0.2em] text-foreground">
                    {t("home.preview")}
                    <ArrowRight size={13} weight="bold" className="transition-transform duration-300 group-hover:translate-x-0.5" />
                  </span>
                </span>
              </button>
            </div>
          </div>
        </section>

        {/* Certificate preview modal */}
        {previewOpen && (
          <div
            data-testid={TEST_IDS.common.previewModal}
            className="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-8"
          >
            <div
              className="absolute inset-0 bg-primary/70 backdrop-blur-sm"
              onClick={() => setPreviewOpen(false)}
            />
            <div className="relative z-10 w-full max-w-3xl overflow-hidden rounded-2xl border border-border bg-background shadow-[0_50px_120px_-40px_rgba(13,27,42,0.7)]">
              <button
                type="button"
                data-testid="certificate-preview-close"
                onClick={() => setPreviewOpen(false)}
                aria-label="Close preview"
                className="absolute right-4 top-4 z-20 flex h-9 w-9 items-center justify-center rounded-full bg-background/90 text-foreground shadow-sm transition-colors duration-300 hover:bg-secondary"
              >
                <X size={18} weight="bold" />
              </button>
              <div className="grid md:grid-cols-[1.1fr_1fr]">
                <div className="bg-secondary p-4">
                  <img
                    src={CERT_PREVIEW_IMAGE}
                    alt={t("home.previewTitle")}
                    data-testid={TEST_IDS.common.previewImage}
                    className="mx-auto h-full max-h-[70vh] w-full rounded-xl object-contain shadow-lg"
                  />
                </div>
                <div className="flex flex-col justify-center p-8">
                  <span className="mb-4 inline-flex w-fit items-center gap-2 rounded-full border border-gold/40 px-3 py-1 text-[0.6rem] uppercase tracking-[0.28em] text-gold">
                    <Diamond size={12} weight="fill" />
                    {t("home.previewBadge")}
                  </span>
                  <h2 className="font-serif text-2xl font-normal tracking-tight text-foreground">
                    {t("home.previewTitle")}
                  </h2>
                  <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
                    {t("home.previewSubtitle")}
                  </p>
                  <Link
                    to="/verification"
                    onClick={() => setPreviewOpen(false)}
                    className="mt-8 inline-flex w-fit items-center gap-3 rounded-lg border border-gold px-6 py-3 text-[0.68rem] uppercase tracking-[0.22em] text-foreground transition-shadow duration-300 hover:shadow-lg"
                  >
                    <ShieldCheck size={16} weight="regular" className="text-gold" />
                    {t("nav.verification")}
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

      {/* Stats bar (navy) — overlaps hero */}
      <div className="relative z-10 mx-auto -mt-24 max-w-7xl px-6 md:px-10">
        <div className="grid grid-cols-2 gap-y-8 rounded-2xl bg-primary px-8 py-9 text-primary-foreground shadow-[0_30px_70px_-40px_rgba(13,27,42,0.6)] md:grid-cols-4 md:divide-x md:divide-white/10">
          {stats.map(({ icon: Ic, k }) => (
            <div key={k} className="flex items-center gap-4 md:px-6">
              <Ic size={30} weight="thin" className="shrink-0 text-gold" />
              <div>
                <p className="font-serif text-xl tracking-tight">{t(`${k}.value`)}</p>
                <p className="mt-0.5 text-[0.68rem] uppercase tracking-[0.15em] text-primary-foreground/60">
                  {t(`${k}.label`)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Feature cards */}
      <section className="mx-auto max-w-7xl px-6 py-24 md:px-10 md:py-28">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {features.map(({ icon: Ic, k }) => (
            <div
              key={k}
              className="rounded-2xl border border-border bg-card p-8 shadow-[0_20px_50px_-40px_rgba(13,27,42,0.35)]"
            >
              <span className="flex h-14 w-14 items-center justify-center rounded-full border border-gold/40 bg-secondary">
                <Ic size={24} weight="thin" className="text-gold" />
              </span>
              <h3 className="mt-6 text-xs uppercase tracking-[0.2em] text-foreground">
                {t(`${k}.title`)}
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                {t(`${k}.desc`)}
              </p>
            </div>
          ))}
        </div>
        <p className="mt-16 text-center text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground/60">
          {t("sprintNotice")}
        </p>
      </section>
    </div>
  );
}
