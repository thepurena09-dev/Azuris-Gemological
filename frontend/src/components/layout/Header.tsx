import { Link, NavLink } from "react-router-dom";
import { useState } from "react";
import { List, X, Diamond } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import LanguageSwitcher from "@/components/layout/LanguageSwitcher";
import { Logo } from "@/components/common/Logo";

const navItems = [
  { to: "/", key: "nav.home", testId: TEST_IDS.header.navHome, type: "route" as const, end: true },
  { to: "/verify", key: "nav.verification", testId: TEST_IDS.header.navVerification, type: "route" as const },
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
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between gap-2 px-5 sm:px-6 md:h-24 md:px-10 lg:grid lg:grid-cols-[1fr_auto_1fr] lg:gap-0">
          {/* Logo left */}
          <Link
            to="/"
            data-testid={TEST_IDS.header.brand}
            className="group flex w-fit shrink-0 items-center"
          >
            <Logo size={38} className="sm:hidden" testId="azuris-logo-m" />
            <Logo size={46} className="hidden sm:flex" />
          </Link>

          {/* Navigation center */}
          <nav className="hidden items-center gap-7 lg:flex xl:gap-9">
            {navItems.map((item) => {
              const emboss = {
                textShadow:
                  "0 1px 0 rgba(255,255,255,0.9), 0 -0.5px 0 rgba(13,27,42,0.16)",
              };
              const base =
                "group relative rounded-sm text-[0.7rem] font-semibold uppercase tracking-[0.2em] outline-none transition-colors duration-300 focus-visible:ring-2 focus-visible:ring-gold/70 focus-visible:ring-offset-2 focus-visible:ring-offset-background";
              const label = (isActive: boolean) => (
                <span className="relative inline-block py-1">
                  {t(item.key)}
                  <span
                    className={`pointer-events-none absolute -bottom-0.5 left-0 h-px bg-gold transition-all duration-300 ${
                      isActive ? "w-full" : "w-0 group-hover:w-full"
                    }`}
                  />
                </span>
              );
              return item.type === "route" ? (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  data-testid={item.testId}
                  style={emboss}
                  className={({ isActive }) =>
                    `${base} ${isActive ? "text-gold" : "text-foreground hover:text-gold"}`
                  }
                >
                  {({ isActive }) => label(isActive)}
                </NavLink>
              ) : (
                <Link
                  key={item.to}
                  to={item.to}
                  data-testid={item.testId}
                  style={emboss}
                  className={`${base} text-foreground hover:text-gold`}
                >
                  {label(false)}
                </Link>
              );
            })}
          </nav>

          {/* Actions right */}
          <div className="flex shrink-0 items-center justify-end gap-2 sm:gap-3 lg:gap-5">
            <LanguageSwitcher />
            <button
              type="button"
              data-testid={TEST_IDS.header.mobileToggle}
              onClick={() => setOpen((v) => !v)}
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg text-foreground transition-colors hover:bg-gold/10 lg:hidden"
              aria-label="Toggle navigation"
            >
              {open ? <X size={24} weight="thin" /> : <List size={24} weight="thin" />}
            </button>
          </div>
        </div>

        {open && (
          <div className="border-t border-border bg-background px-5 py-4 sm:px-6 md:px-10 lg:hidden">
            <nav className="flex flex-col">
              {navItems.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  data-testid={`${item.testId}-mobile`}
                  onClick={() => setOpen(false)}
                  style={{ textShadow: "0 1px 0 rgba(255,255,255,0.9)" }}
                  className="border-b border-border/60 py-3.5 text-sm font-semibold uppercase tracking-[0.2em] text-foreground outline-none transition-colors last:border-0 hover:text-gold focus-visible:text-gold focus-visible:ring-2 focus-visible:ring-gold/70"
                >
                  {t(item.key)}
                </Link>
              ))}
            </nav>
          </div>
        )}
      </header>
    </div>
  );
}
