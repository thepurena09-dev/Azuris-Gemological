import { Link, Outlet, NavLink } from "react-router-dom";
import { Gauge, ArrowLeft } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

export default function AdminLayout() {
  const { t } = useLanguage();

  return (
    <div
      data-testid={TEST_IDS.admin.layout}
      className="flex min-h-screen bg-background text-foreground"
    >
      <aside
        data-testid={TEST_IDS.admin.sidebar}
        className="hidden w-64 shrink-0 flex-col border-r border-border/60 bg-secondary/20 p-6 md:flex"
      >
        <Link to="/" className="mb-12 block">
          <span className="font-serif text-xl font-light tracking-tighter">
            AZURIS
          </span>
          <span className="mt-1 block text-[0.55rem] uppercase tracking-[0.3em] text-muted-foreground">
            {t("admin.title")}
          </span>
        </Link>

        <nav className="flex flex-col gap-1">
          <NavLink
            to="/admin/dashboard"
            data-testid={TEST_IDS.admin.navDashboard}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-sm px-3 py-2.5 text-xs uppercase tracking-[0.15em] transition-colors duration-300 ${
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:text-foreground"
              }`
            }
          >
            <Gauge size={18} weight="duotone" />
            {t("admin.dashboard")}
          </NavLink>
        </nav>

        <Link
          to="/"
          className="mt-auto flex items-center gap-2 text-xs uppercase tracking-[0.15em] text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft size={16} weight="thin" />
          {t("nav.home")}
        </Link>
      </aside>

      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
