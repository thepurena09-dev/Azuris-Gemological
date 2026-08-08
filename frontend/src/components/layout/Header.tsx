import { Link, NavLink } from "react-router-dom";
import { useState } from "react";
import { List, X, Diamond, UserCircle } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import LanguageSwitcher from "@/components/layout/LanguageSwitcher";

const navItems = [
  { to: "/", key: "nav.home", testId: TEST_IDS.header.navHome, type: "route" as const, end: true },
  { to: "/#verification", key: "nav.verification", testId: TEST_IDS.header.navVerification, type: "hash" as const },
  { to: "/#proses", key: "nav.process", testId: TEST_IDS.header.navProcess, type: "hash" as const },
  { to: "/legalitas", key: "nav.legality", testId: TEST_IDS.header.navLegality, type: "route" as const },
  { to: "/about", key: "nav.about", testId: TEST_IDS.header.navAbout, type: "route" as const },
  { to: "/contact", key: "nav.contact", testId: TEST_IDS.header.navContact, type: "route" as const },
];

export default function Header() {
  const { t } = useLanguage();
  const [open, setOpen] = useState(false);

  return (
    <div className="sticky top-0 z-50">
      {/* Announcement bar */}
      <div className="bg-primary">
        <div className="mx-auto flex h-9 max-w-7xl items-center gap-3 px-6 md:px-10">
          <Diamond size={13} weight="fill" className="text-gold" />
          <span className="text-[0.62rem] uppercase tracking-[0.35em] text-gold">
            {t("footer.established")}
          </span>
        </div>
      </div>

      {/* Main header */}
      <header
        data-testid={TEST_IDS.header.root}
        className="border-b border-border bg-background"
      >
        <div className="mx-auto grid h-24 max-w-7xl grid-cols-[1fr_auto_1fr] items-center px-6 md:px-10">
          {/* Logo left */}
          <Link
            to="/"
            data-testid={TEST_IDS.header.brand}
            className="group flex w-fit items-center gap-3"
          >
            <Diamond size={30} weight="fill" className="text-gold" />
            <span className="flex flex-col leading-none">
              <span className="font-serif text-[1.6rem] font-semibold tracking-tight text-foreground transition-colors duration-300 group-hover:text-royal">
                AZURIS
              </span>
              <span className="mt-1 text-[0.5rem] uppercase tracking-[0.5em] text-muted-foreground">
                Gemological
              </span>
            </span>
          </Link>

          {/* Navigation center */}
          <nav className="hidden items-center gap-9 lg:flex">
            {navItems.map((item) =>
              item.type === "route" ? (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  data-testid={item.testId}
                  className={({ isActive }) =>
                    `relative py-2 text-[0.72rem] uppercase tracking-[0.2em] transition-colors duration-300 ${
                      isActive ? "text-foreground" : "text-muted-foreground hover:text-foreground"
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      {t(item.key)}
                      {isActive && (
                        <span className="absolute -bottom-0.5 left-1/2 h-0.5 w-6 -translate-x-1/2 rounded-full bg-gold" />
                      )}
                    </>
                  )}
                </NavLink>
              ) : (
                <Link
                  key={item.to}
                  to={item.to}
                  data-testid={item.testId}
                  className="py-2 text-[0.72rem] uppercase tracking-[0.2em] text-muted-foreground transition-colors duration-300 hover:text-foreground"
                >
                  {t(item.key)}
                </Link>
              )
            )}
          </nav>

          {/* Actions right */}
          <div className="flex items-center justify-end gap-5">
            <LanguageSwitcher />
            <Link
              to="/login"
              data-testid={TEST_IDS.header.navLogin}
              className="hidden items-center gap-2 rounded-lg bg-primary px-5 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground shadow-sm transition-shadow duration-300 hover:shadow-lg sm:inline-flex"
            >
              <UserCircle size={16} weight="regular" />
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
          <div className="border-t border-border bg-background px-6 py-6 lg:hidden">
            <nav className="flex flex-col gap-5">
              {navItems.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  data-testid={`${item.testId}-mobile`}
                  onClick={() => setOpen(false)}
                  className="text-sm uppercase tracking-[0.22em] text-muted-foreground transition-colors hover:text-foreground"
                >
                  {t(item.key)}
                </Link>
              ))}
              <Link
                to="/login"
                onClick={() => setOpen(false)}
                className="mt-2 rounded-lg bg-primary px-6 py-3 text-center text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground"
              >
                {t("nav.login")}
              </Link>
            </nav>
          </div>
        )}
      </header>
    </div>
  );
}
