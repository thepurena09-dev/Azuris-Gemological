import { Link } from "react-router-dom";
import { ArrowLeft, Lock } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import LanguageSwitcher from "@/components/layout/LanguageSwitcher";
import { TEST_IDS } from "@/constants/testIds";

const PANEL_IMAGE =
  "https://images.unsplash.com/photo-1521133573892-e44906baee46?auto=format&fit=crop&w=1200&q=80";

export default function LoginPage() {
  const { t } = useLanguage();

  return (
    <div
      data-testid={TEST_IDS.page.login}
      className="grid min-h-screen bg-background lg:grid-cols-2"
    >
      {/* Brand panel */}
      <div className="relative hidden overflow-hidden lg:block">
        <img
          src={PANEL_IMAGE}
          alt="Gemstone"
          className="h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-background/60" />
        <div className="absolute inset-0 flex flex-col justify-between p-12">
          <Link to="/" className="flex flex-col leading-none">
            <span className="font-serif text-2xl font-light tracking-tighter">
              AZURIS
            </span>
            <span className="mt-1 text-[0.6rem] uppercase tracking-[0.35em] text-muted-foreground">
              Gemological
            </span>
          </Link>
          <p className="max-w-sm font-serif text-3xl font-light tracking-tighter">
            {t("tagline")}
          </p>
        </div>
      </div>

      {/* Form panel */}
      <div className="flex flex-col justify-center px-8 py-16 md:px-16">
        <div className="mb-10 flex items-center justify-between">
          <Link
            to="/"
            className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft size={16} weight="thin" />
            {t("nav.home")}
          </Link>
          <LanguageSwitcher />
        </div>

        <div className="max-w-sm">
          <div className="mb-6 inline-flex items-center gap-3 text-primary">
            <Lock size={22} weight="duotone" />
            <span className="text-xs uppercase tracking-[0.3em]">
              {t("admin.title")}
            </span>
          </div>
          <h1 className="font-serif text-5xl font-light tracking-tighter">
            {t("nav.login")}
          </h1>
          <p
            data-testid={TEST_IDS.common.comingSoon}
            className="mt-10 border-l border-primary/40 pl-6 text-lg leading-relaxed text-muted-foreground"
          >
            {t("comingSoon")}
          </p>
          <p className="mt-8 text-xs uppercase tracking-[0.3em] text-muted-foreground">
            {t("sprintNotice")}
          </p>
        </div>
      </div>
    </div>
  );
}
