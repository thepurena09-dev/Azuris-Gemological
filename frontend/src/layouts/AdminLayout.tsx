import { useState } from "react";
import { Link, Outlet, NavLink } from "react-router-dom";
import { Gauge, MagnifyingGlass, Bell, Certificate, Gear, SignOut, SealCheck, Users, Diamond, Crown, ShieldCheck, ArrowsLeftRight, IdentificationCard, Image as ImageIcon, List, X } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { useAuth } from "@/lib/auth";
import { useBusiness } from "@/lib/settings";
import { mediaUrl } from "@/lib/api";

const MARBLE_BG =
  "https://static.prod-images.emergentagent.com/jobs/6572b450-f0e7-4d20-83da-0f44a5e44dfd/images/df3161b0cd73f56ca5ed2325b394244a0bc533006164f0b288a0bd38c33fcfef.jpeg";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `relative flex items-center gap-3 rounded-lg px-4 py-3 text-xs uppercase tracking-[0.15em] transition-colors duration-300 ${
    isActive ? "bg-white/5 text-gold" : "text-primary-foreground/60 hover:text-primary-foreground"
  }`;

const NAV_ITEMS = [
  { to: "/admin/dashboard", id: TEST_IDS.admin.navDashboard, Icon: Gauge, label: "admin.dashboard" },
  { to: "/admin/legalitas", id: TEST_IDS.admin.navLegality, Icon: Certificate, label: "adminNav.legality" },
  { to: "/admin/certificates", id: TEST_IDS.admin.navCertificates, Icon: SealCheck, label: "adminCert.navTitle" },
  { to: "/admin/customers", id: TEST_IDS.admin.navCustomers, Icon: Users, label: "adminNav.customers" },
  { to: "/admin/gemstones", id: TEST_IDS.admin.navGemstones, Icon: Diamond, label: "adminNav.gemstones" },
  { to: "/admin/jewelry", id: TEST_IDS.admin.navJewelry, Icon: Crown, label: "adminNav.jewelry" },
  { to: "/admin/warranties", id: TEST_IDS.admin.navWarranties, Icon: ShieldCheck, label: "adminNav.warranties" },
  { to: "/admin/ownership", id: TEST_IDS.admin.navOwnership, Icon: ArrowsLeftRight, label: "adminNav.ownership" },
  { to: "/admin/membership", id: TEST_IDS.admin.navMembership, Icon: IdentificationCard, label: "adminNav.membership" },
  { to: "/admin/visuals", id: TEST_IDS.admin.navVisuals, Icon: ImageIcon, label: "adminVisuals.navTitle" },
  { to: "/admin/settings", id: TEST_IDS.admin.navSettings, Icon: Gear, label: "adminNav.settings" },
] as const;

