import * as React from "react";
import { CircleNotch, UploadSimple, Trash } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiFetch, apiJson } from "@/lib/api";

interface Credential {
  uuid: string;
  certificate_name: string;
  holder_name?: string;
  certificate_number?: string;
  issuer?: string;
  issue_date?: string;
  expiry_date?: string;
  status: string;
  short_description?: string;
  public_download_allowed?: boolean;
  publication_status: string;
  document_id?: string;
  document_url?: string;
}

const EMPTY = {
  certificate_name: "",
  holder_name: "",
  certificate_number: "",
  issuer: "",
  issue_date: "",
  expiry_date: "",
  status: "aktif",
  short_description: "",
  public_download_allowed: false,
};

export default function LegalityAdminPage() {
  const { t } = useLanguage();
  const [items, setItems] = React.useState<Credential[]>([]);
  const [form, setForm] = React.useState<any>(EMPTY);
  const [editing, setEditing] = React.useState<string | null>(null);
  const [msg, setMsg] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);

  const load = React.useCallback(async () => {
    const data = await apiJson<{ items: Credential[] }>("/api/admin/legality");
    setItems(data.items || []);
  }, []);

  React.useEffect(() => {
    load();
  }, [load]);

  const set = (k: string, v: any) => setForm((f: any) => ({ ...f, [k]: v }));

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setMsg(null);
    try {
      const path = editing ? `/api/admin/legality/${editing}` : "/api/admin/legality";
      const method = editing ? "PUT" : "POST";
      const saved = await apiJson<Credential>(path, { method, body: JSON.stringify(form) });
      if (!editing) setEditing(saved.uuid);
      setMsg(t("adminLegality.saved"));
      await load();
    } finally {
      setBusy(false);
    }
  };

  const edit = (c: Credential) => {
    setEditing(c.uuid);
    setForm({
      certificate_name: c.certificate_name || "",
      holder_name: c.holder_name || "",
      certificate_number: c.certificate_number || "",
      issuer: c.issuer || "",
      issue_date: c.issue_date || "",
      expiry_date: c.expiry_date || "",
      status: c.status || "aktif",
      short_description: c.short_description || "",
      public_download_allowed: !!c.public_download_allowed,
    });
  };

  const resetForm = () => {
    setEditing(null);
    setForm(EMPTY);
  };

  const publish = async (uuid: string, pub: boolean) => {
    await apiFetch(`/api/admin/legality/${uuid}/${pub ? "publish" : "unpublish"}`, { method: "POST" });
    await load();
  };
  const remove = async (uuid: string) => {
    await apiFetch(`/api/admin/legality/${uuid}`, { method: "DELETE" });
    if (editing === uuid) resetForm();
    await load();
  };

  const upload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !editing) return;
    setBusy(true);
    const fd = new FormData();
    fd.append("file", file);
    const res = await apiFetch(`/api/admin/legality/${editing}/document`, { method: "POST", body: fd });
    if (res.ok) setMsg(t("adminLegality.uploaded"));
    setBusy(false);
    await load();
  };

  const field = (k: string, label: string, type = "text") => (
    <div>
      <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">{label}</label>
      <input
        data-testid={`legality-${k}`}
        type={type}
        value={form[k] || ""}
        onChange={(e) => set(k, e.target.value)}
        className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-gold"
      />
    </div>
  );

  return (
    <section data-testid={TEST_IDS.page.adminLegality} className="px-6 py-10 md:px-10 md:py-12">
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">{t("admin.title")}</p>
      <h1 className="mt-3 font-serif text-4xl font-normal tracking-tight">{t("adminLegality.title")}</h1>
      <p className="mt-3 max-w-2xl text-sm text-muted-foreground">{t("adminLegality.subtitle")}</p>

      <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_1fr]">
        {/* Form */}
        <form onSubmit={save} className="rounded-2xl border border-border bg-card p-7">
          <div className="grid gap-4 sm:grid-cols-2">
            {field("certificate_name", t("adminLegality.name"))}
            {field("holder_name", t("adminLegality.holder"))}
            {field("certificate_number", t("adminLegality.number"))}
            {field("issuer", t("adminLegality.issuer"))}
            {field("issue_date", t("adminLegality.issueDate"), "date")}
            {field("expiry_date", t("adminLegality.expiry"), "date")}
            <div>
              <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">{t("adminLegality.status")}</label>
              <select
                data-testid="legality-status"
                value={form.status}
                onChange={(e) => set("status", e.target.value)}
                className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-gold"
              >
                <option value="aktif">Aktif</option>
                <option value="tidak_aktif">Tidak Aktif</option>
                <option value="kedaluwarsa">Kedaluwarsa</option>
                <option value="dalam_pembaruan">Dalam Pembaruan</option>
              </select>
            </div>
            <label className="flex items-center gap-2 self-end pb-2 text-sm text-foreground">
              <input
                data-testid="legality-download"
                type="checkbox"
                checked={form.public_download_allowed}
                onChange={(e) => set("public_download_allowed", e.target.checked)}
              />
              {t("adminLegality.download")}
            </label>
          </div>
          <div className="mt-4">
            <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">{t("adminLegality.description")}</label>
            <textarea
              data-testid="legality-short_description"
              value={form.short_description || ""}
              onChange={(e) => set("short_description", e.target.value)}
              rows={3}
              className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-gold"
            />
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              type="submit"
              data-testid="legality-save"
              disabled={busy}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-70"
            >
              {busy ? <CircleNotch size={14} className="animate-spin" /> : null}
              {t("adminLegality.save")}
            </button>
            {editing && (
              <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-gold px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-foreground">
                <UploadSimple size={16} className="text-gold" />
                {t("adminLegality.upload")}
                <input data-testid="legality-upload" type="file" accept="image/*,application/pdf" className="hidden" onChange={upload} />
              </label>
            )}
            {editing && (
              <button type="button" onClick={resetForm} className="text-[0.66rem] uppercase tracking-[0.2em] text-muted-foreground hover:text-foreground">
                + {t("adminLegality.create")}
              </button>
            )}
            {msg && <span className="text-sm text-emerald-600">{msg}</span>}
          </div>
        </form>

        {/* List */}
        <div className="rounded-2xl border border-border bg-card p-7">
          {items.length === 0 ? (
            <p className="text-sm text-muted-foreground">{t("adminLegality.empty")}</p>
          ) : (
            <ul className="space-y-4">
              {items.map((c) => (
                <li key={c.uuid} data-testid={`legality-item-${c.uuid}`} className="rounded-xl border border-border p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-serif text-lg tracking-tight text-foreground">{c.certificate_name}</p>
                      <p className="mt-1 text-xs text-muted-foreground">{c.certificate_number || "—"} · {c.issuer || "—"}</p>
                    </div>
                    <span className={`rounded-full px-3 py-1 text-[0.55rem] uppercase tracking-[0.18em] ${c.publication_status === "published" ? "bg-emerald-100 text-emerald-700" : "bg-secondary text-muted-foreground"}`}>
                      {c.publication_status === "published" ? t("adminLegality.published") : t("adminLegality.draft")}
                    </span>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-3">
                    <button onClick={() => edit(c)} className="text-[0.62rem] uppercase tracking-[0.18em] text-royal hover:underline">Edit</button>
                    {c.publication_status === "published" ? (
                      <button data-testid={`legality-unpublish-${c.uuid}`} onClick={() => publish(c.uuid, false)} className="text-[0.62rem] uppercase tracking-[0.18em] text-muted-foreground hover:text-foreground">{t("adminLegality.unpublish")}</button>
                    ) : (
                      <button data-testid={`legality-publish-${c.uuid}`} onClick={() => publish(c.uuid, true)} className="text-[0.62rem] uppercase tracking-[0.18em] text-gold hover:underline">{t("adminLegality.publish")}</button>
                    )}
                    <button onClick={() => remove(c.uuid)} className="inline-flex items-center gap-1 text-[0.62rem] uppercase tracking-[0.18em] text-red-600 hover:underline">
                      <Trash size={12} /> {t("adminLegality.delete")}
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
}
