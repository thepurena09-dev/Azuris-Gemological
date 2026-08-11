import { WhatsappLogo } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { useBusiness } from "@/lib/settings";

export default function ContactPage() {
  const { t } = useLanguage();
  const { whatsappHref, whatsappNumber } = useBusiness();

  return (
    <div data-testid={TEST_IDS.page.contact} className="bg-background">
      <section className="border-b border-border bg-secondary/40">
        <div className="mx-auto max-w-4xl px-6 py-20 text-center md:px-10">
          <div className="mx-auto mb-6 flex w-fit items-center gap-4">
            <span className="h-px w-10 bg-gold" />
            <span className="text-[0.68rem] uppercase tracking-[0.4em] text-gold">
              {t("contact.eyebrow")}
            </span>
            <span className="h-px w-10 bg-gold" />
          </div>
          <h1 className="font-serif text-4xl font-normal leading-tight tracking-tight text-foreground md:text-6xl">
            {t("contact.title")}
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-muted-foreground">
            {t("contact.subtitle")}
          </p>
        </div>
      </section>

      <div className="mx-auto max-w-3xl px-6 py-16 text-center md:px-10">
        <div className="rounded-2xl border border-border bg-card p-10 shadow-[0_30px_70px_-45px_rgba(13,27,42,0.4)]">
          <p className="text-sm text-muted-foreground">
            {t("contact.subtitle")}
          </p>
          <a
            href={whatsappHref()}
            target="_blank"
            rel="noopener noreferrer"
            data-testid="contact-whatsapp-btn"
            className="group mt-8 inline-flex items-center gap-3 rounded-lg border border-gold bg-primary px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground transition-colors duration-300 hover:bg-gold hover:text-primary"
          >
            <WhatsappLogo size={18} weight="fill" className="text-gold group-hover:text-primary" />
            {t("contact.whatsapp")}
          </a>
          {whatsappNumber && (
            <p data-testid="contact-whatsapp-number" className="mt-4 font-mono text-sm text-muted-foreground">
              +{whatsappNumber}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
