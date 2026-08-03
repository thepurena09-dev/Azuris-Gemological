import { Link } from "react-router-dom";
import { ArrowLeft, Lock } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import LanguageSwitcher from "@/components/layout/LanguageSwitcher";
import { TEST_IDS } from "@/constants/testIds";

const PANEL_IMAGE =
  "https://images.unsplash.com/photo-1587947330318-88fcd9055420?crop=entropy&cs=srgb&fm=jpg&q=90&w=1400";

export default function LoginPage() {
  const { t } = useLanguage();

  return (
    <div
      data-testid={TEST_IDS.page.login}
      className="grid min-h-screen bg-background lg:grid-cols-2"
    >
      {/* Brand panel — bright imagery */}
      <div className="relative hidden overflow-hidden bg-secondary lg:block">
        <img
          src={PANEL_IMAGE}
          alt="Diamond jewelry"
          className="h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background/50 via-transparent to-transparent" />
        <div className="absolute inset-0 flex flex-col justify-between p-14">
          <Link to="/" className="flex flex-col leading-none">
            <span className="font-serif text-2xl font-medium tracking-tight text-foreground">
              AZURIS
            </span>
            <span className="mt-1.5 text-[0.55rem] uppercase tracking-[0.45em] text-muted-foreground">
              Gemological
            </span>
          </Link>
          <p className="max-w-sm font-serif text-4xl font-normal leading-tight tracking-tight text-foreground">
            {t("tagline")}
          </p>
        </div>
      </div>

      {/* Form panel */}
      <div className="flex flex-col justify-center px-8 py-16 md:px-20">
        <div className="mb-14 flex items-center justify-between">
          <Link
            to="/"
            className="flex items-center gap-2 text-[0.7rem] uppercase tracking-[0.25em] text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft size={16} weight="thin" />
            {t("nav.home")}
          </Link>
          <LanguageSwitcher />
        </div>

        <div className="max-w-sm">
          <div className="mb-6 flex items-center gap-4">
            <span className="h-px w-10 bg-gold" />
            <span className="flex items-center gap-2 text-[0.7rem] uppercase tracking-[0.3em] text-gold">
              <Lock size={16} weight="regular" />
              {t("admin.title")}
            </span>
          </div>
          <h1 className="font-serif text-6xl font-normal tracking-tight">
            {t("nav.login")}
          </h1>
          <p
            data-testid={TEST_IDS.common.comingSoon}
            className="mt-12 text-lg font-light leading-relaxed text-muted-foreground"
          >
            {t("comingSoon")}
          </p>
          <p className="mt-10 text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground/70">
            {t("sprintNotice")}
          </p>
        </div>
      </div>
    </div>
  );
}
