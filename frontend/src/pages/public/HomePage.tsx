import * as React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  ShieldCheck,
  ArrowRight,
  CaretRight,
  WhatsappLogo,
  ClipboardText,
  MagnifyingGlass,
  FileText,
  Certificate,
  QrCode,
  LockKey,
  Palette,
  Flask,
  Camera,
  Diamond,
} from "@phosphor-icons/react";
import type { Icon } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { useBusiness } from "@/lib/settings";
import { mediaUrl } from "@/lib/api";
import HeroCarousel from "@/components/home/HeroCarousel";

const MARBLE_BG =
  "https://static.prod-images.emergentagent.com/jobs/6572b450-f0e7-4d20-83da-0f44a5e44dfd/images/df3161b0cd73f56ca5ed2325b394244a0bc533006164f0b288a0bd38c33fcfef.jpeg";

const GEM = {
  diamond:
    "https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
  ruby: "https://images.unsplash.com/photo-1705575490492-4e91fd97bbb4?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
  sapphire:
    "https://static.prod-images.emergentagent.com/jobs/0d8170c5-08d6-45ed-9937-114710780b07/images/11e5956f874718e6db198dda556242a9e59a93fb2ea1cd0b3fe0d77cc5e02724.jpeg",
  emerald:
    "https://static.prod-images.emergentagent.com/jobs/6572b450-f0e7-4d20-83da-0f44a5e44dfd/images/8138fec9a0cfedc223c4896ebd58852071928246a1875cecdb3ce5aaebe929ad.jpeg",
};

function Eyebrow({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-4">
      <span className="h-px w-10 bg-gold" />
      <span className="text-[0.68rem] uppercase tracking-[0.4em] text-gold">{label}</span>
    </div>
  );
}

function StonePanel({ img, name, desc }: { img: string; name: string; desc: string }) {
  return (
    <div className="flex flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-[0_20px_50px_-40px_rgba(13,27,42,0.35)]">
      <div className="aspect-[16/10] overflow-hidden bg-secondary">
        <img src={img} alt={name} className="h-full w-full object-cover" />
      </div>
      <div className="p-6">
        <h3 className="font-serif text-2xl font-normal tracking-tight text-foreground">{name}</h3>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{desc}</p>
      </div>
    </div>
  );
}

