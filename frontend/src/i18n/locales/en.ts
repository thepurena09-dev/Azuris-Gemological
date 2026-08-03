/**
 * English locale — SECONDARY.
 * Sprint 1: placeholder/shell values only.
 */
const en = {
  brand: "Azuris Gemological",
  tagline: "World-Class Gemstone Certification & Verification",
  comingSoon: "This page will be implemented in a future sprint.",
  sprintNotice: "Application shell — Sprint 3",
  breadcrumbHome: "Home",
  nav: {
    home: "Home",
    about: "About",
    verification: "Verification",
    catalog: "Catalog",
    gemstones: "Gemstones",
    jewelry: "Jewelry",
    contact: "Contact",
    login: "Sign In",
  },
  footer: {
    rights: "All rights reserved.",
    established: "A Trusted Gemological Institution",
  },
  home: {
    description:
      "International standards for results you can trust, supported by modern technology and professional gemologists.",
    stats: {
      accurate: { value: "100%", label: "Accurate & Trusted" },
      global: { value: "Global", label: "International Standard" },
      professional: { value: "Professional", label: "Certified Gemologists" },
      recognized: { value: "World-Recognized", label: "Global Reputation" },
    },
    features: {
      trusted: { title: "Trusted", desc: "International standards for dependable results." },
      accurate: { title: "Accurate", desc: "Modern technology and certified experts." },
      professional: { title: "Professional", desc: "Transparent, professional gemological services." },
      global: { title: "Global", desc: "Globally recognized, the preferred choice." },
    },
  },
  admin: {
    title: "Admin Panel",
    dashboard: "Dashboard",
  },
  language: {
    label: "Language",
    id: "Indonesian",
    en: "English",
  },
} as const;

export default en;
