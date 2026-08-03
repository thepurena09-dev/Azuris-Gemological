import PlaceholderPage from "@/components/common/PlaceholderPage";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

export default function VerificationPage() {
  const { t } = useLanguage();
  return (
    <PlaceholderPage
      title={t("nav.verification")}
      testId={TEST_IDS.page.verification}
      breadcrumbs={[{ label: t("nav.verification") }]}
    />
  );
}
