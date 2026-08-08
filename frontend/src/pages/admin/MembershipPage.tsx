import * as React from "react";
import { CircleNotch, Plus, Trash, ArrowClockwise, IdentificationCard, X } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiJson } from "@/lib/api";
import { appConfig } from "@/config";
import { MembershipCardVisual } from "@/components/membership/MembershipCardVisual";

interface Card {
  uuid: string;
  card_number: string;
  customer_id: string;
  masked_name: string;
  status: string;
  version: number;
  is_current: boolean;
  member_since?: string | null;
  verify_token?: string;
  verify_url?: string;
  qr_url?: string;
}
interface Customer { uuid: string; full_name: string; privacy_consent: boolean; }

export default function MembershipPage() {
  const { t } = useLanguage();
  const [items, setItems] = React.useState<Card[]>([]);
  const [customers, setCustomers] = React.useState<Customer[]>([]);
  const [pick, setPick] = React.useState("");
  const [open, setOpen] = React.useState(false);
  const [busy, setBusy] = React.useState(false);
  const [err, setErr] = React.useState("");
  const [detail, setDetail] = React.useState<Card | null>(null);

  const load = React.useCallback(async () => {
    const d = await apiJson<{ items: Card[] }>("/api/admin/membership?page_size=100");
    setItems(d.items || []);
  }, []);
  React.useEffect(() => {
    load();
    apiJson<{ items: Customer[] }>("/api/admin/customers?page_size=200").then((d) => setCustomers(d.items || [])).catch(() => {});
  }, [load]);

  const create = async (e: React.FormEvent) => {
    e.preventDefault(); if (!pick) return;
    setBusy(true); setErr("");
    try {
      await apiJson("/api/admin/membership", { method: "POST", body: JSON.stringify({ customer_id: pick }) });
      setPick(""); setOpen(false); await load();
    } catch (e: any) { setErr(e?.message || "Error"); } finally { setBusy(false); }
  };

  const setStatus = async (uuid: string, status: string) => {
    await apiJson(`/api/admin/membership/${uuid}/status`, { method: "POST", body: JSON.stringify({ status }) });
    await load();
  };
  const reissue = async (uuid: string) => {
    await apiJson(`/api/admin/membership/${uuid}/reissue`, { method: "POST" });
    await load();
  };
  const remove = async (uuid: string) => {
    if (!window.confirm(t("adminMembership.confirmDelete"))) return;
    await apiJson(`/api/admin/membership/${uuid}`, { method: "DELETE" });
    await load();
  };
  const viewCard = async (uuid: string) => {
    const c = await apiJson<Card>(`/api/admin/membership/${uuid}`);
    setDetail(c);
  };

  const consented = customers.filter((c) => c.privacy_consent);
  const qrSrc = detail?.qr_url ? `${appConfig.api.baseUrl}${detail.qr_url}` : null;

  return (
    <section data-testid={TEST_IDS.page.adminMembership} className="px-6 py-10 md:px-10 md:py-12">
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">{t("admin.title")}</p>
      <div className="mt-3 flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-serif text-4xl font-normal tracking-tight">{t("adminMembership.title")}</h1>
        <button data-testid="membership-add-btn" onClick={() => { setOpen(true); setErr(""); }} className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground">
          <Plus size={14} /> {t("adminMembership.add")}
        </button>
      </div>
      <p className="mt-3 max-w-2xl text-sm text-muted-foreground">{t("adminMembership.subtitle")}</p>

      {open && (
        <form data-testid="membership-form" onSubmit={create} className="mt-6 rounded-2xl border border-border bg-card p-7">
          <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">{t("adminMembership.customer")}</label>
          <select data-testid="membership-customer-select" value={pick} onChange={(e) => setPick(e.target.value)} className="w-full max-w-md rounded-lg border border-border bg-background px-3 py-2.5 text-sm">
            <option value="">{t("adminMembership.selectCustomer")}</option>
            {consented.map((c) => <option key={c.uuid} value={c.uuid}>{c.full_name}</option>)}
          </select>
          {err && <p data-testid="membership-error" className="mt-3 text-sm text-red-600">{err}</p>}
          <div className="mt-5 flex gap-3">
            <button data-testid="membership-save" type="submit" disabled={busy || !pick} className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-70">
              {busy ? <CircleNotch size={14} className="animate-spin" /> : null}{t("adminMembership.create")}
            </button>
            <button type="button" onClick={() => setOpen(false)} className="rounded-lg border border-border px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-muted-foreground">{t("adminMembership.cancel")}</button>
          </div>
        </form>
      )}

      <div className="mt-8 rounded-2xl border border-border bg-card p-2">
        {items.length === 0 ? (
          <p className="p-6 text-sm text-muted-foreground">{t("adminMembership.empty")}</p>
        ) : (
          <ul className="divide-y divide-border">
            {items.map((c) => (
              <li key={c.uuid} data-testid={`membership-item-${c.uuid}`} className="flex flex-wrap items-center justify-between gap-3 p-4">
                <div className="min-w-0">
                  <p className="flex items-center gap-2 truncate text-sm font-medium text-foreground">
                    <span className="font-mono text-gold">{c.card_number}</span>
                    <span className={`text-xs uppercase tracking-wide ${c.status === "active" ? "text-emerald-600" : "text-muted-foreground"}`}>{c.status}</span>
                    <span className="text-xs text-muted-foreground">v{c.version}</span>
                  </p>
                  <p className="truncate text-xs text-muted-foreground">{c.masked_name} · {t("adminMembership.memberSince")}: {c.member_since || "—"}</p>
                </div>
                <div className="flex shrink-0 flex-wrap items-center gap-2">
                  <button data-testid={`membership-view-${c.uuid}`} onClick={() => viewCard(c.uuid)} className="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1.5 text-xs text-foreground"><IdentificationCard size={14} /> {t("adminMembership.viewCard")}</button>
                  {c.status === "active"
                    ? <button data-testid={`membership-deactivate-${c.uuid}`} onClick={() => setStatus(c.uuid, "inactive")} className="rounded-md border border-border px-2.5 py-1.5 text-xs text-amber-600">{t("adminMembership.deactivate")}</button>
                    : <button data-testid={`membership-activate-${c.uuid}`} onClick={() => setStatus(c.uuid, "active")} className="rounded-md border border-border px-2.5 py-1.5 text-xs text-emerald-600">{t("adminMembership.activate")}</button>}
                  <button data-testid={`membership-reissue-${c.uuid}`} onClick={() => reissue(c.uuid)} className="rounded-md border border-border p-2 text-muted-foreground hover:text-foreground"><ArrowClockwise size={15} /></button>
                  <button data-testid={`membership-delete-${c.uuid}`} onClick={() => remove(c.uuid)} className="rounded-md border border-border p-2 text-red-600 hover:bg-red-50"><Trash size={15} /></button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {detail && (
        <div data-testid="membership-card-modal" className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onClick={() => setDetail(null)}>
          <div className="w-full max-w-md rounded-2xl bg-background p-6" onClick={(e) => e.stopPropagation()}>
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm font-medium">{detail.card_number}</p>
              <button data-testid="membership-card-close" onClick={() => setDetail(null)} className="rounded-md p-1.5 text-muted-foreground hover:text-foreground"><X size={18} /></button>
            </div>
            <div className="space-y-4">
              <MembershipCardVisual cardNumber={detail.card_number} memberName={detail.masked_name} memberSince={detail.member_since} status={detail.status} side="front" />
              <MembershipCardVisual cardNumber={detail.card_number} memberName={detail.masked_name} memberSince={detail.member_since} status={detail.status} qrSrc={qrSrc} side="back" />
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
