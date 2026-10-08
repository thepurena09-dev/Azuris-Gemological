import PlaceholderPage from "@/components/common/PlaceholderPage";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

export default function AboutPage() {
  const { t } = useLanguage();
  return (
    <div
      className="border-y border-gold/20 bg-[#f7f3ea]"
      style={{
        backgroundImage:
          "radial-gradient(circle at 10% 16%, rgba(199,159,70,0.23), transparent 24%), radial-gradient(circle at 90% 82%, rgba(13,27,42,0.14), transparent 30%), linear-gradient(135deg, #faf8f2 0%, #eee5d4 50%, #f8f5ee 100%)",
      }}
    >
      <PlaceholderPage
        title={t("nav.about")}
        description="Azuris Gemological Research provides gemstone examination, identification, documentation, and certification services. Each issued gemstone certificate has a unique number that can be checked through the digital verification system."
        testId={TEST_IDS.page.about}
        breadcrumbs={[{ label: t("nav.about") }]}
      />
    </div>
  );
}
