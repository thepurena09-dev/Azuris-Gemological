import { Link, NavLink } from "react-router-dom";
import { useState } from "react";
import { List, X } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import LanguageSwitcher from "@/components/layout/LanguageSwitcher";

const navItems = [
  { to: "/", key: "nav.home", testId: TEST_IDS.header.navHome, end: true },
  { to: "/catalog", key: "nav.catalog", testId: TEST_IDS.header.navCatalog, end: false },
  { to: "/verification", key: "nav.verification", testId: TEST_IDS.header.navVerification, end: false },
  { to: "/about", key: "nav.about", testId: TEST_IDS.header.navAbout, end: false },
  { to: "/contact", key: "nav.contact", testId: TEST_IDS.header.navContact, end: false },
];

export default function Header() {
  const { t } = useLanguage();
  const [open, setOpen] = useState(false);

  return (
    <header
      data-testid={TEST_IDS.header.root}
      className="sticky top-0 z-50 border-b border-border/60 bg-background/70 backdrop-blur-xl"
    >
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6 md:px-10">
        <Link
          to="/"
          data-testid={TEST_IDS.header.brand}
          className="group flex flex-col leading-none"
        >
          <span className="font-serif text-2xl font-light tracking-tighter text-foreground transition-colors duration-500 group-hover:text-primary">
            AZURIS
          </span>
          <span className="mt-1 text-[0.6rem] uppercase tracking-[0.35em] text-muted-foreground">
            Gemological
          </span>
        </Link>

        <nav className="hidden items-center gap-9 lg:flex">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              data-testid={item.testId}
              className={({ isActive }) =>
                `relative text-xs uppercase tracking-[0.2em] transition-colors duration-500 ${
                  isActive
                    ? "text-primary"
                    : "text-muted-foreground hover:text-foreground"
                }`
              }
            >
              {t(item.key)}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-4">
          <LanguageSwitcher />
          <Link
            to="/login"
            data-testid={TEST_IDS.header.navLogin}
            className="hidden rounded-full border border-primary/40 px-5 py-2 text-xs uppercase tracking-[0.2em] text-primary transition-all duration-500 hover:bg-primary hover:text-primary-foreground sm:inline-block"
          >
            {t("nav.login")}
          </Link>
          <button
            type="button"
            data-testid={TEST_IDS.header.mobileToggle}
            onClick={() => setOpen((v) => !v)}
            className="text-foreground lg:hidden"
            aria-label="Toggle navigation"
          >
            {open ? <X size={24} weight="thin" /> : <List size={24} weight="thin" />}
          </button>
        </div>
      </div>

      {open && (
        <div className="border-t border-border/60 bg-background/95 px-6 py-6 lg:hidden">
          <nav className="flex flex-col gap-5">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `text-sm uppercase tracking-[0.2em] ${
                    isActive ? "text-primary" : "text-muted-foreground"
                  }`
                }
              >
                {t(item.key)}
              </NavLink>
            ))}
            <Link
              to="/login"
              onClick={() => setOpen(false)}
              className="mt-2 rounded-full border border-primary/40 px-5 py-2 text-center text-xs uppercase tracking-[0.2em] text-primary"
            >
              {t("nav.login")}
            </Link>
          </nav>
        </div>
      )}
    </header>
  );
}
