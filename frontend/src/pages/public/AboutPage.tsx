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
        testId={TEST_IDS.page.about}
        breadcrumbs={[{ label: t("nav.about") }]}
      />
    </div>
  );
}
