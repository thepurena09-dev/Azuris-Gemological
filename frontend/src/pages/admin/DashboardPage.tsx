import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

export default function DashboardPage() {
  const { t } = useLanguage();

  return (
    <section
      data-testid={TEST_IDS.page.adminDashboard}
      className="px-6 py-10 md:px-10 md:py-14"
    >
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">
        {t("admin.title")}
      </p>
      <h1 className="mt-3 font-serif text-4xl font-normal tracking-tight md:text-5xl">
        {t("admin.dashboard")}
      </h1>

      <div className="mt-10 rounded-2xl border border-border bg-card p-10 shadow-[0_20px_60px_-40px_rgba(13,27,42,0.35)] md:p-14">
        <div className="mb-6 flex items-center gap-4">
          <span className="h-px w-12 bg-gold" />
          <span className="text-[0.7rem] uppercase tracking-[0.4em] text-gold">
            {t("sprintNotice")}
          </span>
        </div>
        <p
          data-testid={TEST_IDS.common.comingSoon}
          className="max-w-2xl text-lg font-light leading-relaxed text-muted-foreground"
        >
          {t("comingSoon")}
        </p>
      </div>
    </section>
  );
}
