import * as React from "react";
import { useSearchParams } from "react-router-dom";
import { SealCheck, XCircle, CircleNotch } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiJson } from "@/lib/api";
import { MembershipCardVisual } from "@/components/membership/MembershipCardVisual";

interface Result {
  valid: boolean;
  status?: string;
  member_id?: string;
  member_name?: string;
  member_since?: string | null;
}

export default function MembershipVerifyPage() {
  const { t } = useLanguage();
  const [params] = useSearchParams();
  const token = params.get("t") || "";
  const [res, setRes] = React.useState<Result | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    if (!token) { setRes({ valid: false }); setLoading(false); return; }
    apiJson<Result>(`/api/membership/verify?t=${encodeURIComponent(token)}`)
      .then((d) => setRes(d))
      .catch(() => setRes({ valid: false }))
      .finally(() => setLoading(false));
  }, [token]);

  return (
    <section data-testid={TEST_IDS.page.membershipVerify} className="mx-auto max-w-2xl px-6 py-16 md:py-24">
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">AZURIS GEMOLOGICAL</p>
      <h1 className="mt-3 font-serif text-4xl font-normal tracking-tight sm:text-5xl">{t("membershipVerify.title")}</h1>

      {loading ? (
        <div className="mt-10 flex items-center gap-2 text-muted-foreground"><CircleNotch size={18} className="animate-spin" /> {t("membershipVerify.checking")}</div>
      ) : res && (res.member_id) ? (
        <div className="mt-10 space-y-6">
          <div className={`flex items-center gap-2 rounded-lg px-4 py-3 text-sm ${res.valid ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>
            {res.valid ? <SealCheck size={20} /> : <XCircle size={20} />}
            <span data-testid="membership-verify-status">{res.valid ? t("membershipVerify.valid") : t("membershipVerify.inactive")}</span>
          </div>
          <MembershipCardVisual cardNumber={res.member_id!} memberName={res.member_name || "—"} memberSince={res.member_since} status={res.status} side="front" />
          <dl className="grid grid-cols-2 gap-4 rounded-2xl border border-border bg-card p-6 text-sm">
            <div><dt className="text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground">{t("membershipVerify.memberId")}</dt><dd className="mt-1 font-mono">{res.member_id}</dd></div>
            <div><dt className="text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground">{t("membershipVerify.memberName")}</dt><dd className="mt-1">{res.member_name}</dd></div>
            <div><dt className="text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground">{t("membershipVerify.memberSince")}</dt><dd className="mt-1">{res.member_since || "—"}</dd></div>
            <div><dt className="text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground">{t("membershipVerify.status")}</dt><dd className="mt-1 capitalize">{res.status}</dd></div>
          </dl>
        </div>
      ) : (
        <div data-testid="membership-verify-invalid" className="mt-10 flex items-center gap-2 rounded-lg bg-secondary px-4 py-4 text-sm text-muted-foreground">
          <XCircle size={20} className="text-red-500" /> {t("membershipVerify.invalid")}
        </div>
      )}
    </section>
  );
}
