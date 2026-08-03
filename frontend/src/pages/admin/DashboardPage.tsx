import { Sparkle } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

export default function DashboardPage() {
  const { t } = useLanguage();

  return (
    <section
      data-testid={TEST_IDS.page.adminDashboard}
      className="px-8 py-16 md:px-12"
    >
      <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">
        {t("admin.title")}
      </p>
      <h1 className="mt-3 font-serif text-5xl font-light tracking-tighter">
        {t("admin.dashboard")}
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
