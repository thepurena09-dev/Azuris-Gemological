import { Link, Outlet, NavLink } from "react-router-dom";
import { Gauge, MagnifyingGlass, Bell, Certificate, Gear, SignOut, SealCheck, Users, Diamond, Crown, ShieldCheck, ArrowsLeftRight, IdentificationCard, Image as ImageIcon } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { useAuth } from "@/lib/auth";

const MARBLE_BG =
  "https://static.prod-images.emergentagent.com/jobs/6572b450-f0e7-4d20-83da-0f44a5e44dfd/images/df3161b0cd73f56ca5ed2325b394244a0bc533006164f0b288a0bd38c33fcfef.jpeg";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `relative flex items-center gap-3 rounded-lg px-4 py-3 text-xs uppercase tracking-[0.15em] transition-colors duration-300 ${
    isActive ? "bg-white/5 text-gold" : "text-primary-foreground/60 hover:text-primary-foreground"
  }`;

export default function AdminLayout() {
  const { t } = useLanguage();
  const { logout } = useAuth();

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
        <Link to="/" className="mb-10 flex items-center gap-3">
          <img
            src="/azuris-logo.png"
            alt="Azuris Gemological"
            width={34}
            height={34}
            className="h-[34px] w-[34px] object-contain"
            data-testid="admin-logo"
          />
          <span className="flex flex-col leading-none">
            <span className="font-serif text-xl font-semibold tracking-tight">
              AZURIS
            </span>
            <span className="mt-1.5 block text-[0.5rem] uppercase tracking-[0.4em] text-primary-foreground/50">
              {t("admin.title")}
            </span>
          </span>
        </Link>

        <nav className="flex flex-col gap-1.5 border-t border-primary-foreground/10 pt-8">
          <NavLink to="/admin/dashboard" data-testid={TEST_IDS.admin.navDashboard} className={navLinkClass}>
            <Gauge size={18} weight="regular" />
            {t("admin.dashboard")}
          </NavLink>
          <NavLink to="/admin/legalitas" data-testid={TEST_IDS.admin.navLegality} className={navLinkClass}>
            <Certificate size={18} weight="regular" />
            {t("adminNav.legality")}
          </NavLink>
          <NavLink to="/admin/certificates" data-testid={TEST_IDS.admin.navCertificates} className={navLinkClass}>
            <SealCheck size={18} weight="regular" />
            {t("adminCert.navTitle")}
          </NavLink>
          <NavLink to="/admin/customers" data-testid={TEST_IDS.admin.navCustomers} className={navLinkClass}>
            <Users size={18} weight="regular" />
            {t("adminNav.customers")}
          </NavLink>
          <NavLink to="/admin/gemstones" data-testid={TEST_IDS.admin.navGemstones} className={navLinkClass}>
            <Diamond size={18} weight="regular" />
            {t("adminNav.gemstones")}
          </NavLink>
          <NavLink to="/admin/jewelry" data-testid={TEST_IDS.admin.navJewelry} className={navLinkClass}>
            <Crown size={18} weight="regular" />
            {t("adminNav.jewelry")}
          </NavLink>
          <NavLink to="/admin/warranties" data-testid={TEST_IDS.admin.navWarranties} className={navLinkClass}>
            <ShieldCheck size={18} weight="regular" />
            {t("adminNav.warranties")}
          </NavLink>
          <NavLink to="/admin/ownership" data-testid={TEST_IDS.admin.navOwnership} className={navLinkClass}>
            <ArrowsLeftRight size={18} weight="regular" />
            {t("adminNav.ownership")}
          </NavLink>
          <NavLink to="/admin/membership" data-testid={TEST_IDS.admin.navMembership} className={navLinkClass}>
            <IdentificationCard size={18} weight="regular" />
            {t("adminNav.membership")}
          </NavLink>
          <NavLink to="/admin/visuals" data-testid={TEST_IDS.admin.navVisuals} className={navLinkClass}>
            <ImageIcon size={18} weight="regular" />
            {t("adminVisuals.navTitle")}
          </NavLink>
          <NavLink to="/admin/settings" data-testid={TEST_IDS.admin.navSettings} className={navLinkClass}>
            <Gear size={18} weight="regular" />
            {t("adminNav.settings")}
          </NavLink>
        </nav>

        <button
          type="button"
          data-testid={TEST_IDS.admin.logout}
          onClick={logout}
          className="mt-auto flex items-center gap-2 text-[0.7rem] uppercase tracking-[0.15em] text-primary-foreground/50 transition-colors hover:text-primary-foreground"
        >
          <SignOut size={16} weight="thin" />
          {t("auth.logout")}
        </button>
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
            <span className="flex h-10 w-10 items-center justify-center rounded-full border border-gold/40 bg-secondary">
              <img
                src="/azuris-logo.png"
                alt="Azuris"
                width={24}
                height={24}
                className="h-6 w-6 object-contain"
              />
            </span>
          </div>
        </header>

        <main className="relative min-w-0 flex-1 bg-secondary">
          {/* Refined marble veining — subtle, premium, readability preserved */}
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 bg-cover bg-center opacity-[0.10] mix-blend-multiply"
            style={{ backgroundImage: `url(${MARBLE_BG})`, filter: "contrast(1.25) saturate(0.9)" }}
          />
          <div className="relative">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
