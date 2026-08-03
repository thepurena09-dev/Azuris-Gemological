import { GlobeSimple } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import type { Locale } from "@/config";
import { TEST_IDS } from "@/constants/testIds";

const options: { value: Locale; label: string; testId: string }[] = [
  { value: "id", label: "ID", testId: TEST_IDS.header.langId },
  { value: "en", label: "EN", testId: TEST_IDS.header.langEn },
];

export default function LanguageSwitcher() {
  const { locale, setLocale } = useLanguage();

  return (
    <div
      data-testid={TEST_IDS.header.langSwitcher}
      className="flex items-center gap-2"
    >
      <GlobeSimple size={18} weight="regular" className="text-muted-foreground" />
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          data-testid={opt.testId}
          onClick={() => setLocale(opt.value)}
          aria-pressed={locale === opt.value}
          className={`rounded-md px-2.5 py-1 text-[0.7rem] font-medium uppercase tracking-[0.15em] transition-colors duration-300 ${
            locale === opt.value
              ? "border border-gold text-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
