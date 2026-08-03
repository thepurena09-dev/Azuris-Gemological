import { Link } from "react-router-dom";
import { ShieldCheck, ArrowRight } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

const HERO_IMAGE =
  "https://images.unsplash.com/photo-1596213411964-ee96819a396c?crop=entropy&cs=srgb&fm=jpg&q=90&w=1600";

export default function HomePage() {
  const { t } = useLanguage();

  return (
    <div data-testid={TEST_IDS.page.home} className="bg-background">
      {/* Editorial hero — content left, luxury photography right */}
      <section className="mx-auto grid max-w-7xl items-center gap-16 px-6 py-24 md:px-10 md:py-32 lg:grid-cols-2 lg:gap-24 lg:py-40">
        <div>
          <div className="mb-8 flex items-center gap-4">
            <span className="h-px w-12 bg-gold" />
            <span className="text-[0.72rem] uppercase tracking-[0.4em] text-gold">
              {t("footer.established")}
            </span>
          </div>

          <h1 className="font-serif text-6xl font-normal leading-[1.05] tracking-tight text-foreground md:text-7xl">
            {t("brand")}
          </h1>

          <p className="mt-8 max-w-md text-lg font-light leading-relaxed text-muted-foreground md:text-xl">
            {t("tagline")}
          </p>

          <div className="mt-12 flex flex-wrap items-center gap-4">
            <Link
              to="/catalog"
              data-testid={TEST_IDS.common.ctaHome}
              className="group inline-flex items-center gap-3 rounded-lg bg-primary px-9 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground shadow-sm transition-shadow duration-300 hover:shadow-xl"
            >
              {t("nav.catalog")}
              <ArrowRight size={16} weight="bold" />
            </Link>
            <Link
              to="/verification"
              data-testid={TEST_IDS.common.ctaVerify}
              className="inline-flex items-center gap-3 rounded-lg border border-gold px-9 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-foreground shadow-sm transition-shadow duration-300 hover:shadow-lg"
            >
              <ShieldCheck size={18} weight="regular" className="text-gold" />
              {t("nav.verification")}
            </Link>
          </div>

          <p className="mt-16 text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground/70">
            {t("sprintNotice")}
          </p>
        </div>

        {/* Large luxury image on the right */}
        <div className="relative">
          <div className="overflow-hidden rounded-2xl border border-border bg-secondary shadow-[0_30px_80px_-40px_rgba(13,27,42,0.35)]">
            <img
              src={HERO_IMAGE}
              alt="Brilliant-cut diamonds on a bright studio surface"
              className="aspect-[4/5] w-full object-cover"
            />
          </div>
          <div className="pointer-events-none absolute -bottom-5 -left-5 hidden h-24 w-24 rounded-2xl border border-gold/40 md:block" />
        </div>
      </section>
    </div>
  );
}
