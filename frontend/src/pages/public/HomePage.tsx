import { Link } from "react-router-dom";
import { ShieldCheck, ArrowRight } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

const HERO_IMAGE =
  "https://images.unsplash.com/photo-1678245687839-231ed039a18b?crop=entropy&cs=srgb&fm=jpg&q=90&w=2000";

export default function HomePage() {
  const { t } = useLanguage();

  return (
    <div data-testid={TEST_IDS.page.home}>
      {/* Hero — editorial, bright, white-forward */}
      <section className="relative overflow-hidden bg-background">
        <div className="absolute inset-0">
          <img
            src={HERO_IMAGE}
            alt="Emerald gemstones on a light surface"
            className="h-full w-full object-cover"
          />
          {/* Bright, airy white wash from the left — no dark overlay */}
          <div className="absolute inset-0 bg-gradient-to-r from-background via-background/85 to-background/20" />
          <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent" />
        </div>

        <div className="relative mx-auto flex min-h-[86vh] max-w-7xl flex-col justify-center px-6 py-28 md:px-10">
          <div className="mb-8 flex items-center gap-4">
            <span className="h-px w-10 bg-gold" />
            <span className="text-[0.7rem] uppercase tracking-[0.4em] text-gold">
              {t("footer.established")}
            </span>
          </div>

          <h1 className="max-w-4xl font-serif text-6xl font-normal leading-[1.02] tracking-tight text-foreground md:text-[7.5rem]">
            {t("brand")}
          </h1>

          <p className="mt-10 max-w-xl text-lg font-light leading-relaxed text-muted-foreground md:text-2xl">
            {t("tagline")}
          </p>

          <div className="mt-14 flex flex-wrap items-center gap-5">
            <Link
              to="/catalog"
              data-testid={TEST_IDS.common.ctaHome}
              className="group inline-flex items-center gap-3 rounded-sm bg-primary px-10 py-5 text-[0.7rem] uppercase tracking-[0.3em] text-primary-foreground transition-colors duration-300 hover:bg-primary/90"
            >
              {t("nav.catalog")}
              <ArrowRight
                size={16}
                weight="bold"
                className="transition-transform duration-300 group-hover:translate-x-1"
              />
            </Link>
            <Link
              to="/verification"
              data-testid={TEST_IDS.common.ctaVerify}
              className="inline-flex items-center gap-3 rounded-sm border border-primary px-10 py-5 text-[0.7rem] uppercase tracking-[0.3em] text-primary transition-colors duration-300 hover:bg-primary hover:text-primary-foreground"
            >
              <ShieldCheck size={18} weight="regular" />
              {t("nav.verification")}
            </Link>
          </div>

          <p className="mt-20 text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground/70">
            {t("sprintNotice")}
          </p>
        </div>
      </section>
    </div>
  );
}
