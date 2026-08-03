import PlaceholderPage from "@/components/common/PlaceholderPage";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

export default function JewelryPage() {
  const { t } = useLanguage();
  return (
    <PlaceholderPage
      title={t("nav.jewelry")}
      testId={TEST_IDS.page.jewelry}
      breadcrumbs={[
        { label: t("nav.catalog"), to: "/catalog" },
        { label: t("nav.jewelry") },
      ]}
    />
  );
}
