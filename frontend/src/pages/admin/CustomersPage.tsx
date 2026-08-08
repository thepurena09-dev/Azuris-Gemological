import * as React from "react";
import { CircleNotch, Plus, PencilSimple, Trash, MagnifyingGlass, SealCheck } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiJson } from "@/lib/api";

interface Customer {
  uuid: string;
  full_name: string;
  email?: string | null;
  phone?: string | null;
  address_id?: string | null;
  privacy_consent: boolean;
  consent_at?: string | null;
  notes_id?: string | null;
}

const EMPTY = { full_name: "", email: "", phone: "", address_id: "", notes_id: "", privacy_consent: false };

export default function CustomersPage() {
  const { t } = useLanguage();
  const [items, setItems] = React.useState<Customer[]>([]);
  const [q, setQ] = React.useState("");
  const [form, setForm] = React.useState<any>(EMPTY);
  const [editing, setEditing] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);
  const [open, setOpen] = React.useState(false);

  const load = React.useCallback(async () => {
    const d = await apiJson<{ items: Customer[] }>(`/api/admin/customers?q=${encodeURIComponent(q)}&page_size=100`);
    setItems(d.items || []);
  }, [q]);
  React.useEffect(() => { load(); }, [load]);

  const set = (k: string, v: any) => setForm((f: any) => ({ ...f, [k]: v }));

  const startAdd = () => { setForm(EMPTY); setEditing(null); setOpen(true); };
  const startEdit = (c: Customer) => {
    setForm({ full_name: c.full_name, email: c.email || "", phone: c.phone || "", address_id: c.address_id || "", notes_id: c.notes_id || "", privacy_consent: c.privacy_consent });
    setEditing(c.uuid); setOpen(true);
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      const body = JSON.stringify({ ...form, email: form.email || null, phone: form.phone || null });
      if (editing) await apiJson(`/api/admin/customers/${editing}`, { method: "PUT", body });
      else await apiJson("/api/admin/customers", { method: "POST", body });
      setOpen(false); setForm(EMPTY); setEditing(null);
      await load();
    } finally { setBusy(false); }
  };

  const remove = async (uuid: string) => {
    if (!window.confirm(t("adminCustomers.confirmDelete"))) return;
    await apiJson(`/api/admin/customers/${uuid}`, { method: "DELETE" });
    await load();
  };

  const field = (k: string, label: string) => (
    <div>
      <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">{label}</label>
      <input data-testid={`customer-${k}`} value={form[k]} onChange={(e) => set(k, e.target.value)}
        className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-gold" />
    </div>
  );

  return (
    <section data-testid={TEST_IDS.page.adminCustomers} className="px-6 py-10 md:px-10 md:py-12">
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">{t("admin.title")}</p>
      <div className="mt-3 flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-serif text-4xl font-normal tracking-tight">{t("adminCustomers.title")}</h1>
        <button data-testid="customer-add-btn" onClick={startAdd} className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground">
          <Plus size={14} /> {t("adminCustomers.add")}
        </button>
      </div>
      <p className="mt-3 max-w-2xl text-sm text-muted-foreground">{t("adminCustomers.subtitle")}</p>

      <div className="mt-6 flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-2.5 max-w-md">
        <MagnifyingGlass size={16} className="text-muted-foreground" />
        <input data-testid="customer-search" value={q} onChange={(e) => setQ(e.target.value)} placeholder={t("adminCustomers.search")}
          className="w-full bg-transparent text-sm outline-none" />
      </div>

      {open && (
        <form data-testid="customer-form" onSubmit={submit} className="mt-6 rounded-2xl border border-border bg-card p-7">
          <div className="grid gap-4 sm:grid-cols-2">
            {field("full_name", t("adminCustomers.fullName"))}
            {field("email", t("adminCustomers.email"))}
            {field("phone", t("adminCustomers.phone"))}
            {field("address_id", t("adminCustomers.address"))}
            {field("notes_id", t("adminCustomers.notes"))}
            <label className="mt-6 flex items-center gap-2 text-sm text-foreground">
              <input data-testid="customer-consent" type="checkbox" checked={form.privacy_consent} onChange={(e) => set("privacy_consent", e.target.checked)} />
              {t("adminCustomers.consent")}
            </label>
          </div>
          <div className="mt-5 flex gap-3">
            <button data-testid="customer-save" type="submit" disabled={busy} className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-70">
              {busy ? <CircleNotch size={14} className="animate-spin" /> : null}{t("adminCustomers.save")}
            </button>
            <button type="button" onClick={() => setOpen(false)} className="rounded-lg border border-border px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-muted-foreground">{t("adminCustomers.cancel")}</button>
          </div>
        </form>
      )}

      <div className="mt-8 rounded-2xl border border-border bg-card p-2">
        {items.length === 0 ? (
          <p className="p-6 text-sm text-muted-foreground">{t("adminCustomers.empty")}</p>
        ) : (
          <ul className="divide-y divide-border">
            {items.map((c) => (
              <li key={c.uuid} data-testid={`customer-item-${c.uuid}`} className="flex items-center justify-between gap-3 p-4">
                <div className="min-w-0">
                  <p className="flex items-center gap-2 truncate text-sm font-medium text-foreground">
                    {c.full_name}
                    {c.privacy_consent && <SealCheck size={14} className="text-emerald-600" />}
                  </p>
                  <p className="truncate text-xs text-muted-foreground">{[c.email, c.phone].filter(Boolean).join(" · ") || "—"}</p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <button data-testid={`customer-edit-${c.uuid}`} onClick={() => startEdit(c)} className="rounded-md border border-border p-2 text-muted-foreground hover:text-foreground"><PencilSimple size={15} /></button>
                  <button data-testid={`customer-delete-${c.uuid}`} onClick={() => remove(c.uuid)} className="rounded-md border border-border p-2 text-red-600 hover:bg-red-50"><Trash size={15} /></button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
