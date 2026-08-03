import { Link, Outlet, NavLink } from "react-router-dom";
import { Gauge, ArrowLeft, MagnifyingGlass, Bell } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

export default function AdminLayout() {
  const { t } = useLanguage();

  return (
    <div
      data-testid={TEST_IDS.admin.layout}
      className="flex min-h-screen bg-secondary text-foreground"
    >
      {/* Deep Navy sidebar */}
      <aside
        data-testid={TEST_IDS.admin.sidebar}
        className="hidden w-72 shrink-0 flex-col bg-primary p-7 text-primary-foreground md:flex"
      >
        <Link to="/" className="mb-14 block">
          <span className="font-serif text-2xl font-semibold tracking-tight">
            AZURIS
          </span>
          <span className="mt-1.5 block text-[0.55rem] uppercase tracking-[0.4em] text-primary-foreground/50">
            {t("admin.title")}
          </span>
        </Link>

        <nav className="flex flex-col gap-1.5">
          <NavLink
            to="/admin/dashboard"
            data-testid={TEST_IDS.admin.navDashboard}
            className={({ isActive }) =>
              `relative flex items-center gap-3 rounded-lg px-4 py-3 text-xs uppercase tracking-[0.15em] transition-colors duration-300 ${
                isActive
                  ? "bg-white/5 text-gold"
                  : "text-primary-foreground/60 hover:text-primary-foreground"
              }`
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <span className="absolute left-0 top-1/2 h-6 w-1 -translate-y-1/2 rounded-r bg-gold" />
                )}
                <Gauge size={18} weight="regular" />
                {t("admin.dashboard")}
              </>
            )}
          </NavLink>
        </nav>

        <Link
          to="/"
          className="mt-auto flex items-center gap-2 text-[0.7rem] uppercase tracking-[0.15em] text-primary-foreground/50 transition-colors hover:text-primary-foreground"
        >
          <ArrowLeft size={16} weight="thin" />
          {t("nav.home")}
        </Link>
      </aside>

      {/* Workspace */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* White topbar */}
        <header className="flex h-20 items-center justify-between gap-6 border-b border-border bg-background px-6 md:px-10">
          <div className="flex max-w-md flex-1 items-center gap-3 rounded-lg border border-border bg-secondary px-4 py-2.5 text-muted-foreground">
            <MagnifyingGlass size={16} weight="regular" />
            <span className="text-sm">Search…</span>
          </div>
          <div className="flex items-center gap-5">
            <Bell size={20} weight="regular" className="text-muted-foreground" />
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-xs font-semibold tracking-wide text-primary-foreground">
              AZ
            </span>
          </div>
        </header>

        <main className="min-w-0 flex-1 bg-secondary">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