export default function AdminLayout() {
  const { t } = useLanguage();
  const { logout } = useAuth();
  const { visuals } = useBusiness();
  const [navOpen, setNavOpen] = useState(false);

  const useCustomBg = Boolean(visuals?.dashboard_bg_enabled && visuals?.dashboard_bg_url);
  const bgImage = useCustomBg ? mediaUrl(visuals!.dashboard_bg_url) : MARBLE_BG;
  const bgOpacity = useCustomBg
    ? Math.min(Math.max((visuals!.dashboard_bg_opacity ?? 10) / 100, 0.04), 0.24)
    : 0.1;
  const bgSize = useCustomBg && visuals!.dashboard_bg_fit === "center" ? "contain" : "cover";
  const bgBlur = useCustomBg ? Math.min(Math.max(visuals!.dashboard_bg_blur ?? 0, 0), 12) : 0;

  // Shared sidebar body (brand + nav + logout). `idSuffix` keeps mobile testids
  // unique from the always-in-DOM desktop sidebar. `onNavigate` closes the drawer.
  const SidebarBody = ({ idSuffix = "", onNavigate }: { idSuffix?: string; onNavigate?: () => void }) => (
    <>
      <Link to="/" onClick={onNavigate} className="mb-10 flex items-center gap-3">
        <img
          src="/azuris-logo.png"
          alt="Azuris Gemological"
          width={34}
          height={34}
          className="h-[34px] w-[34px] object-contain"
          data-testid={`admin-logo${idSuffix}`}
        />
        <span className="flex flex-col leading-none">
          <span className="font-serif text-xl font-semibold tracking-tight">AZURIS</span>
          <span className="mt-1.5 block text-[0.5rem] uppercase tracking-[0.4em] text-primary-foreground/50">
            {t("admin.title")}
          </span>
        </span>
      </Link>

      <nav className="flex flex-col gap-1.5 border-t border-primary-foreground/10 pt-8">
        {NAV_ITEMS.map(({ to, id, Icon, label }) => (
          <NavLink key={to} to={to} data-testid={`${id}${idSuffix}`} className={navLinkClass} onClick={onNavigate}>
            <Icon size={18} weight="regular" />
            {t(label)}
          </NavLink>
        ))}
      </nav>

      <button
        type="button"
        data-testid={`${TEST_IDS.admin.logout}${idSuffix}`}
        onClick={() => {
          onNavigate?.();
          logout();
        }}
        className="mt-auto flex items-center gap-2 pt-8 text-[0.7rem] uppercase tracking-[0.15em] text-primary-foreground/50 transition-colors hover:text-primary-foreground"
      >
        <SignOut size={16} weight="thin" />
        {t("auth.logout")}
      </button>
    </>
  );

  return (
    <div data-testid={TEST_IDS.admin.layout} className="flex min-h-screen bg-secondary text-foreground">
      {/* Deep Navy sidebar (desktop) */}
      <aside
        data-testid={TEST_IDS.admin.sidebar}
        className="hidden w-72 shrink-0 flex-col bg-primary p-7 text-primary-foreground md:flex"
      >
        <SidebarBody />
      </aside>

      {/* Mobile navigation drawer */}
      {navOpen && (
        <div className="fixed inset-0 z-50 md:hidden" data-testid="admin-mobile-nav">
          <div
            className="absolute inset-0 bg-black/50"
            aria-hidden="true"
            onClick={() => setNavOpen(false)}
          />
          <aside className="absolute left-0 top-0 flex h-full w-72 max-w-[82%] flex-col overflow-y-auto bg-primary p-7 text-primary-foreground shadow-2xl">
            <button
              type="button"
              data-testid="admin-mobile-nav-close"
              onClick={() => setNavOpen(false)}
              aria-label="Tutup menu"
              className="mb-4 self-end text-primary-foreground/70 hover:text-primary-foreground"
            >
              <X size={22} weight="thin" />
            </button>
            <SidebarBody idSuffix="-m" onNavigate={() => setNavOpen(false)} />
          </aside>
        </div>
      )}

      {/* Workspace */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* White topbar */}
        <header className="flex h-20 items-center justify-between gap-4 border-b border-border bg-background px-4 md:px-10">
          <div className="flex min-w-0 flex-1 items-center gap-3">
            <button
              type="button"
              data-testid="admin-mobile-nav-toggle"
              onClick={() => setNavOpen(true)}
              aria-label="Buka menu"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-border text-foreground md:hidden"
            >
              <List size={22} weight="regular" />
            </button>
            <div className="hidden max-w-md flex-1 items-center gap-3 rounded-lg border border-border bg-secondary px-4 py-2.5 text-muted-foreground md:flex">
              <MagnifyingGlass size={16} weight="regular" />
              <span className="text-sm">Search…</span>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-5">
            <Bell size={20} weight="regular" className="text-muted-foreground" />
            <span className="flex h-10 w-10 items-center justify-center rounded-full border border-gold/40 bg-secondary">
              <img src="/azuris-logo.png" alt="Azuris" width={24} height={24} className="h-6 w-6 object-contain" />
            </span>
          </div>
        </header>

        <main className="relative min-w-0 flex-1 bg-secondary">
          {/* Dashboard background — CMS-controlled; approved marble is the default */}
          <div
            aria-hidden="true"
            data-testid="admin-bg-overlay"
            className={`pointer-events-none absolute inset-0 bg-center bg-no-repeat ${useCustomBg ? "" : "mix-blend-multiply"}`}
            style={{
              backgroundImage: `url(${bgImage})`,
              backgroundSize: bgSize,
              opacity: bgOpacity,
              filter: useCustomBg
                ? bgBlur
                  ? `blur(${bgBlur}px)`
                  : undefined
                : "contrast(1.25) saturate(0.9)",
            }}
          />
          <div className="relative">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
