import { Link } from "react-router-dom";
import { ShieldCheck, Certificate, FileDashed, Info } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

export default function LegalityPage() {
  const { t } = useLanguage();

  return (
    <div data-testid={TEST_IDS.legality.page} className="bg-background">
      {/* Hero */}
      <section className="border-b border-border bg-secondary">
        <div className="mx-auto max-w-5xl px-6 py-24 text-center md:px-10 md:py-28">
          <div className="mb-6 flex items-center justify-center gap-4">
            <span className="h-px w-10 bg-gold" />
            <span className="text-[0.68rem] uppercase tracking-[0.4em] text-gold">
              {t("legalityTeaser.eyebrow")}
            </span>
            <span className="h-px w-10 bg-gold" />
          </div>
          <h1 className="mx-auto max-w-3xl font-serif text-4xl font-normal leading-[1.08] tracking-tight text-foreground md:text-6xl">
            {t("legality.title")}
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-muted-foreground">
            {t("legality.subtitle")}
          </p>
          <Link
            to="/#verification"
            data-testid={TEST_IDS.legality.ctaVerify}
            className="mt-9 inline-flex items-center gap-3 rounded-lg bg-primary px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground transition-shadow duration-300 hover:shadow-xl"
          >
            <ShieldCheck size={16} weight="regular" className="text-gold" />
            {t("legality.ctaVerify")}
          </Link>
        </div>
      </section>

      {/* Certificate viewer — premium placeholder (no document published yet) */}
      <section className="mx-auto max-w-5xl px-6 py-20 md:px-10 md:py-24">
        <div className="mb-8 flex items-center gap-4">
          <span className="h-px w-10 bg-gold" />
          <span className="text-[0.68rem] uppercase tracking-[0.4em] text-gold">
            {t("legality.viewerTitle")}
          </span>
        </div>

        <div
          data-testid={TEST_IDS.legality.viewer}
          className="relative overflow-hidden rounded-2xl border border-border bg-card p-10 shadow-[0_30px_70px_-45px_rgba(13,27,42,0.4)] md:p-16"
        >
          <div className="pointer-events-none absolute -right-24 -top-28 h-80 w-80 rounded-full bg-gold/10 blur-3xl" />
          <div className="relative flex flex-col items-center justify-center rounded-xl border border-dashed border-border bg-secondary/60 px-8 py-20 text-center">
            <span className="flex h-16 w-16 items-center justify-center rounded-full border border-gold/40 bg-background">
              <FileDashed size={30} weight="thin" className="text-gold" />
            </span>
            <p className="mt-7 font-serif text-2xl font-normal tracking-tight text-foreground">
              {t("legality.emptyTitle")}
            </p>
            <p className="mt-4 max-w-xl text-sm leading-relaxed text-muted-foreground">
              {t("legality.empty")}
            </p>
          </div>
        </div>
      </section>

      {/* Commitment + disclaimer */}
      <section className="border-t border-border bg-secondary/40">
        <div className="mx-auto grid max-w-5xl gap-10 px-6 py-20 md:grid-cols-2 md:px-10 md:py-24">
          <div>
            <div className="flex items-center gap-3">
              <Certificate size={20} weight="regular" className="text-gold" />
              <h2 className="text-xs uppercase tracking-[0.25em] text-foreground">
                {t("legality.copyTitle")}
              </h2>
            </div>
            <p className="mt-5 text-sm leading-relaxed text-muted-foreground">
              {t("legality.copy")}
            </p>
          </div>
          <div className="rounded-2xl border border-border bg-card p-7">
            <div className="flex items-center gap-3">
              <Info size={20} weight="regular" className="text-gold" />
              <h2 className="text-xs uppercase tracking-[0.25em] text-foreground">
                {t("legality.disclaimerTitle")}
              </h2>
            </div>
            <p className="mt-5 text-sm leading-relaxed text-muted-foreground">
              {t("legality.disclaimer")}
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
