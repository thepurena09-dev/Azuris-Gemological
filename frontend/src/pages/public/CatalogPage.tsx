import PlaceholderPage from "@/components/common/PlaceholderPage";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

export default function CatalogPage() {
  const { t } = useLanguage();
  return (
    <PlaceholderPage
      title={t("nav.catalog")}
      testId={TEST_IDS.page.catalog}
      breadcrumbs={[{ label: t("nav.catalog") }]}
    />
  );
}
