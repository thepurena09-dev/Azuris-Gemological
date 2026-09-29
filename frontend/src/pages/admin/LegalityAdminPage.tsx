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
  signatory_name?: string;
  signatory_position?: string;
  signature_document_id?: string;
  signature_url?: string;
  active_for_certificates?: boolean;
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
  signatory_name: "H.Zulfikar.se.GG",
  signatory_position: "",
  active_for_certificates: false,
};

export default function LegalityAdminPage() {
  const { t } = useLanguage();
  const [items, setItems] = React.useState<Credential[]>([]);
  const [form, setForm] = React.useState<any>(EMPTY);
  const [editing, setEditing] = React.useState<string | null>(null);
  const [msg, setMsg] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);
  const [sigPreview, setSigPreview] = React.useState<string | null>(null);
  const [sigBusy, setSigBusy] = React.useState(false);
  const [activeSigPreview, setActiveSigPreview] = React.useState<string | null>(null);
  const [activeSigExists, setActiveSigExists] = React.useState(false);
  const [activeSigBusy, setActiveSigBusy] = React.useState(false);

  const [pendingSignature, setPendingSignature] = React.useState<File | null>(null);

  const loadSignature = React.useCallback(async (uuid: string) => {
    const res = await apiFetch(`/api/admin/legality/${uuid}/signature`);
    if (!res.ok) {
      setSigPreview(null);
      return;
    }
    const blob = await res.blob();
    setSigPreview((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return URL.createObjectURL(blob);
    });
  }, []);

  const loadActiveSignature = React.useCallback(async () => {
    try {
      const status = await apiJson<{
        active: boolean;
        has_signature: boolean;
        signatory_name?: string;
      }>("/api/admin/legality/active-signature/status");

      setActiveSigExists(
        !!status.active && !!status.has_signature
      );

      if (!status.active || !status.has_signature) {
        setActiveSigPreview((prev) => {
          if (prev) URL.revokeObjectURL(prev);
          return null;
        });
        return;
      }

      const res = await apiFetch(
        "/api/admin/legality/active-signature/file"
      );

      if (!res.ok) return;

      const blob = await res.blob();

      setActiveSigPreview((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return URL.createObjectURL(blob);
      });
    } catch {
      setActiveSigExists(false);
    }
  }, []);

  const uploadActiveSignature = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];

    if (!file) return;

    setActiveSigBusy(true);
    setMsg(null);

    try {
      const fd = new FormData();
      fd.append("file", file);

      const res = await apiFetch(
        "/api/admin/legality/active-signature",
        {
          method: "POST",
          body: fd,
        }
      );

      if (!res.ok) {
        const text = await res.text();
        setMsg(text || "Signature upload failed.");
        return;
      }

      setMsg("Authorised signature saved.");
      await loadActiveSignature();
      await load();
    } finally {
      setActiveSigBusy(false);
      e.target.value = "";
    }
  };

  const load = React.useCallback(async () => {
    const data = await apiJson<{ items: Credential[] }>("/api/admin/legality");
    setItems(data["items"] || []);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  React.useEffect(() => {
    load();
    loadActiveSignature();
  }, [load, loadActiveSignature]);

  const set = (k: string, v: any) => setForm((f: any) => ({ ...f, [k]: v }));

  const save = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!String(form.certificate_name || "").trim()) {
      setMsg("Certificate Name is required.");
      return;
    }
    setBusy(true);
    setMsg(null);
    try {
      const path = editing ? `/api/admin/legality/${editing}` : "/api/admin/legality";
      const method = editing ? "PUT" : "POST";
      const saved = await apiJson<Credential>(path, { method, body: JSON.stringify(form) });

      const targetUuid = editing || saved.uuid;

      if (!editing) setEditing(saved.uuid);

      if (pendingSignature && targetUuid) {
        const fd = new FormData();
        fd.append("file", pendingSignature);

        const sigRes = await apiFetch(
          `/api/admin/legality/${targetUuid}/signature`,
          { method: "POST", body: fd }
        );

        if (!sigRes.ok) {
          throw new Error("Failed to upload authorised signature");
        }

        setPendingSignature(null);
        await loadSignature(targetUuid);
      }

      setMsg(
        pendingSignature
          ? "Legality record and authorised signature saved."
          : t("adminLegality.saved")
      );

      await load();
    } catch (error) {
      setMsg(error instanceof Error ? error.message : "Failed to save the legality record and signature.");
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
      signatory_name: c.signatory_name || "",
      signatory_position: c.signatory_position || "",
      active_for_certificates: !!c.active_for_certificates,
    });
    setMsg(null);
    if (c.signature_document_id) loadSignature(c.uuid);
    else setSigPreview(null);
  };

  const resetForm = () => {
    setEditing(null);
    setForm(EMPTY);
    setSigPreview(null);
    setPendingSignature(null);
    setMsg(null);
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

  const uploadSignature = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !editing) return;
    setSigBusy(true);
    const fd = new FormData();
    fd.append("file", file);
    const res = await apiFetch(`/api/admin/legality/${editing}/signature`, { method: "POST", body: fd });
    if (res.ok) {
      setMsg(t("adminLegality.signatureUploaded"));
      await loadSignature(editing);
      await load();
    } else {
      setMsg("Failed to upload the authorised signature.");
    }
    setSigBusy(false);
    e.target.value = "";
  };

  const removeSignature = async () => {
    if (!editing) return;
    setSigBusy(true);
    const res = await apiFetch(`/api/admin/legality/${editing}/signature`, { method: "DELETE" });
    if (res.ok) {
      setSigPreview((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return null;
      });
      setMsg(t("adminLegality.signatureRemoved"));
      await load();
    }
    setSigBusy(false);
  };

  const field = (k: string, label: string, type = "text") => (
    <div>
      <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">{label}</label>
      <input
        data-testid={`legality-${k}`}
        type={type}
        required={k === "certificate_name"}
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

      <div className="mt-6 rounded-2xl border border-gold/40 bg-card p-5">
        <p className="text-[0.62rem] font-semibold uppercase tracking-[0.2em] text-gold">
          Certificate & Card Signature
        </p>

        <div className="mt-4 flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="font-serif text-xl">
              H.Zulfikar.se.GG
            </p>

            <p className="mt-1 max-w-xl text-sm text-muted-foreground">
              This image is attached to the Legality record marked
              Active for Certificates and is used by both Certificate
              and Card rendering.
            </p>
          </div>

          <div className="flex flex-col items-start gap-3">
            {activeSigPreview ? (
              <div className="flex h-20 w-52 items-center justify-center rounded-lg border border-border bg-white p-2">
                <img
                  src={activeSigPreview}
                  alt="Authorised signature"
                  className="max-h-full max-w-full object-contain"
                />
              </div>
            ) : (
              <div className="flex h-20 w-52 items-center justify-center rounded-lg border border-dashed border-border px-4 text-center text-xs text-muted-foreground">
                No signature saved on the active Legality record
              </div>
            )}

            <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-gold px-4 py-2.5 text-[0.62rem] uppercase tracking-[0.15em]">
              {activeSigBusy ? (
                <CircleNotch
                  size={14}
                  className="animate-spin text-gold"
                />
              ) : (
                <UploadSimple
                  size={14}
                  className="text-gold"
                />
              )}

              {activeSigExists
                ? "Replace Signature"
                : "Upload Signature"}

              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                className="hidden"
                disabled={activeSigBusy}
                onChange={uploadActiveSignature}
              />
            </label>
          </div>
        </div>
      </div>

      {/* Non-persistent guidance panel. */}
      <div data-testid="legality-info-panel" className="mt-6 grid gap-5 lg:grid-cols-2">
        <div className="rounded-2xl border border-royal/25 bg-royal/5 p-5">
          <p className="text-[0.62rem] uppercase tracking-[0.2em] text-royal">About Legality Records</p>
          <ul className="mt-3 space-y-2 text-[0.82rem] leading-relaxed text-foreground">
            <li>• Store the institution's official licence, accreditation, or credential details here.</li>
            <li>• The active record and authorised signatory are copied into each new certificate snapshot.</li>
            <li>• Later changes do not alter certificates that have already been issued.</li>
            <li>• The uploaded signature appears on certificate page 2.</li>
            <li>• Public download controls access to the related legality document.</li>
            <li>• Keep only one record active for new certificates.</li>
          </ul>
        </div>
        <div className="rounded-2xl border border-dashed border-gold/50 bg-gold/5 p-5">
          <p className="text-[0.62rem] font-bold uppercase tracking-[0.2em] text-gold">
            Example Only — Not an Official Credential
          </p>
          <dl className="mt-3 grid grid-cols-1 gap-x-6 gap-y-1.5 text-[0.82rem] text-foreground sm:grid-cols-2">
            {[
              ["Certificate Name", "Gemological Laboratory Accreditation"],
              ["Holder / Institution", "Azuris Gemological Research"],
              ["Certificate Number", "AGR-ACC-EXAMPLE-001"],
              ["Issuer", "Example Accreditation Authority"],
              ["Issue Date", "01/01/2026"],
              ["Valid Until", "31/12/2030"],
              ["Signatory Name", "Dr. A. Pratama"],
              ["Position / Title", "Chief Gemologist"],
            ].map(([k, val]) => (
              <div key={k}>
                <dt className="text-[0.6rem] uppercase tracking-[0.14em] text-muted-foreground">{k}</dt>
                <dd className="font-medium">{val}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-2 text-[0.78rem] text-muted-foreground">
            Description: Institutional gemological examination credential.
          </p>
          <p className="mt-3 text-[0.72rem] italic text-muted-foreground">
            This example is guidance only; it is not stored or displayed publicly.
          </p>
        </div>
      </div>

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
                <option value="aktif">Active</option>
                <option value="tidak_aktif">Inactive</option>
                <option value="kedaluwarsa">Expired</option>
                <option value="dalam_pembaruan">Being Updated</option>
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

          {/* Certificate legality source */}
          <div className="mt-6 rounded-xl border border-border bg-secondary/20 p-4">
            <p className="text-[0.62rem] uppercase tracking-[0.18em] text-muted-foreground">
              Certificate Legality Source
            </p>

            <label className="mt-3 flex items-center gap-2 text-sm text-foreground">
              <input
                data-testid="legality-active"
                type="checkbox"
                checked={form.active_for_certificates}
                onChange={(e) =>
                  set("active_for_certificates", e.target.checked)
                }
              />
              Use this legality record for new certificate details
            </label>

            <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
              The authorised signature is managed globally above and is not
              stored inside this legality record.
            </p>
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              type="submit"
              data-testid="legality-save"
              disabled={busy}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-70"
            >
              {busy ? <CircleNotch size={14} className="animate-spin" /> : null}
              {pendingSignature ? "Save and Apply Signature" : t("adminLegality.save")}
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
            {msg && (
            <span className={`text-sm ${msg.startsWith("Failed") ? "text-red-600" : "text-emerald-600"}`}>
              {msg}
            </span>
          )}
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
                    <div className="flex flex-col items-end gap-1.5">
                      <span className={`rounded-full px-3 py-1 text-[0.55rem] uppercase tracking-[0.18em] ${c.publication_status === "published" ? "bg-emerald-100 text-emerald-700" : "bg-secondary text-muted-foreground"}`}>
                        {c.publication_status === "published" ? t("adminLegality.published") : t("adminLegality.draft")}
                      </span>
                      {c.active_for_certificates && (
                        <span data-testid={`legality-active-badge-${c.uuid}`} className="rounded-full bg-gold/20 px-3 py-1 text-[0.55rem] uppercase tracking-[0.18em] text-gold">
                          {t("adminLegality.activeBadge")}
                        </span>
                      )}
                    </div>
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
