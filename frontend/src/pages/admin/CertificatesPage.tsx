import * as React from "react";
import { CircleNotch, UploadSimple, SealCheck, FilePdf, Prohibit } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiFetch, apiJson } from "@/lib/api";

interface Gem {
  uuid: string;
  name_en: string;
  name_id: string;
  gemstone_type: string;
  weight_carat: number;
  certificate_id?: string;
  photo_id?: string;
}
interface Cert {
  uuid: string;
  certificate_number: string;
  status: string;
  version: number;
  is_current: boolean;
}

const EMPTY_GEM = {
  name_id: "", name_en: "", category: "Batu Mulia", gemstone_type: "",
  weight_carat: "", color: "", clarity: "", cut: "", shape: "", dimensions_mm: "", origin: "", treatment: "",
};

export default function CertificatesPage() {
  const { t } = useLanguage();
  const [gems, setGems] = React.useState<Gem[]>([]);
  const [certs, setCerts] = React.useState<Cert[]>([]);
  const [gem, setGem] = React.useState<any>(EMPTY_GEM);
  const [busy, setBusy] = React.useState(false);
  const [issueResult, setIssueResult] = React.useState<any>(null);
  const [examiner, setExaminer] = React.useState("");
  const [conclusion, setConclusion] = React.useState("");

  const load = React.useCallback(async () => {
    const [g, c] = await Promise.all([
      apiJson<{ items: Gem[] }>("/api/admin/gemstones"),
      apiJson<{ items: Cert[] }>("/api/admin/certificates"),
    ]);
    setGems(g.items || []);
    setCerts(c.items || []);
  }, []);
  React.useEffect(() => {
    load();
  }, [load]);

  const setG = (k: string, v: any) => setGem((f: any) => ({ ...f, [k]: v }));

  const createGem = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      await apiJson("/api/admin/gemstones", {
        method: "POST",
        body: JSON.stringify({ ...gem, weight_carat: parseFloat(gem.weight_carat) || 0 }),
      });
      setGem(EMPTY_GEM);
      await load();
    } finally {
      setBusy(false);
    }
  };

  const uploadPhoto = async (uuid: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    await apiFetch(`/api/admin/gemstones/${uuid}/photo`, { method: "POST", body: fd });
    await load();
  };

  const issue = async (uuid: string) => {
    setBusy(true);
    setIssueResult(null);
    try {
      const res = await apiJson<any>("/api/admin/certificates/issue", {
        method: "POST",
        body: JSON.stringify({ gemstone_id: uuid, examiner, conclusion }),
      });
      setIssueResult(res);
      await load();
    } finally {
      setBusy(false);
    }
  };

  const revoke = async (uuid: string) => {
    await apiFetch(`/api/admin/certificates/${uuid}/revoke`, { method: "POST" });
    await load();
  };

  const openPdf = (uuid: string) => {
    // stream with auth header, then open blob
    apiFetch(`/api/admin/certificates/${uuid}/pdf`).then(async (r) => {
      if (!r.ok) return;
      const blob = await r.blob();
      window.open(URL.createObjectURL(blob), "_blank");
    });
  };

  const gf = (k: string, label: string, type = "text") => (
    <div>
      <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">{label}</label>
      <input
        data-testid={`gem-${k}`}
        type={type}
        value={gem[k]}
        onChange={(e) => setG(k, e.target.value)}
        className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-gold"
      />
    </div>
  );

  return (
    <section data-testid={TEST_IDS.page.adminCertificates} className="px-6 py-10 md:px-10 md:py-12">
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">{t("admin.title")}</p>
      <h1 className="mt-3 font-serif text-4xl font-normal tracking-tight">{t("adminCert.title")}</h1>
      <p className="mt-3 max-w-2xl text-sm text-muted-foreground">{t("adminCert.subtitle")}</p>

      {issueResult && (
        <div data-testid="issue-result" className="mt-6 rounded-xl border border-emerald-300 bg-emerald-50 p-5">
          <p className="flex items-center gap-2 text-sm font-semibold text-emerald-700">
            <SealCheck size={18} weight="fill" /> {t("adminCert.issued")} — {issueResult.certificate_number}
          </p>
          <p className="mt-2 text-sm text-foreground">
            {t("adminCert.securityCodeNote")} <span data-testid="issue-security-code" className="font-mono font-bold tracking-widest">{issueResult.security_code}</span>
          </p>
          <p className="mt-1 break-all text-xs text-muted-foreground">{t("adminCert.qrNote")} {issueResult.qr_url}</p>
        </div>
      )}

      <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_1fr]">
        {/* Gemstone form */}
        <form onSubmit={createGem} className="rounded-2xl border border-border bg-card p-7">
          <h2 className="mb-4 text-xs uppercase tracking-[0.2em] text-foreground">{t("adminCert.newGem")}</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {gf("name_id", t("adminCert.gemNameId"))}
            {gf("name_en", t("adminCert.gemName"))}
            {gf("category", t("adminCert.category"))}
            {gf("gemstone_type", t("adminCert.type"))}
            {gf("weight_carat", t("adminCert.carat"), "number")}
            {gf("color", t("adminCert.color"))}
            {gf("clarity", t("adminCert.clarity"))}
            {gf("cut", t("adminCert.cut"))}
            {gf("shape", t("adminCert.shape"))}
            {gf("dimensions_mm", t("adminCert.dimensions"))}
            {gf("origin", t("adminCert.origin"))}
            {gf("treatment", t("adminCert.treatment"))}
          </div>
          <button data-testid="gem-save" type="submit" disabled={busy} className="mt-5 inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-70">
            {busy ? <CircleNotch size={14} className="animate-spin" /> : null}
            {t("adminCert.createGem")}
          </button>
        </form>

        {/* Issue controls + lists */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-border bg-card p-7">
            <h2 className="mb-4 text-xs uppercase tracking-[0.2em] text-foreground">{t("adminCert.gemstones")}</h2>
            <div className="mb-4 grid gap-3 sm:grid-cols-2">
              <input data-testid="issue-examiner" placeholder={t("adminCert.examiner")} value={examiner} onChange={(e) => setExaminer(e.target.value)} className="rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-gold" />
              <input data-testid="issue-conclusion" placeholder={t("adminCert.conclusion")} value={conclusion} onChange={(e) => setConclusion(e.target.value)} className="rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-gold" />
            </div>
            {gems.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t("adminCert.noGem")}</p>
            ) : (
              <ul className="space-y-3">
                {gems.map((g) => (
                  <li key={g.uuid} data-testid={`gem-item-${g.uuid}`} className="flex items-center justify-between gap-3 rounded-xl border border-border p-3">
                    <div className="min-w-0">
                      <p className="truncate text-sm text-foreground">{g.name_en} · {g.weight_carat} ct</p>
                      <p className="text-xs text-muted-foreground">{g.gemstone_type}</p>
                    </div>
                    <div className="flex shrink-0 items-center gap-2">
                      <label className="inline-flex cursor-pointer items-center gap-1 rounded-md border border-border px-2.5 py-1.5 text-[0.58rem] uppercase tracking-[0.15em] text-muted-foreground">
                        <UploadSimple size={13} /> {t("adminCert.uploadPhoto")}
                        <input type="file" accept="image/*" className="hidden" onChange={(e) => uploadPhoto(g.uuid, e)} />
                      </label>
                      {g.certificate_id ? (
                        <span className="rounded-md bg-emerald-100 px-2.5 py-1.5 text-[0.58rem] uppercase tracking-[0.15em] text-emerald-700">{t("adminCert.issuedBadge")}</span>
                      ) : (
                        <button data-testid={`issue-${g.uuid}`} onClick={() => issue(g.uuid)} disabled={busy} className="rounded-md bg-primary px-3 py-1.5 text-[0.58rem] uppercase tracking-[0.15em] text-primary-foreground disabled:opacity-70">
                          {t("adminCert.issue")}
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="rounded-2xl border border-border bg-card p-7">
            <h2 className="mb-4 text-xs uppercase tracking-[0.2em] text-foreground">{t("adminCert.certificates")}</h2>
            {certs.length === 0 ? (
              <p className="text-sm text-muted-foreground">—</p>
            ) : (
              <ul className="space-y-3">
                {certs.map((c) => (
                  <li key={c.uuid} data-testid={`cert-item-${c.uuid}`} className="flex items-center justify-between gap-3 rounded-xl border border-border p-3">
                    <div>
                      <p className="font-mono text-sm text-foreground">{c.certificate_number}</p>
                      <p className="text-xs text-muted-foreground">v{c.version} · {c.status}{c.is_current ? "" : " · archived"}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <button data-testid={`pdf-${c.uuid}`} onClick={() => openPdf(c.uuid)} className="inline-flex items-center gap-1 text-[0.62rem] uppercase tracking-[0.16em] text-royal hover:underline">
                        <FilePdf size={14} /> {t("adminCert.pdf")}
                      </button>
                      {c.status !== "revoked" && c.is_current && (
                        <button data-testid={`revoke-${c.uuid}`} onClick={() => revoke(c.uuid)} className="inline-flex items-center gap-1 text-[0.62rem] uppercase tracking-[0.16em] text-red-600 hover:underline">
                          <Prohibit size={13} /> {t("adminCert.revoke")}
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
