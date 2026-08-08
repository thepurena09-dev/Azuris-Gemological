/**
 * English locale — SECONDARY.
 */
const en = {
  brand: "Azuris Gemological",
  tagline: "Gemstone certification, identity documentation, and verification.",
  comingSoon: "This page will be implemented in a future stage.",
  sprintNotice: "A Trusted Gemological Institution",
  breadcrumbHome: "Home",
  nav: {
    home: "Home",
    verification: "Verify Certificate",
    process: "Certification Process",
    legality: "Legality",
    about: "About Azuris",
    contact: "Contact Us",
    login: "Sign In",
    catalog: "Catalog",
    gemstones: "Gemstones",
    jewelry: "Jewelry",
  },
  footer: {
    rights: "All rights reserved.",
    established: "A Trusted Gemological Institution",
    tagline2: "Certification · Documentation · Verification",
  },
  home: {
    established: "A Trusted Gemological Institution",
    slides: {
      pillars: {
        eyebrow: "Four Pillars",
        title: "The Four Pillars of Gemstones",
        subtitle:
          "Understanding the key characters of gemstones that form an essential part of gemology.",
        ctaPrimary: "Verify Certificate",
        ctaSecondary: "Learn the Certification Process",
        items: {
          diamond: "Diamond",
          ruby: "Ruby",
          sapphire: "Sapphire",
          emerald: "Emerald",
        },
      },
      diamondRuby: {
        eyebrow: "Gemstone Identity",
        title: "Diamond & Ruby",
        diamond: {
          name: "Diamond",
          desc: "The hardest stone on earth, renowned for its brilliance and clarity.",
        },
        ruby: {
          name: "Ruby",
          desc: "A vivid red gemstone symbolizing strength and passion.",
        },
      },
      sapphireEmerald: {
        eyebrow: "Gemstone Identity",
        title: "Sapphire & Emerald",
        sapphire: {
          name: "Sapphire",
          desc: "A precious stone commonly known for its elegant deep blue color.",
        },
        emerald: {
          name: "Emerald",
          desc: "A gemstone with a distinctive, iconic green color.",
        },
      },
    },
  },
  verify: {
    eyebrow: "Authenticity Verification",
    title: "Verify Certificate",
    description:
      "Enter the certificate number and security code printed on your Azuris document to check its authenticity.",
    certLabel: "Certificate Number",
    certPlaceholder: "AZR-GEM-YYYY-000001",
    codeLabel: "Security Code",
    codePlaceholder: "Code on the certificate",
    submit: "Verify",
    submitting: "Checking…",
    formatError: "Invalid certificate number format. Example: AZR-GEM-2026-000001",
    codeRequired: "Security code is required.",
    unavailableTitle: "Verification Service Is Being Prepared",
    unavailable:
      "The verification service is being prepared. No certificate data is shown before the verification system is active.",
    emptyHint:
      "Every Azuris certificate has a unique number and can be verified digitally.",
  },
  process: {
    eyebrow: "Workflow",
    title: "Certification Process",
    subtitle:
      "Every stone goes through a documented and verifiable examination workflow.",
    steps: {
      register: {
        title: "Stone Registration",
        desc: "Initial data recording and intake of the stone for examination.",
      },
      examine: {
        title: "Physical & Gemological Examination",
        desc: "Physical and gemological analysis to identify the stone's characteristics.",
      },
      document: {
        title: "Result Documentation",
        desc: "Detailed and structured recording of examination results.",
      },
      issue: {
        title: "Certificate Issuance",
        desc: "Issuance of a certificate with a unique, verifiable number.",
      },
      verify: {
        title: "Digital Verification",
        desc: "Checking certificate authenticity through the digital verification system.",
      },
    },
  },
  why: {
    eyebrow: "Advantages",
    title: "Why Choose Azuris",
    subtitle:
      "Our focus is professional gemstone examination, documentation, and verification.",
    items: {
      examination: {
        title: "Gemological Examination",
        desc: "Thorough and objective gemological examination.",
      },
      documentation: {
        title: "Identity Documentation",
        desc: "Complete and consistent gemstone identity documentation.",
      },
      verification: {
        title: "Authenticity Verification",
        desc: "Verify certificate authenticity anytime, digitally.",
      },
      integrity: {
        title: "Document Integrity",
        desc: "Document integrity protection and data transparency.",
      },
    },
  },
  standards: {
    eyebrow: "Standards",
    title: "Examination Standards",
    subtitle: "Every stone is examined against the key gemological aspects.",
    items: {
      species: {
        title: "Species & Variety Identification",
        desc: "Determining the stone's type and variety through gemological analysis.",
      },
      color: {
        title: "Color & Clarity Characteristics",
        desc: "Assessment of color, transparency, and clarity characteristics.",
      },
      treatment: {
        title: "Treatment Indication",
        desc: "Identification of any treatment indications on the stone.",
      },
      photo: {
        title: "Photographic Documentation",
        desc: "Visual documentation as part of the examination report.",
      },
    },
  },
  legalityTeaser: {
    eyebrow: "Credibility",
    title: "Legality and Credibility",
    body: "Azuris Gemological is committed to professional and verifiable gemstone examination, identification, documentation, and certification services.",
    cta: "View Legality",
  },
  contact: {
    eyebrow: "Contact Us",
    title: "Contact Azuris",
    subtitle:
      "Reach the Azuris team for questions about gemstone examination, certification, and verification.",
    whatsapp: "Contact via WhatsApp",
  },
  legality: {
    title: "Azuris Gemological Legality",
    subtitle:
      "A commitment to professional and verifiable gemstone examination, identification, and certificate issuance.",
    ctaVerify: "Verify a Gemstone Certificate",
    viewerTitle: "Legality Document",
    emptyTitle: "Document Not Yet Published",
    empty:
      "The official legality document has not been published yet. Information will appear here once available and validated by Azuris Gemological.",
    copyTitle: "Our Commitment",
    copy: "This certificate represents Azuris Gemological's commitment to providing professional gemstone examination, identification, documentation, and certification services. Every gemstone certificate issued by Azuris has a unique number and can be verified through the digital verification system.",
    disclaimerTitle: "Disclaimer",
    disclaimer:
      "A gemological certificate is a report of gemstone examination and identification. It does not automatically guarantee price, investment value, ownership, or the legal origin of a gemstone.",
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
