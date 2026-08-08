import * as React from "react";
import { useLanguage } from "@/i18n/LanguageContext";

interface Props {
  cardNumber: string;
  memberName: string;
  memberSince?: string | null;
  status?: string;
  qrSrc?: string | null;
  side?: "front" | "back";
}

/** Premium Azuris membership card (CR80 aspect 85.6×54). Navy-dominant, gold hairline. */
export const MembershipCardVisual: React.FC<Props> = ({ cardNumber, memberName, memberSince, status, qrSrc, side = "front" }) => {
  const { t } = useLanguage();
  const active = (status || "active") === "active";

  if (side === "back") {
    return (
      <div
        data-testid="membership-card-back"
        className="relative overflow-hidden rounded-2xl border border-[#C7A247]/40 p-6 text-[#FAF9F6] shadow-xl"
        style={{ aspectRatio: "85.6 / 54", background: "#0D1B2A" }}
      >
        <div className="absolute inset-0 opacity-[0.06]" style={{ backgroundImage: "url(/azuris-logo.png)", backgroundSize: "180px", backgroundRepeat: "no-repeat", backgroundPosition: "center" }} />
        <div className="relative flex h-full flex-col justify-between">
          <div className="flex items-center gap-2">
            <img src="/azuris-logo.png" alt="Azuris" className="h-6 w-6 object-contain" />
            <span className="font-serif text-lg tracking-wide">AZURIS</span>
          </div>
          <div className="flex items-end justify-between gap-4">
            <div className="max-w-[60%]">
              <p className="text-[0.7rem] leading-snug text-[#FAF9F6]/80">{t("adminMembership.statement")}</p>
              <p className="mt-2 text-[0.6rem] uppercase tracking-[0.15em] text-[#C7A247]">{t("adminMembership.scan")}</p>
            </div>
            {qrSrc ? (
              <div className="rounded-lg bg-white p-1.5">
                <img data-testid="membership-card-qr" src={qrSrc} alt="QR" className="h-20 w-20" />
              </div>
            ) : null}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      data-testid="membership-card-front"
      className="relative overflow-hidden rounded-2xl border border-[#C7A247]/50 p-6 text-[#FAF9F6] shadow-xl"
      style={{ aspectRatio: "85.6 / 54", background: "#0D1B2A" }}
    >
      <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full" style={{ background: "radial-gradient(circle, rgba(199,162,71,0.18), transparent 70%)" }} />
      <div className="absolute inset-0 opacity-[0.05]" style={{ backgroundImage: "url(/azuris-logo.png)", backgroundSize: "260px", backgroundRepeat: "no-repeat", backgroundPosition: "right -40px bottom -40px" }} />
      <div className="relative flex h-full flex-col justify-between">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2.5">
            <img src="/azuris-logo.png" alt="Azuris" className="h-9 w-9 object-contain" />
            <div className="leading-none">
              <div className="font-serif text-xl tracking-wide">AZURIS</div>
              <div className="mt-1 text-[0.5rem] uppercase tracking-[0.35em] text-[#C7A247]">Gemological</div>
            </div>
          </div>
          <span className={`rounded-full px-2.5 py-1 text-[0.5rem] uppercase tracking-[0.2em] ${active ? "bg-[#C7A247]/20 text-[#C7A247]" : "bg-white/10 text-white/60"}`}>
            {status}
          </span>
        </div>
        <div className="text-[0.55rem] uppercase tracking-[0.4em] text-[#FAF9F6]/70">{t("adminMembership.cardTitle")}</div>
        <div className="space-y-2">
          <div>
            <div className="text-[0.5rem] uppercase tracking-[0.2em] text-[#FAF9F6]/50">{t("adminMembership.memberName")}</div>
            <div className="font-serif text-lg">{memberName}</div>
          </div>
          <div className="flex items-end justify-between gap-3">
            <div>
              <div className="text-[0.5rem] uppercase tracking-[0.2em] text-[#FAF9F6]/50">{t("adminMembership.memberId")}</div>
              <div className="font-mono text-sm tracking-wider text-[#C7A247]">{cardNumber}</div>
            </div>
            <div className="text-right">
              <div className="text-[0.5rem] uppercase tracking-[0.2em] text-[#FAF9F6]/50">{t("adminMembership.memberSince")}</div>
              <div className="text-xs">{memberSince || "—"}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
