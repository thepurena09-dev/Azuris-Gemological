import PlaceholderPage from "@/components/common/PlaceholderPage";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

export default function GemstonesPage() {
  const { t } = useLanguage();
  return (
    <PlaceholderPage
      title={t("nav.gemstones")}
      testId={TEST_IDS.page.gemstones}
      breadcrumbs={[
        { label: t("nav.catalog"), to: "/catalog" },
        { label: t("nav.gemstones") },
      ]}
    />
  );
}
