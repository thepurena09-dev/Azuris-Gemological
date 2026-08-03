import { Link } from "react-router-dom";
import {
  ShieldCheck,
  ArrowRight,
  Diamond,
  Medal,
  GlobeHemisphereWest,
  Shield,
} from "@phosphor-icons/react";
import type { Icon } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

const HERO_IMAGE =
  "https://static.prod-images.emergentagent.com/jobs/0d8170c5-08d6-45ed-9937-114710780b07/images/4b2af966dff0609c424ad0916be569527aa95a96a9218ce74111ead9a08b4b8d.jpeg";

export default function HomePage() {
  const { t } = useLanguage();

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
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0">
          <img src={HERO_IMAGE} alt="Blue sapphire" className="h-full w-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-r from-background via-background/85 to-transparent" />
        </div>

        <div className="relative mx-auto max-w-7xl px-6 pb-40 pt-24 md:px-10 md:pb-48 md:pt-32">
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
            </div>
          </div>
        </div>
      </section>

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
