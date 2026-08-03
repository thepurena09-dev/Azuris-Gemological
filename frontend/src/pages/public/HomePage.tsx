import { Link } from "react-router-dom";
import { ShieldCheck, ArrowRight, Sparkle } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

const HERO_IMAGE =
  "https://images.unsplash.com/photo-1632980205460-e490e885e848?auto=format&fit=crop&w=1600&q=80";

export default function HomePage() {
  const { t } = useLanguage();

  return (
    <div data-testid={TEST_IDS.page.home}>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0">
          <img
            src={HERO_IMAGE}
            alt="Macro crystal"
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-background/70 backdrop-blur-[1px]" />
          <div className="absolute inset-0 bg-gradient-to-t from-background via-background/40 to-transparent" />
        </div>

        <div className="relative mx-auto flex min-h-[82vh] max-w-7xl flex-col justify-center px-6 py-24 md:px-10">
          <div className="mb-8 flex items-center gap-3 text-primary">
            <Sparkle size={20} weight="duotone" />
            <span className="text-xs uppercase tracking-[0.35em]">
              {t("footer.established")}
            </span>
          </div>

          <h1 className="max-w-4xl font-serif text-6xl font-light leading-[0.95] tracking-tighter md:text-8xl">
            {t("brand")}
          </h1>

          <p className="mt-8 max-w-xl text-lg leading-relaxed text-muted-foreground md:text-xl">
            {t("tagline")}
          </p>

          <div className="mt-12 flex flex-wrap items-center gap-4">
            <Link
              to="/catalog"
              data-testid={TEST_IDS.common.ctaHome}
              className="group inline-flex items-center gap-3 rounded-full bg-primary px-8 py-4 text-xs uppercase tracking-[0.2em] text-primary-foreground transition-all duration-500 hover:gap-4"
            >
              {t("nav.catalog")}
              <ArrowRight size={16} weight="bold" />
            </Link>
            <Link
              to="/verification"
              data-testid={TEST_IDS.common.ctaVerify}
              className="inline-flex items-center gap-3 rounded-full border border-primary/40 px-8 py-4 text-xs uppercase tracking-[0.2em] text-primary transition-all duration-500 hover:bg-primary/10"
            >
              <ShieldCheck size={18} weight="duotone" />
              {t("nav.verification")}
            </Link>
          </div>

          <p className="mt-16 text-xs uppercase tracking-[0.3em] text-muted-foreground">
            {t("sprintNotice")}
          </p>
        </div>
      </section>
    </div>
  );
}
