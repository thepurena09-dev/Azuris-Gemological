import PlaceholderPage from "@/components/common/PlaceholderPage";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

export default function AboutPage() {
  const { t } = useLanguage();
  return (
    <PlaceholderPage
      title={t("nav.about")}
      testId={TEST_IDS.page.about}
      breadcrumbs={[{ label: t("nav.about") }]}
    />
  );
}
