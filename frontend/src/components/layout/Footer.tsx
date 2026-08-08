import { Link } from "react-router-dom";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

const footerLinks = [
  { to: "/#verification", key: "nav.verification" },
  { to: "/#proses", key: "nav.process" },
  { to: "/legalitas", key: "nav.legality" },
  { to: "/about", key: "nav.about" },
  { to: "/contact", key: "nav.contact" },
];

export default function Footer() {
  const { t } = useLanguage();
  const year = new Date().getFullYear();

  return (
    <footer
      data-testid={TEST_IDS.footer.root}
      className="border-t border-border/60 bg-secondary/30"
    >
      <div className="mx-auto max-w-7xl px-6 py-16 md:px-10">
        <div className="grid gap-12 md:grid-cols-[1.5fr_1fr]">
          <div>
            <p className="font-serif text-3xl font-light tracking-tighter">
              AZURIS
            </p>
            <p className="mt-1 text-[0.6rem] uppercase tracking-[0.35em] text-muted-foreground">
              Gemological
            </p>
            <p className="mt-6 max-w-md text-sm leading-relaxed text-muted-foreground">
              {t("tagline")}
            </p>
            <p className="mt-4 text-xs uppercase tracking-[0.2em] text-primary/70">
              {t("footer.established")}
            </p>
          </div>

          <nav className="flex flex-col gap-3">
            {footerLinks.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className="text-sm text-muted-foreground transition-colors duration-500 hover:text-foreground"
              >
                {t(item.key)}
              </Link>
            ))}
          </nav>
        </div>

        <div className="mt-14 flex flex-col items-start justify-between gap-3 border-t border-border/60 pt-8 text-xs text-muted-foreground md:flex-row md:items-center">
          <span>
            © {year} {t("brand")}. {t("footer.rights")}
          </span>
          <span className="uppercase tracking-[0.2em]">{t("footer.tagline2")}</span>
        </div>
      </div>
    </footer>
  );
}
