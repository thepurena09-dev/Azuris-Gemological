import * as React from "react";
import { CircleNotch, Plus, Trash, ArrowClockwise } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiJson } from "@/lib/api";

interface Warranty {
  uuid: string;
  warranty_number?: string | null;
  gemstone_id: string;
  status: string;
  terms_id: string;
  terms_en: string;
  period_months: number;
  start_date?: string | null;
  end_date?: string | null;
  version: number;
  is_current: boolean;
}

const EMPTY = { gemstone_id: "", terms_id: "", terms_en: "", period_months: 12, start_date: "" };

export default function WarrantiesPage() {
  const { t } = useLanguage();
  const [items, setItems] = React.useState<Warranty[]>([]);
  const [filterGem, setFilterGem] = React.useState("");
  const [form, setForm] = React.useState<any>(EMPTY);
  const [reissuing, setReissuing] = React.useState<string | null>(null);
  const [open, setOpen] = React.useState(false);
  const [busy, setBusy] = React.useState(false);
  const [err, setErr] = React.useState("");

  const load = React.useCallback(async () => {
    const qs = filterGem ? `?gemstone_id=${encodeURIComponent(filterGem)}&page_size=100` : "?page_size=100";
    const d = await apiJson<{ items: Warranty[] }>(`/api/admin/warranties${qs}`);
    setItems(d.items || []);
  }, [filterGem]);
  React.useEffect(() => { load(); }, [load]);

  const set = (k: string, v: any) => setForm((f: any) => ({ ...f, [k]: v }));
  const startAdd = () => { setForm(EMPTY); setReissuing(null); setErr(""); setOpen(true); };
  const startReissue = (w: Warranty) => {
    setForm({ gemstone_id: w.gemstone_id, terms_id: w.terms_id, terms_en: w.terms_en, period_months: w.period_months, start_date: w.start_date || "" });
    setReissuing(w.uuid); setErr(""); setOpen(true);
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true); setErr("");
    try {
      const body = JSON.stringify({ ...form, period_months: Number(form.period_months), start_date: form.start_date || null });
      if (reissuing) await apiJson(`/api/admin/warranties/${reissuing}/reissue`, { method: "POST", body });
      else await apiJson("/api/admin/warranties", { method: "POST", body });
      setOpen(false); setForm(EMPTY); setReissuing(null);
      await load();
    } catch (e: any) { setErr(e?.message || "Error"); } finally { setBusy(false); }
  };

  const setStatus = async (uuid: string, status: string) => {
    await apiJson(`/api/admin/warranties/${uuid}/status`, { method: "POST", body: JSON.stringify({ status }) });
    await load();
  };
  const remove = async (uuid: string) => {
    if (!window.confirm(t("adminWarranty.confirmDelete"))) return;
    await apiJson(`/api/admin/warranties/${uuid}`, { method: "DELETE" });
    await load();
  };

  const field = (k: string, label: string, type = "text") => (
    <div>
      <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">{label}</label>
      <input data-testid={`warranty-${k}`} type={type} value={form[k]} onChange={(e) => set(k, e.target.value)}
        className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-gold" />
    </div>
  );

  const statusColor = (s: string) => s === "active" ? "text-emerald-600" : s === "void" ? "text-red-600" : "text-amber-600";

  return (
    <section data-testid={TEST_IDS.page.adminWarranties} className="px-6 py-10 md:px-10 md:py-12">
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">{t("admin.title")}</p>
      <div className="mt-3 flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-serif text-4xl font-normal tracking-tight">{t("adminWarranty.title")}</h1>
        <button data-testid="warranty-add-btn" onClick={startAdd} className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground">
          <Plus size={14} /> {t("adminWarranty.add")}
        </button>
      </div>
      <p className="mt-3 max-w-2xl text-sm text-muted-foreground">{t("adminWarranty.subtitle")}</p>

      <div className="mt-6 max-w-md">
        <input data-testid="warranty-filter-gem" value={filterGem} onChange={(e) => setFilterGem(e.target.value)} placeholder={t("adminWarranty.filterGem")}
          className="w-full rounded-lg border border-border bg-card px-4 py-2.5 text-sm outline-none focus:border-gold" />
      </div>

      {open && (
        <form data-testid="warranty-form" onSubmit={submit} className="mt-6 rounded-2xl border border-border bg-card p-7">
          <div className="grid gap-4 sm:grid-cols-2">
            {field("gemstone_id", t("adminWarranty.gemstone"))}
            {field("period_months", t("adminWarranty.period"), "number")}
            {field("terms_id", t("adminWarranty.termsId"))}
            {field("terms_en", t("adminWarranty.termsEn"))}
            {field("start_date", t("adminWarranty.startDate"), "date")}
          </div>
          {err && <p data-testid="warranty-error" className="mt-3 text-sm text-red-600">{err}</p>}
          <div className="mt-5 flex gap-3">
            <button data-testid="warranty-save" type="submit" disabled={busy} className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-70">
              {busy ? <CircleNotch size={14} className="animate-spin" /> : null}{reissuing ? t("adminWarranty.reissue") : t("adminWarranty.save")}
            </button>
            <button type="button" onClick={() => setOpen(false)} className="rounded-lg border border-border px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-muted-foreground">{t("adminWarranty.cancel")}</button>
          </div>
        </form>
      )}

      <div className="mt-8 rounded-2xl border border-border bg-card p-2">
        {items.length === 0 ? (
          <p className="p-6 text-sm text-muted-foreground">{t("adminWarranty.empty")}</p>
        ) : (
          <ul className="divide-y divide-border">
            {items.map((w) => (
              <li key={w.uuid} data-testid={`warranty-item-${w.uuid}`} className="flex flex-wrap items-center justify-between gap-3 p-4">
                <div className="min-w-0">
                  <p className="flex items-center gap-2 truncate text-sm font-medium text-foreground">
                    <span className="font-mono text-gold">{w.warranty_number}</span>
                    <span className={`text-xs uppercase tracking-wide ${statusColor(w.status)}`}>{w.status}</span>
                    <span className="text-xs text-muted-foreground">v{w.version}{w.is_current ? " ·current" : ""}</span>
                  </p>
                  <p className="truncate text-xs text-muted-foreground">{w.gemstone_id} · {w.start_date || "—"} → {w.end_date || "—"}</p>
                </div>
                <div className="flex shrink-0 flex-wrap items-center gap-2">
                  {w.status === "active" && (
                    <>
                      <button data-testid={`warranty-void-${w.uuid}`} onClick={() => setStatus(w.uuid, "void")} className="rounded-md border border-border px-2.5 py-1.5 text-xs text-red-600">{t("adminWarranty.setVoid")}</button>
                      <button data-testid={`warranty-expire-${w.uuid}`} onClick={() => setStatus(w.uuid, "expired")} className="rounded-md border border-border px-2.5 py-1.5 text-xs text-amber-600">{t("adminWarranty.setExpired")}</button>
                    </>
                  )}
                  <button data-testid={`warranty-reissue-${w.uuid}`} onClick={() => startReissue(w)} className="rounded-md border border-border p-2 text-muted-foreground hover:text-foreground"><ArrowClockwise size={15} /></button>
                  <button data-testid={`warranty-delete-${w.uuid}`} onClick={() => remove(w.uuid)} className="rounded-md border border-border p-2 text-red-600 hover:bg-red-50"><Trash size={15} /></button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
