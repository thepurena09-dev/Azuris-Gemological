/**
 * Centralized data-testid constants for stable UI testing.
 */
export const TEST_IDS = {
  header: {
    root: "public-header",
    brand: "header-brand-link",
    navHome: "nav-home",
    navAbout: "nav-about",
    navVerification: "nav-verification",
    navCatalog: "nav-catalog",
    navGemstones: "nav-gemstones",
    navJewelry: "nav-jewelry",
    navContact: "nav-contact",
    navLogin: "nav-login",
    langSwitcher: "language-switcher",
    langId: "language-option-id",
    langEn: "language-option-en",
    mobileToggle: "header-mobile-toggle",
  },
  footer: {
    root: "public-footer",
  },
  page: {
    home: "page-home",
    about: "page-about",
    verification: "page-verification",
    catalog: "page-catalog",
    gemstones: "page-gemstones",
    jewelry: "page-jewelry",
    contact: "page-contact",
    login: "page-login",
    adminDashboard: "page-admin-dashboard",
    notFound: "page-not-found",
  },
  common: {
    breadcrumb: "breadcrumb",
    comingSoon: "coming-soon-message",
    ctaHome: "cta-home",
    ctaVerify: "cta-verify",
  },
  admin: {
    layout: "admin-layout",
    sidebar: "admin-sidebar",
    navDashboard: "admin-nav-dashboard",
  },
} as const;
