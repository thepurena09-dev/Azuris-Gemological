import * as React from "react";
import { CircleNotch, Plus, PencilSimple, Trash, MagnifyingGlass } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiJson } from "@/lib/api";

interface Jewelry {
  uuid: string;
  name_id: string;
  name_en: string;
  jewelry_type: string;
  material: string;
  gemstone_ids: string[];
  weight_grams?: number | null;
  status: string;
}
interface GemLite { uuid: string; name_en: string; gemstone_type: string; }

const EMPTY = { name_id: "", name_en: "", jewelry_type: "", material: "", weight_grams: "", dimensions_mm: "", gemstone_ids: [] as string[] };
const NEXT: Record<string, string[]> = { draft: ["published", "archived"], published: ["archived"], archived: ["published"] };

export default function JewelryPage() {
  const { t } = useLanguage();
  const [items, setItems] = React.useState<Jewelry[]>([]);
  const [gems, setGems] = React.useState<GemLite[]>([]);
  const [q, setQ] = React.useState("");
  const [status, setStatus] = React.useState("");
  const [form, setForm] = React.useState<any>(EMPTY);
  const [editing, setEditing] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);
  const [open, setOpen] = React.useState(false);

  const load = React.useCallback(async () => {
    const qs = `q=${encodeURIComponent(q)}&status=${status}&page_size=100`;
    const [j, g] = await Promise.all([
      apiJson<{ items: Jewelry[] }>(`/api/admin/jewelry?${qs}`),
      apiJson<{ items: GemLite[] }>("/api/admin/gemstones?page_size=200"),
    ]);
    setItems(j.items || []);
    setGems(g.items || []);
  }, [q, status]);
  React.useEffect(() => { load(); }, [load]);

  const set = (k: string, v: any) => setForm((f: any) => ({ ...f, [k]: v }));
  const toggleGem = (uuid: string) =>
    setForm((f: any) => ({ ...f, gemstone_ids: f.gemstone_ids.includes(uuid) ? f.gemstone_ids.filter((x: string) => x !== uuid) : [...f.gemstone_ids, uuid] }));

  const startAdd = () => { setForm(EMPTY); setEditing(null); setOpen(true); };
  const startEdit = (j: Jewelry) => {
    setForm({ name_id: j.name_id, name_en: j.name_en, jewelry_type: j.jewelry_type, material: j.material, weight_grams: j.weight_grams ?? "", dimensions_mm: "", gemstone_ids: j.gemstone_ids || [] });
    setEditing(j.uuid); setOpen(true);
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      const payload: any = { ...form, gemstone_ids: form.gemstone_ids };
      payload.weight_grams = form.weight_grams ? parseFloat(form.weight_grams) : null;
      if (!payload.dimensions_mm) delete payload.dimensions_mm;
      const body = JSON.stringify(payload);
      if (editing) await apiJson(`/api/admin/jewelry/${editing}`, { method: "PUT", body });
      else await apiJson("/api/admin/jewelry", { method: "POST", body });
      setOpen(false); setForm(EMPTY); setEditing(null);
      await load();
    } finally { setBusy(false); }
  };

  const changeStatus = async (uuid: string, next: string) => {
    await apiJson(`/api/admin/jewelry/${uuid}/status`, { method: "POST", body: JSON.stringify({ status: next }) });
    await load();
  };
  const remove = async (uuid: string) => {
    if (!window.confirm(t("adminJewelry.confirmDelete"))) return;
    await apiJson(`/api/admin/jewelry/${uuid}`, { method: "DELETE" });
    await load();
  };

  const field = (k: string, label: string, type = "text") => (
    <div>
      <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">{label}</label>
      <input data-testid={`jewelry-${k}`} type={type} value={form[k]} onChange={(e) => set(k, e.target.value)}
        className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-gold" />
    </div>
  );

  return (
    <section data-testid={TEST_IDS.page.adminJewelry} className="px-6 py-10 md:px-10 md:py-12">
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">{t("admin.title")}</p>
      <div className="mt-3 flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-serif text-4xl font-normal tracking-tight">{t("adminJewelry.title")}</h1>
        <button data-testid="jewelry-add-btn" onClick={startAdd} className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground">
          <Plus size={14} /> {t("adminJewelry.add")}
        </button>
      </div>
      <p className="mt-3 max-w-2xl text-sm text-muted-foreground">{t("adminJewelry.subtitle")}</p>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-2.5 max-w-md flex-1">
          <MagnifyingGlass size={16} className="text-muted-foreground" />
          <input data-testid="jewelry-search" value={q} onChange={(e) => setQ(e.target.value)} placeholder={t("adminJewelry.search")} className="w-full bg-transparent text-sm outline-none" />
        </div>
        <select data-testid="jewelry-status-filter" value={status} onChange={(e) => setStatus(e.target.value)} className="rounded-lg border border-border bg-card px-3 py-2.5 text-sm outline-none">
          <option value="">{t("adminJewelry.allStatus")}</option>
          <option value="draft">draft</option><option value="published">published</option><option value="archived">archived</option>
        </select>
      </div>

      {open && (
        <form data-testid="jewelry-form" onSubmit={submit} className="mt-6 rounded-2xl border border-border bg-card p-7">
          <div className="grid gap-4 sm:grid-cols-2">
            {field("name_id", t("adminJewelry.nameId"))}
            {field("name_en", t("adminJewelry.nameEn"))}
            {field("jewelry_type", t("adminJewelry.type"))}
            {field("material", t("adminJewelry.material"))}
            {field("weight_grams", t("adminJewelry.weight"), "number")}
            {field("dimensions_mm", t("adminJewelry.dimensions"))}
          </div>
          <div className="mt-5">
            <p className="mb-2 text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">{t("adminJewelry.gemstones")}</p>
            {gems.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t("adminJewelry.noGems")}</p>
            ) : (
              <div className="flex flex-wrap gap-2" data-testid="jewelry-gem-picker">
                {gems.map((g) => (
                  <button key={g.uuid} type="button" data-testid={`jewelry-gem-${g.uuid}`} onClick={() => toggleGem(g.uuid)}
                    className={`rounded-full border px-3 py-1.5 text-xs ${form.gemstone_ids.includes(g.uuid) ? "border-gold bg-gold/10 text-foreground" : "border-border text-muted-foreground"}`}>
                    {g.name_en}
                  </button>
                ))}
              </div>
            )}
          </div>
          <div className="mt-5 flex gap-3">
            <button data-testid="jewelry-save" type="submit" disabled={busy} className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-70">
              {busy ? <CircleNotch size={14} className="animate-spin" /> : null}{t("adminJewelry.save")}
            </button>
            <button type="button" onClick={() => setOpen(false)} className="rounded-lg border border-border px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-muted-foreground">{t("adminJewelry.cancel")}</button>
          </div>
        </form>
      )}

      <div className="mt-8 rounded-2xl border border-border bg-card p-2">
        {items.length === 0 ? (
          <p className="p-6 text-sm text-muted-foreground">{t("adminJewelry.empty")}</p>
        ) : (
          <ul className="divide-y divide-border">
            {items.map((j) => (
              <li key={j.uuid} data-testid={`jewelry-item-${j.uuid}`} className="flex flex-wrap items-center justify-between gap-3 p-4">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-foreground">{j.name_en} · {j.jewelry_type}</p>
                  <p className="text-xs text-muted-foreground">{j.material} · {(j.gemstone_ids || []).length} {t("adminJewelry.gemstones")} · <span className="uppercase tracking-wide">{j.status}</span></p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <select data-testid={`jewelry-status-${j.uuid}`} value="" onChange={(e) => e.target.value && changeStatus(j.uuid, e.target.value)} className="rounded-md border border-border px-2 py-1.5 text-xs text-muted-foreground">
                    <option value="">{t("adminJewelry.updateStatus")}</option>
                    {(NEXT[j.status] || []).map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                  <button data-testid={`jewelry-edit-${j.uuid}`} onClick={() => startEdit(j)} className="rounded-md border border-border p-2 text-muted-foreground hover:text-foreground"><PencilSimple size={15} /></button>
                  <button data-testid={`jewelry-delete-${j.uuid}`} onClick={() => remove(j.uuid)} className="rounded-md border border-border p-2 text-red-600 hover:bg-red-50"><Trash size={15} /></button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
