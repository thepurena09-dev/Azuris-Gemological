import { Link } from "react-router-dom";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

export default function NotFoundPage() {
  const { t } = useLanguage();

  return (
    <div
      data-testid={TEST_IDS.page.notFound}
      className="flex min-h-screen flex-col items-start justify-center bg-background px-8 md:px-24"
    >
      <p className="font-serif text-[8rem] font-light leading-none tracking-tighter text-primary/70">
        404
      </p>
      <p className="mt-4 max-w-md text-lg text-muted-foreground">
        {t("comingSoon")}
      </p>
      <Link
        to="/"
        className="mt-10 rounded-full border border-primary/40 px-8 py-4 text-xs uppercase tracking-[0.2em] text-primary transition-all duration-500 hover:bg-primary hover:text-primary-foreground"
      >
        {t("nav.home")}
      </Link>
    </div>
  );
}
