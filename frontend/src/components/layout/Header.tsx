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
          <nav className="hidden items-center gap-2.5 lg:flex">
            {navItems.map((item) => {
              const base =
                "rounded-lg border border-gold/20 px-3.5 py-2 text-[0.66rem] uppercase tracking-[0.16em] transition-[color,box-shadow,transform,background-color] duration-300 will-change-transform";
              const normal =
                "bg-gradient-to-b from-white to-muted text-muted-foreground shadow-[0_1px_1px_rgba(24,42,64,0.04),0_2px_4px_rgba(24,42,64,0.06),inset_0_1px_0_rgba(255,255,255,0.85)] hover:-translate-y-px hover:text-foreground hover:shadow-[0_2px_4px_rgba(24,42,64,0.06),0_5px_12px_rgba(24,42,64,0.09),inset_0_1px_0_rgba(255,255,255,0.95)] active:translate-y-0 active:shadow-[inset_0_2px_4px_rgba(24,42,64,0.10)]";
              const active =
                "border-gold/45 bg-gold/10 text-foreground shadow-[inset_0_1px_3px_rgba(24,42,64,0.12),inset_0_-1px_0_rgba(255,255,255,0.5)]";
              return item.type === "route" ? (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  data-testid={item.testId}
                  className={({ isActive }) => `${base} ${isActive ? active : normal}`}
                >
                  {t(item.key)}
                </NavLink>
              ) : (
                <Link
                  key={item.to}
                  to={item.to}
                  data-testid={item.testId}
                  className={`${base} ${normal}`}
                >
                  {t(item.key)}
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
          <div className="border-t border-border bg-background px-5 py-6 sm:px-6 md:px-10 lg:hidden">
            <nav className="flex flex-col gap-3">
              {navItems.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  data-testid={`${item.testId}-mobile`}
                  onClick={() => setOpen(false)}
                  className="rounded-lg border border-gold/20 bg-gradient-to-b from-white to-muted px-4 py-3.5 text-sm uppercase tracking-[0.18em] text-muted-foreground shadow-[0_1px_1px_rgba(24,42,64,0.04),0_2px_4px_rgba(24,42,64,0.06),inset_0_1px_0_rgba(255,255,255,0.85)] transition-[color,box-shadow] duration-300 hover:text-foreground active:shadow-[inset_0_2px_4px_rgba(24,42,64,0.10)]"
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
