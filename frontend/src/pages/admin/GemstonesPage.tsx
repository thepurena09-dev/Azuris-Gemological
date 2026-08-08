import * as React from "react";
import { CircleNotch, Plus, PencilSimple, Trash, MagnifyingGlass, UploadSimple, Star, Image as ImageIcon } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiJson, apiFetch } from "@/lib/api";

interface Gem {
  uuid: string; name_id: string; name_en: string; category: string; gemstone_type: string;
  weight_carat: number; color?: string | null; origin?: string | null; status: string;
  certificate_id?: string | null; media_ids?: string[];
}
interface MediaItem { uuid: string; role: string; visibility: string; mime_type: string; }

const EMPTY = { name_id: "", name_en: "", category: "", gemstone_type: "", weight_carat: "", color: "", clarity: "", cut: "", shape: "", dimensions_mm: "", origin: "", treatment: "" };
const NEXT: Record<string, string[]> = {
  draft: ["verified", "archived"], verified: ["published", "archived"],
  published: ["transferred", "archived"], transferred: ["published", "archived"], archived: ["published"],
};

export default function GemstonesPage() {
  const { t } = useLanguage();
  const [items, setItems] = React.useState<Gem[]>([]);
  const [q, setQ] = React.useState("");
  const [status, setStatus] = React.useState("");
  const [form, setForm] = React.useState<any>(EMPTY);
  const [editing, setEditing] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);
  const [open, setOpen] = React.useState(false);
  const [mediaOpen, setMediaOpen] = React.useState<string | null>(null);
  const [media, setMedia] = React.useState<MediaItem[]>([]);

  const load = React.useCallback(async () => {
    const d = await apiJson<{ items: Gem[] }>(`/api/admin/gemstones?q=${encodeURIComponent(q)}&status=${status}&page_size=100`);
    setItems(d.items || []);
  }, [q, status]);
  React.useEffect(() => { load(); }, [load]);

  const set = (k: string, v: any) => setForm((f: any) => ({ ...f, [k]: v }));
  const startAdd = () => { setForm(EMPTY); setEditing(null); setOpen(true); };
  const startEdit = (g: Gem) => {
    setForm({ ...EMPTY, name_id: g.name_id, name_en: g.name_en, category: g.category, gemstone_type: g.gemstone_type, weight_carat: String(g.weight_carat), color: g.color || "", origin: g.origin || "" });
    setEditing(g.uuid); setOpen(true);
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      const body = JSON.stringify({ ...form, weight_carat: parseFloat(form.weight_carat) || 0 });
      if (editing) await apiJson(`/api/admin/gemstones/${editing}`, { method: "PUT", body });
      else await apiJson("/api/admin/gemstones", { method: "POST", body });
      setOpen(false); setForm(EMPTY); setEditing(null);
      await load();
    } finally { setBusy(false); }
  };

  const changeStatus = async (uuid: string, next: string) => {
    await apiJson(`/api/admin/gemstones/${uuid}/status`, { method: "POST", body: JSON.stringify({ status: next }) });
    await load();
  };
  const remove = async (uuid: string) => {
    if (!window.confirm(t("adminGemstones.confirmDelete"))) return;
    await apiJson(`/api/admin/gemstones/${uuid}`, { method: "DELETE" });
    await load();
  };

  const loadMedia = async (uuid: string) => {
    const d = await apiJson<{ items: MediaItem[] }>(`/api/admin/media?entity_type=gemstone&entity_id=${uuid}`);
    setMedia(d.items || []);
  };
  const openMedia = async (uuid: string) => { setMediaOpen(uuid); await loadMedia(uuid); };
  const uploadMedia = async (uuid: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file); fd.append("entity_type", "gemstone"); fd.append("entity_id", uuid);
    fd.append("role", "gallery"); fd.append("visibility", "public");
    await apiFetch("/api/admin/media", { method: "POST", body: fd });
    await loadMedia(uuid); await load();
  };
  const setMain = async (mUuid: string, gUuid: string) => {
    await apiJson(`/api/admin/media/${mUuid}/main`, { method: "POST" });
    await loadMedia(gUuid);
  };
  const delMedia = async (mUuid: string, gUuid: string) => {
    await apiJson(`/api/admin/media/${mUuid}`, { method: "DELETE" });
    await loadMedia(gUuid); await load();
  };

  const field = (k: string, label: string, type = "text") => (
    <div>
      <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">{label}</label>
      <input data-testid={`gemstone-${k}`} type={type} value={form[k]} onChange={(e) => set(k, e.target.value)}
        className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-gold" />
    </div>
  );

  return (
    <section data-testid={TEST_IDS.page.adminGemstones} className="px-6 py-10 md:px-10 md:py-12">
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">{t("admin.title")}</p>
      <div className="mt-3 flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-serif text-4xl font-normal tracking-tight">{t("adminGemstones.title")}</h1>
        <button data-testid="gemstone-add-btn" onClick={startAdd} className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground">
          <Plus size={14} /> {t("adminGemstones.add")}
        </button>
      </div>
      <p className="mt-3 max-w-2xl text-sm text-muted-foreground">{t("adminGemstones.subtitle")}</p>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-2.5 max-w-md flex-1">
          <MagnifyingGlass size={16} className="text-muted-foreground" />
          <input data-testid="gemstone-search" value={q} onChange={(e) => setQ(e.target.value)} placeholder={t("adminGemstones.search")} className="w-full bg-transparent text-sm outline-none" />
        </div>
        <select data-testid="gemstone-status-filter" value={status} onChange={(e) => setStatus(e.target.value)} className="rounded-lg border border-border bg-card px-3 py-2.5 text-sm outline-none">
          <option value="">{t("adminGemstones.allStatus")}</option>
          {["draft", "verified", "published", "transferred", "archived"].map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {open && (
        <form data-testid="gemstone-form" onSubmit={submit} className="mt-6 rounded-2xl border border-border bg-card p-7">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {field("name_id", t("adminGemstones.nameId"))}
            {field("name_en", t("adminGemstones.nameEn"))}
            {field("category", t("adminGemstones.category"))}
            {field("gemstone_type", t("adminGemstones.type"))}
            {field("weight_carat", t("adminGemstones.carat"), "number")}
            {field("color", t("adminGemstones.color"))}
            {field("clarity", t("adminGemstones.clarity"))}
            {field("cut", t("adminGemstones.cut"))}
            {field("shape", t("adminGemstones.shape"))}
            {field("dimensions_mm", t("adminGemstones.dimensions"))}
            {field("origin", t("adminGemstones.origin"))}
            {field("treatment", t("adminGemstones.treatment"))}
          </div>
          <div className="mt-5 flex gap-3">
            <button data-testid="gemstone-save" type="submit" disabled={busy} className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-70">
              {busy ? <CircleNotch size={14} className="animate-spin" /> : null}{t("adminGemstones.save")}
            </button>
            <button type="button" onClick={() => setOpen(false)} className="rounded-lg border border-border px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-muted-foreground">{t("adminGemstones.cancel")}</button>
          </div>
        </form>
      )}

      <div className="mt-8 rounded-2xl border border-border bg-card p-2">
        {items.length === 0 ? (
          <p className="p-6 text-sm text-muted-foreground">{t("adminGemstones.empty")}</p>
        ) : (
          <ul className="divide-y divide-border">
            {items.map((g) => (
              <li key={g.uuid} data-testid={`gemstone-item-${g.uuid}`} className="p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-foreground">{g.name_en} · {g.weight_carat} ct</p>
                    <p className="text-xs text-muted-foreground">{g.gemstone_type}{g.origin ? ` · ${g.origin}` : ""} · <span className="uppercase tracking-wide">{g.status}</span>{g.certificate_id ? ` · ${t("adminGemstones.hasCert")}` : ""}</p>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <select data-testid={`gemstone-status-${g.uuid}`} value="" onChange={(e) => e.target.value && changeStatus(g.uuid, e.target.value)} className="rounded-md border border-border px-2 py-1.5 text-xs text-muted-foreground">
                      <option value="">{t("adminGemstones.updateStatus")}</option>
                      {(NEXT[g.status] || []).map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                    <button data-testid={`gemstone-media-${g.uuid}`} onClick={() => openMedia(mediaOpen === g.uuid ? "" : g.uuid)} className="rounded-md border border-border p-2 text-muted-foreground hover:text-foreground"><ImageIcon size={15} /></button>
                    <button data-testid={`gemstone-edit-${g.uuid}`} onClick={() => startEdit(g)} className="rounded-md border border-border p-2 text-muted-foreground hover:text-foreground"><PencilSimple size={15} /></button>
                    <button data-testid={`gemstone-delete-${g.uuid}`} onClick={() => remove(g.uuid)} disabled={!!g.certificate_id} className="rounded-md border border-border p-2 text-red-600 hover:bg-red-50 disabled:opacity-40"><Trash size={15} /></button>
                  </div>
                </div>

                {mediaOpen === g.uuid && (
                  <div data-testid={`gemstone-media-panel-${g.uuid}`} className="mt-4 rounded-xl border border-border bg-secondary p-4">
                    <div className="mb-3 flex items-center justify-between">
                      <span className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{t("adminGemstones.media")}</span>
                      <label className="inline-flex cursor-pointer items-center gap-1 rounded-md border border-border bg-background px-2.5 py-1.5 text-[0.58rem] uppercase tracking-[0.15em] text-muted-foreground">
                        <UploadSimple size={13} /> {t("adminGemstones.uploadMedia")}
                        <input data-testid={`gemstone-media-upload-${g.uuid}`} type="file" accept="image/*,application/pdf" className="hidden" onChange={(e) => uploadMedia(g.uuid, e)} />
                      </label>
                    </div>
                    {media.length === 0 ? (
                      <p className="text-xs text-muted-foreground">—</p>
                    ) : (
                      <ul className="space-y-2">
                        {media.map((m) => (
                          <li key={m.uuid} data-testid={`media-item-${m.uuid}`} className="flex items-center justify-between gap-2 rounded-md border border-border bg-background px-3 py-2 text-xs">
                            <span className="truncate text-muted-foreground">{m.role} · {m.visibility} · {m.mime_type}</span>
                            <span className="flex shrink-0 items-center gap-2">
                              {m.role !== "main" && <button data-testid={`media-main-${m.uuid}`} onClick={() => setMain(m.uuid, g.uuid)} className="inline-flex items-center gap-1 text-royal hover:underline"><Star size={12} /> {t("adminGemstones.setMain")}</button>}
                              {m.role === "main" && <Star size={12} weight="fill" className="text-gold" />}
                              <button data-testid={`media-del-${m.uuid}`} onClick={() => delMedia(m.uuid, g.uuid)} className="text-red-600 hover:underline"><Trash size={13} /></button>
                            </span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
