import { Link } from "react-router-dom";
import { CaretRight } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

interface Crumb {
  label: string;
  to?: string;
}

interface PlaceholderPageProps {
  title: string;
  testId: string;
  breadcrumbs?: Crumb[];
}

export default function PlaceholderPage({
  title,
  testId,
  breadcrumbs = [],
}: PlaceholderPageProps) {
  const { t } = useLanguage();

  return (
    <section
      data-testid={testId}
      className="mx-auto max-w-7xl px-6 py-28 md:px-10 md:py-40"
    >
      <nav
        data-testid={TEST_IDS.common.breadcrumb}
        className="mb-12 flex items-center text-[0.7rem] uppercase tracking-[0.25em] text-muted-foreground"
      >
        <Link to="/" className="transition-colors hover:text-foreground">
          {t("breadcrumbHome")}
        </Link>
        {breadcrumbs.map((crumb) => (
          <span key={crumb.label} className="flex items-center">
            <CaretRight size={11} weight="bold" className="mx-3 text-gold" />
            {crumb.to ? (
              <Link to={crumb.to} className="transition-colors hover:text-foreground">
                {crumb.label}
              </Link>
            ) : (
              <span className="text-foreground">{crumb.label}</span>
            )}
          </span>
        ))}
      </nav>

      <div className="flex items-center gap-4">
        <span className="h-px w-10 bg-gold" />
        <span className="text-[0.7rem] uppercase tracking-[0.4em] text-gold">
          {t("sprintNotice")}
        </span>
      </div>

      <h1 className="mt-8 max-w-4xl font-serif text-6xl font-normal leading-[1.03] tracking-tight md:text-8xl">
        {title}
      </h1>

      <p
        data-testid={TEST_IDS.common.comingSoon}
        className="mt-14 max-w-2xl text-xl font-light leading-relaxed text-muted-foreground"
      >
        {t("comingSoon")}
      </p>
    </section>
  );
}
