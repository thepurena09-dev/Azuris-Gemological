import PlaceholderPage from "@/components/common/PlaceholderPage";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

export default function ContactPage() {
  const { t } = useLanguage();
  return (
    <PlaceholderPage
      title={t("nav.contact")}
      testId={TEST_IDS.page.contact}
      breadcrumbs={[{ label: t("nav.contact") }]}
    />
  );
}
