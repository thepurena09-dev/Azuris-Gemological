import { Link } from "react-router-dom";
import { CaretRight, Sparkle } from "@phosphor-icons/react";
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
    <section data-testid={testId} className="mx-auto max-w-7xl px-6 py-24 md:px-10 md:py-32">
      <nav
        data-testid={TEST_IDS.common.breadcrumb}
        className="mb-10 flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-muted-foreground"
      >
        <Link to="/" className="transition-colors hover:text-foreground">
          {t("breadcrumbHome")}
        </Link>
        {breadcrumbs.map((crumb) => (
          <span key={crumb.label} className="flex items-center">
            <CaretRight size={12} weight="bold" className="mx-3 text-primary/60" />
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

      <h1 className="max-w-3xl font-serif text-5xl font-light tracking-tighter md:text-6xl">
        {title}
      </h1>

      <div className="mt-16 max-w-2xl border-l border-primary/40 pl-8">
        <div className="mb-5 flex items-center gap-3 text-primary">
          <Sparkle size={22} weight="duotone" />
          <span className="text-xs uppercase tracking-[0.3em]">
            {t("sprintNotice")}
          </span>
        </div>
        <p
          data-testid={TEST_IDS.common.comingSoon}
          className="text-lg leading-relaxed text-muted-foreground"
        >
          {t("comingSoon")}
        </p>
      </div>
    </section>
  );
}
