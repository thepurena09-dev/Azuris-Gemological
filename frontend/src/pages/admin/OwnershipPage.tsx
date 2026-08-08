import * as React from "react";
import { MagnifyingGlass, ArrowsLeftRight, UserPlus } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiJson } from "@/lib/api";

interface OwnerSummary { uuid: string; full_name: string; masked_name: string; }
interface Transfer { uuid: string; previous_owner_id?: string | null; new_owner_id: string; status: string; transfer_date?: string | null; }
interface Ownership {
  gemstone_id: string;
  gemstone_status: string;
  current_owner: OwnerSummary | null;
  history: Transfer[];
  pending_transfer: Transfer | null;
}
interface Customer { uuid: string; full_name: string; }

export default function OwnershipPage() {
  const { t } = useLanguage();
  const [gem, setGem] = React.useState("");
  const [data, setData] = React.useState<Ownership | null>(null);
  const [customers, setCustomers] = React.useState<Customer[]>([]);
  const [assignTo, setAssignTo] = React.useState("");
  const [transferTo, setTransferTo] = React.useState("");
  const [err, setErr] = React.useState("");
  const [code, setCode] = React.useState("");
  const [busy, setBusy] = React.useState(false);

  React.useEffect(() => {
    apiJson<{ items: Customer[] }>("/api/admin/customers?page_size=200").then((d) => setCustomers(d.items || [])).catch(() => {});
  }, []);

  const nameOf = (uuid?: string | null) => customers.find((c) => c.uuid === uuid)?.full_name || uuid || "—";

  const load = async () => {
    setErr(""); setCode("");
    try {
      const d = await apiJson<Ownership>(`/api/admin/ownership/gemstone/${encodeURIComponent(gem.trim())}`);
      setData(d);
    } catch (e: any) { setData(null); setErr(t("adminOwnership.notFound")); }
  };

  const assign = async () => {
    if (!assignTo) return;
    setBusy(true); setErr("");
    try {
      await apiJson("/api/admin/ownership/assign", { method: "POST", body: JSON.stringify({ gemstone_id: data!.gemstone_id, owner_id: assignTo }) });
      setAssignTo(""); await load();
    } catch (e: any) { setErr(e?.message || "Error"); } finally { setBusy(false); }
  };

  const createTransfer = async () => {
    if (!transferTo) return;
    setBusy(true); setErr("");
    try {
      await apiJson("/api/admin/ownership/transfers", { method: "POST", body: JSON.stringify({ gemstone_id: data!.gemstone_id, new_owner_id: transferTo }) });
      setTransferTo(""); await load();
    } catch (e: any) { setErr(e?.message || "Error"); } finally { setBusy(false); }
  };

  const complete = async (uuid: string) => {
    setBusy(true); setErr("");
    try {
      const r = await apiJson<{ new_security_code?: string }>(`/api/admin/ownership/transfers/${uuid}/complete`, { method: "POST" });
      if (r?.new_security_code) setCode(r.new_security_code);
      await load();
    } catch (e: any) { setErr(e?.message || "Error"); } finally { setBusy(false); }
  };
  const cancel = async (uuid: string) => {
    setBusy(true);
    try { await apiJson(`/api/admin/ownership/transfers/${uuid}/cancel`, { method: "POST" }); await load(); }
    finally { setBusy(false); }
  };

  return (
    <section data-testid={TEST_IDS.page.adminOwnership} className="px-6 py-10 md:px-10 md:py-12">
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">{t("admin.title")}</p>
      <h1 className="mt-3 font-serif text-4xl font-normal tracking-tight">{t("adminOwnership.title")}</h1>
      <p className="mt-3 max-w-2xl text-sm text-muted-foreground">{t("adminOwnership.subtitle")}</p>

      <div className="mt-6 flex max-w-xl items-center gap-3">
        <div className="flex flex-1 items-center gap-3 rounded-lg border border-border bg-card px-4 py-2.5">
          <MagnifyingGlass size={16} className="text-muted-foreground" />
          <input data-testid="ownership-gem-input" value={gem} onChange={(e) => setGem(e.target.value)} placeholder={t("adminOwnership.gemLabel")}
            className="w-full bg-transparent text-sm outline-none" />
        </div>
        <button data-testid="ownership-load-btn" onClick={load} className="rounded-lg bg-primary px-5 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground">{t("adminOwnership.load")}</button>
      </div>

      {err && <p data-testid="ownership-error" className="mt-4 text-sm text-red-600">{err}</p>}
      {code && <p data-testid="ownership-new-code" className="mt-4 rounded-lg border border-gold/40 bg-gold/5 px-4 py-3 text-sm">{t("adminOwnership.codeNote")} <span className="font-mono font-semibold text-gold">{code}</span></p>}

      {data && (
        <div data-testid="ownership-panel" className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-border bg-card p-6">
            <p className="text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground">{t("adminOwnership.gemStatus")}</p>
            <p className="mt-1 text-sm font-medium">{data.gemstone_status}</p>
            <hr className="my-4 border-border" />
            <p className="text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground">{t("adminOwnership.currentOwner")}</p>
            {data.current_owner ? (
              <p data-testid="ownership-current-owner" className="mt-1 text-sm">{data.current_owner.full_name} <span className="text-muted-foreground">({data.current_owner.masked_name})</span></p>
            ) : (
              <p className="mt-1 text-sm text-muted-foreground">{t("adminOwnership.noOwner")}</p>
            )}

            {!data.current_owner && (
              <div className="mt-4 flex items-center gap-2">
                <select data-testid="ownership-assign-select" value={assignTo} onChange={(e) => setAssignTo(e.target.value)} className="flex-1 rounded-lg border border-border bg-background px-3 py-2.5 text-sm">
                  <option value="">{t("adminOwnership.selectCustomer")}</option>
                  {customers.map((c) => <option key={c.uuid} value={c.uuid}>{c.full_name}</option>)}
                </select>
                <button data-testid="ownership-assign-btn" onClick={assign} disabled={busy || !assignTo} className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-[0.62rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-60">
                  <UserPlus size={14} /> {t("adminOwnership.assign")}
                </button>
              </div>
            )}

            {data.current_owner && !data.pending_transfer && (
              <div className="mt-5">
                <p className="text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground">{t("adminOwnership.newTransfer")}</p>
                <div className="mt-2 flex items-center gap-2">
                  <select data-testid="ownership-transfer-select" value={transferTo} onChange={(e) => setTransferTo(e.target.value)} className="flex-1 rounded-lg border border-border bg-background px-3 py-2.5 text-sm">
                    <option value="">{t("adminOwnership.selectCustomer")}</option>
                    {customers.filter((c) => c.uuid !== data.current_owner?.uuid).map((c) => <option key={c.uuid} value={c.uuid}>{c.full_name}</option>)}
                  </select>
                  <button data-testid="ownership-transfer-btn" onClick={createTransfer} disabled={busy || !transferTo} className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-[0.62rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-60">
                    <ArrowsLeftRight size={14} /> {t("adminOwnership.create")}
                  </button>
                </div>
              </div>
            )}

            {data.pending_transfer && (
              <div data-testid="ownership-pending" className="mt-5 rounded-lg border border-amber-300 bg-amber-50 p-4">
                <p className="text-xs font-medium text-amber-700">{t("adminOwnership.pending")}</p>
                <p className="mt-1 text-xs text-muted-foreground">{t("adminOwnership.to")}: {nameOf(data.pending_transfer.new_owner_id)}</p>
                <div className="mt-3 flex gap-2">
                  <button data-testid="ownership-complete-btn" onClick={() => complete(data.pending_transfer!.uuid)} disabled={busy} className="rounded-lg bg-primary px-4 py-2 text-[0.62rem] uppercase tracking-[0.2em] text-primary-foreground">{t("adminOwnership.complete")}</button>
                  <button data-testid="ownership-cancel-btn" onClick={() => cancel(data.pending_transfer!.uuid)} disabled={busy} className="rounded-lg border border-border px-4 py-2 text-[0.62rem] uppercase tracking-[0.2em] text-muted-foreground">{t("adminOwnership.cancel")}</button>
                </div>
              </div>
            )}
          </div>

          <div className="rounded-2xl border border-border bg-card p-6">
            <p className="text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground">{t("adminOwnership.history")}</p>
            {data.history.length === 0 ? (
              <p className="mt-2 text-sm text-muted-foreground">{t("adminOwnership.noHistory")}</p>
            ) : (
              <ul className="mt-3 space-y-3">
                {data.history.map((h) => (
                  <li key={h.uuid} data-testid={`ownership-history-${h.uuid}`} className="rounded-lg border border-border p-3 text-xs">
                    <span className="text-muted-foreground">{t("adminOwnership.from")}:</span> {nameOf(h.previous_owner_id)} → <span className="text-muted-foreground">{t("adminOwnership.to")}:</span> {nameOf(h.new_owner_id)}
                    <span className="ml-2 text-muted-foreground">{(h.transfer_date || "").slice(0, 10)}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