export default function HomePage() {
  const { t, locale } = useLanguage();
  const { hash, search } = useLocation();
  const navigate = useNavigate();
  const { whatsappHref, visuals } = useBusiness();

  const showProcessImg = visuals?.process_image_show !== false && !!visuals?.process_image_url;
  const processImg = mediaUrl(visuals?.process_image_url);
  const processAlt =
    (locale === "en" ? visuals?.process_image_alt_en : visuals?.process_image_alt_id) ||
    t("process.title");

  // Homepage hero background (CMS) — marble default when custom disabled.
  const useHomeBg = Boolean(visuals?.home_bg_enabled && visuals?.home_bg_url);
  const homeBgImage = useHomeBg ? mediaUrl(visuals!.home_bg_url) : MARBLE_BG;
  const homeBgOpacity = useHomeBg
    ? Math.min(Math.max((visuals!.home_bg_opacity ?? 20) / 100, 0), 1)
    : 0.2;
  const homeBgSize = useHomeBg && visuals!.home_bg_fit === "center" ? "contain" : "cover";
  const homeBgBlur = useHomeBg ? Math.min(Math.max(visuals!.home_bg_blur ?? 0, 0), 12) : 0;

  // Homepage hero gemstone photos (CMS) — fall back to bundled defaults.
  const gems = {
    diamond: mediaUrl(visuals?.home_gem_diamond_url) || GEM.diamond,
    ruby: mediaUrl(visuals?.home_gem_ruby_url) || GEM.ruby,
    sapphire: mediaUrl(visuals?.home_gem_sapphire_url) || GEM.sapphire,
    emerald: mediaUrl(visuals?.home_gem_emerald_url) || GEM.emerald,
  };

  // Homepage promotional slide (CMS-editable; neutral i18n defaults). Shown first.
  const promo = {
    show: visuals?.promo_show !== false,
    eyebrow: (locale === "en" ? visuals?.promo_eyebrow_en : visuals?.promo_eyebrow_id) || t("home.promo.eyebrow"),
    heading: (locale === "en" ? visuals?.promo_heading_en : visuals?.promo_heading_id) || t("home.promo.heading"),
    desc: (locale === "en" ? visuals?.promo_desc_en : visuals?.promo_desc_id) || t("home.promo.desc"),
    cta: (locale === "en" ? visuals?.promo_cta_en : visuals?.promo_cta_id) || t("home.promo.cta"),
    image: mediaUrl(visuals?.promo_image_url),
  };

  // QR flow: /?qr=<opaque_token> -> forward to the dedicated /verify page
  React.useEffect(() => {
    const token = new URLSearchParams(search).get("qr");
    if (token) navigate(`/verify?t=${encodeURIComponent(token)}`, { replace: true });
  }, [search, navigate]);

  React.useEffect(() => {
    if (!hash) return;
    const el = document.getElementById(hash.slice(1));
    if (el) {
      const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      el.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
    }
  }, [hash]);

  const pillars = [
    { img: gems.diamond, key: "diamond" },
    { img: gems.ruby, key: "ruby" },
    { img: gems.sapphire, key: "sapphire" },
    { img: gems.emerald, key: "emerald" },
  ];

  const processSteps: { icon: Icon; k: string }[] = [
    { icon: ClipboardText, k: "register" },
    { icon: MagnifyingGlass, k: "examine" },
    { icon: FileText, k: "document" },
    { icon: Certificate, k: "issue" },
    { icon: QrCode, k: "verify" },
  ];

  const whyItems: { icon: Icon; k: string }[] = [
    { icon: MagnifyingGlass, k: "examination" },
    { icon: FileText, k: "documentation" },
    { icon: ShieldCheck, k: "verification" },
    { icon: LockKey, k: "integrity" },
  ];

  const standardsItems: { icon: Icon; k: string }[] = [
    { icon: Diamond, k: "species" },
    { icon: Palette, k: "color" },
    { icon: Flask, k: "treatment" },
    { icon: Camera, k: "photo" },
  ];

  // Slide 0 — Promotional (premium, navy-dominant; first slide on load)
  const slidePromo = (
    <div className="flex min-h-[600px] items-center bg-primary px-6 py-16 text-primary-foreground md:px-10">
      <div className="mx-auto grid w-full max-w-7xl items-center gap-14 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="max-w-xl">
          <Eyebrow label={promo.eyebrow} />
          <h1 className="mt-6 font-serif text-4xl font-normal leading-[1.04] tracking-tight md:text-6xl">
            {promo.heading}
          </h1>
          <p className="mt-6 max-w-md text-base leading-relaxed text-primary-foreground/80">
            {promo.desc}
          </p>
          <div className="mt-9">
            <a
              href={whatsappHref()}
              target="_blank"
              rel="noopener noreferrer"
              data-testid="home-promo-cta"
              className="group inline-flex items-center gap-3 rounded-lg border border-gold bg-gold px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary transition-colors duration-300 hover:bg-transparent hover:text-gold"
            >
              <WhatsappLogo size={18} weight="fill" />
              {promo.cta}
            </a>
          </div>
        </div>

        <div className="relative flex items-center justify-center">
          <img
            src={promo.image || "/sample-card.png"}
            alt={promo.heading}
            data-testid="home-promo-image"
            className="w-full max-w-xl rounded-2xl drop-shadow-[0_30px_70px_rgba(0,0,0,0.5)]"
          />
        </div>
      </div>
    </div>
  );

  // Slide 1 — Four Pillars
  const slidePillars = (
    <div className="flex min-h-[600px] items-center px-6 py-16 md:px-10">
      <div className="mx-auto grid max-w-7xl items-center gap-14 lg:grid-cols-[1fr_1fr]">
        <div className="max-w-xl">
          <img
            src="/azuris-logo.png"
            alt="Azuris Gemological"
            width={64}
            height={64}
            className="mb-6 h-16 w-16 object-contain"
            data-testid="hero-logo"
          />
          <Eyebrow label={t("home.slides.pillars.eyebrow")} />
          <h1 className="mt-6 font-serif text-5xl font-normal leading-[1.02] tracking-tight text-foreground md:text-7xl">
            {t("home.slides.pillars.title")}
          </h1>
          <p className="mt-6 max-w-md text-base leading-relaxed text-muted-foreground">
            {t("home.slides.pillars.subtitle")}
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-4">
            <Link
              to="/verify"
              className="group inline-flex items-center gap-3 rounded-lg bg-primary px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground shadow-sm transition-shadow duration-300 hover:shadow-xl"
            >
              <ShieldCheck size={16} weight="regular" className="text-gold" />
              {t("home.slides.pillars.ctaPrimary")}
            </Link>
            <Link
              to="/#proses"
              className="inline-flex items-center gap-3 rounded-lg border border-gold px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-foreground transition-shadow duration-300 hover:shadow-lg"
            >
              {t("home.slides.pillars.ctaSecondary")}
              <ArrowRight size={16} weight="bold" />
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-5">
          {pillars.map((p) => (
            <div key={p.key} className="overflow-hidden rounded-2xl border border-border bg-card">
              <div className="aspect-square overflow-hidden bg-secondary">
                <img
                  src={p.img}
                  alt={t(`home.slides.pillars.items.${p.key}`)}
                  className="h-full w-full object-cover"
                />
              </div>
              <div className="flex items-center justify-between px-4 py-3">
                <span className="text-[0.7rem] uppercase tracking-[0.24em] text-foreground">
                  {t(`home.slides.pillars.items.${p.key}`)}
                </span>
                <Diamond size={13} weight="fill" className="text-gold" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Slide 2 — Diamond & Ruby
  const slideDiamondRuby = (
    <div className="flex min-h-[600px] items-center px-6 py-16 md:px-10">
      <div className="mx-auto w-full max-w-7xl">
        <Eyebrow label={t("home.slides.diamondRuby.eyebrow")} />
        <h2 className="mt-5 font-serif text-4xl font-normal tracking-tight text-foreground md:text-6xl">
          {t("home.slides.diamondRuby.title")}
        </h2>
        <div className="mt-10 grid gap-8 md:grid-cols-2">
          <StonePanel
            img={gems.diamond}
            name={t("home.slides.diamondRuby.diamond.name")}
            desc={t("home.slides.diamondRuby.diamond.desc")}
          />
          <StonePanel
            img={gems.ruby}
            name={t("home.slides.diamondRuby.ruby.name")}
            desc={t("home.slides.diamondRuby.ruby.desc")}
          />
        </div>
      </div>
    </div>
  );

  // Slide 3 — Sapphire & Emerald
  const slideSapphireEmerald = (
    <div className="flex min-h-[600px] items-center px-6 py-16 md:px-10">
      <div className="mx-auto w-full max-w-7xl">
        <Eyebrow label={t("home.slides.sapphireEmerald.eyebrow")} />
        <h2 className="mt-5 font-serif text-4xl font-normal tracking-tight text-foreground md:text-6xl">
          {t("home.slides.sapphireEmerald.title")}
        </h2>
        <div className="mt-10 grid gap-8 md:grid-cols-2">
          <StonePanel
            img={gems.sapphire}
            name={t("home.slides.sapphireEmerald.sapphire.name")}
            desc={t("home.slides.sapphireEmerald.sapphire.desc")}
          />
          <StonePanel
            img={gems.emerald}
            name={t("home.slides.sapphireEmerald.emerald.name")}
            desc={t("home.slides.sapphireEmerald.emerald.desc")}
          />
        </div>
      </div>
    </div>
  );

  return (
    <div data-testid={TEST_IDS.page.home} className="bg-background">
      {/* Hero carousel — exactly 3 slides */}
      <section className="relative overflow-hidden border-b border-border bg-secondary">
        <div
          data-testid="home-bg-overlay"
          className="pointer-events-none absolute inset-0 bg-center bg-no-repeat mix-blend-multiply"
          style={{
            backgroundImage: `url(${homeBgImage})`,
            backgroundSize: homeBgSize,
            opacity: homeBgOpacity,
            filter: homeBgBlur ? `blur(${homeBgBlur}px)` : undefined,
          }}
        />
        <div className="relative">
          <HeroCarousel
            ariaLabel={t("home.slides.pillars.title")}
            slides={[
              ...(promo.show ? [slidePromo] : []),
              slidePillars,
              slideDiamondRuby,
              slideSapphireEmerald,
            ]}
          />
        </div>
      </section>

      {/* Certification process */}
      <section id="proses" className="scroll-mt-28 mx-auto max-w-7xl px-6 py-24 md:px-10">
        <Eyebrow label={t("process.eyebrow")} />
        <div className="mt-6 flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="max-w-3xl font-serif text-4xl font-normal tracking-tight text-foreground md:text-6xl">
            {t("process.title")}
          </h2>
          <a
            href={whatsappHref()}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="home-whatsapp-process"
            className="inline-flex shrink-0 items-center gap-3 rounded-lg bg-primary px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground transition-shadow duration-300 hover:shadow-xl"
          >
            <WhatsappLogo size={18} weight="fill" className="text-gold" />
            {t("contact.moreInfo")}
          </a>
        </div>
        <p className="mt-5 max-w-2xl text-base leading-relaxed text-muted-foreground">
          {t("process.subtitle")}
        </p>
        {showProcessImg && (
          <div
            data-testid="process-image"
            className="mt-10 overflow-hidden rounded-2xl border border-border bg-secondary shadow-[0_24px_60px_-46px_rgba(13,27,42,0.5)]"
          >
            <img
              src={processImg}
              alt={processAlt}
              className="h-full max-h-[420px] w-full object-cover"
            />
          </div>
        )}
        <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-5">
          {processSteps.map(({ icon: Ic, k }, i) => (
            <div
              key={k}
              className="relative rounded-2xl border border-border bg-card p-6 shadow-[0_20px_50px_-40px_rgba(13,27,42,0.35)]"
            >
              <span className="absolute right-5 top-5 font-serif text-2xl text-gold/30">
                {String(i + 1).padStart(2, "0")}
              </span>
              <span className="flex h-12 w-12 items-center justify-center rounded-full border border-gold/40 bg-secondary">
                <Ic size={22} weight="thin" className="text-gold" />
              </span>
              <h3 className="mt-6 text-xs uppercase tracking-[0.16em] text-foreground">
                {t(`process.steps.${k}.title`)}
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                {t(`process.steps.${k}.desc`)}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Why Azuris */}
      <section className="border-y border-border bg-secondary/40">
        <div className="mx-auto max-w-7xl px-6 py-24 md:px-10">
          <Eyebrow label={t("why.eyebrow")} />
          <h2 className="mt-6 max-w-3xl font-serif text-4xl font-normal tracking-tight text-foreground md:text-6xl">
            {t("why.title")}
          </h2>
          <p className="mt-5 max-w-2xl text-base leading-relaxed text-muted-foreground">
            {t("why.subtitle")}
          </p>
          <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {whyItems.map(({ icon: Ic, k }) => (
              <div key={k} className="rounded-2xl border border-border bg-card p-8">
                <span className="flex h-14 w-14 items-center justify-center rounded-full border border-gold/40 bg-secondary">
                  <Ic size={24} weight="thin" className="text-gold" />
                </span>
                <h3 className="mt-6 text-xs uppercase tracking-[0.18em] text-foreground">
                  {t(`why.items.${k}.title`)}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                  {t(`why.items.${k}.desc`)}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Examination standards */}
      <section className="mx-auto max-w-7xl px-6 py-24 md:px-10">
        <Eyebrow label={t("standards.eyebrow")} />
        <h2 className="mt-6 max-w-3xl font-serif text-4xl font-normal tracking-tight text-foreground md:text-6xl">
          {t("standards.title")}
        </h2>
        <p className="mt-5 max-w-2xl text-base leading-relaxed text-muted-foreground">
          {t("standards.subtitle")}
        </p>
        <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {standardsItems.map(({ icon: Ic, k }) => (
            <div key={k} className="rounded-2xl border border-border bg-card p-8">
              <span className="flex h-14 w-14 items-center justify-center rounded-full border border-gold/40 bg-secondary">
                <Ic size={24} weight="thin" className="text-gold" />
              </span>
              <h3 className="mt-6 text-xs uppercase tracking-[0.18em] text-foreground">
                {t(`standards.items.${k}.title`)}
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                {t(`standards.items.${k}.desc`)}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Legality & credibility teaser */}
      <section className="border-t border-border bg-primary text-primary-foreground">
        <div className="mx-auto flex max-w-7xl flex-col items-start gap-8 px-6 py-20 md:flex-row md:items-center md:justify-between md:px-10">
          <div className="max-w-2xl">
            <span className="text-[0.68rem] uppercase tracking-[0.4em] text-gold">
              {t("legalityTeaser.eyebrow")}
            </span>
            <h2 className="mt-4 font-serif text-3xl font-normal tracking-tight md:text-5xl">
              {t("legalityTeaser.title")}
            </h2>
            <p className="mt-5 text-base leading-relaxed text-primary-foreground/70">
              {t("legalityTeaser.body")}
            </p>
          </div>
          <Link
            to="/legalitas"
            className="group inline-flex shrink-0 items-center gap-3 rounded-lg border border-gold px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-gold transition-colors duration-300 hover:bg-gold hover:text-primary"
          >
            {t("legalityTeaser.cta")}
            <CaretRight size={14} weight="bold" />
          </Link>
        </div>
      </section>

      {/* Contact / WhatsApp */}
      <section id="kontak" className="scroll-mt-28 mx-auto max-w-5xl px-6 py-24 text-center md:px-10">
        <Eyebrow label={t("contact.eyebrow")} />
        <h2 className="mt-6 font-serif text-4xl font-normal tracking-tight text-foreground md:text-6xl">
          {t("contact.title")}
        </h2>
        <p className="mx-auto mt-5 max-w-2xl text-base leading-relaxed text-muted-foreground">
          {t("contact.subtitle")}
        </p>
        <div className="mt-8 flex justify-center">
          <a
            href={whatsappHref()}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="home-whatsapp-contact"
            className="inline-flex items-center gap-3 rounded-lg bg-primary px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground transition-shadow duration-300 hover:shadow-xl"
          >
            <WhatsappLogo size={18} weight="fill" className="text-gold" />
            {t("contact.moreInfo")}
          </a>
        </div>
      </section>
    </div>
  );
}
