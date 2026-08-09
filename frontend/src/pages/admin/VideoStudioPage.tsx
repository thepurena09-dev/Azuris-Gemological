import * as React from "react";
import {
  FilmSlate,
  CircleNotch,
  CheckCircle,
  XCircle,
  ArrowClockwise,
  FloppyDisk,
  Lock,
  ListChecks,
  MapTrifold,
  TextAlignLeft,
  ShieldCheck,
} from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { apiJson } from "@/lib/api";

type Scene = {
  id: string;
  index: number;
  segment: string;
  start: number;
  end: number;
  narration: string;
  subtitle: string;
  visual: string;
  action: string;
  feature: string;
  benefit: string;
  route: string;
  record_targets: string[];
  covers: string[];
  status: string;
};

type Feature = {
  id: string;
  feature: string;
  route: string;
  function: string;
  benefit: string;
  visual_action: string;
  priority: string;
};

const WORKFLOW = [
  { key: "audit", label: "Audit", phase: "A" },
  { key: "script", label: "Script", phase: "A" },
  { key: "voice", label: "Voice", phase: "B" },
  { key: "storyboard", label: "Storyboard", phase: "B" },
  { key: "timeline", label: "Timeline", phase: "B" },
  { key: "preview", label: "Preview", phase: "B" },
  { key: "sync", label: "Sync Check", phase: "A" },
  { key: "export", label: "Export", phase: "B" },
];

const fmt = (s: number) => {
  const m = Math.floor(s / 60);
  const sec = (s % 60).toFixed(1).padStart(4, "0");
  return `${m}:${sec}`;
};

const wc = (t: string) => (t.trim() ? t.trim().split(/\s+/).length : 0);

export default function VideoStudioPage() {
  const { t } = useLanguage();
  const [tab, setTab] = React.useState<"audit" | "blueprint" | "script" | "validate">("audit");
  const [audit, setAudit] = React.useState<any>(null);
  const [project, setProject] = React.useState<any>(null);
  const [scenes, setScenes] = React.useState<Scene[]>([]);
  const [validation, setValidation] = React.useState<any>(null);
  const [busy, setBusy] = React.useState(false);
  const [msg, setMsg] = React.useState<string | null>(null);
  const [open, setOpen] = React.useState<string | null>(null);

  React.useEffect(() => {
    apiJson<any>("/api/admin/video-studio/audit").then(setAudit);
    apiJson<any>("/api/admin/video-studio/project").then((p) => {
      setProject(p);
      setScenes(p.scenes || []);
    });
  }, []);

  const totalWords = scenes.reduce((n, s) => n + wc(s.narration), 0);
  const totalDur = scenes.length ? Math.max(...scenes.map((s) => s.end)) - Math.min(...scenes.map((s) => s.start)) : 0;

  const patchScene = (id: string, field: keyof Scene, value: string) =>
    setScenes((prev) => prev.map((s) => (s.id === id ? { ...s, [field]: value } : s)));

  const save = async () => {
    setBusy(true);
    setMsg(null);
    try {
      const saved = await apiJson<any>("/api/admin/video-studio/project", {
        method: "PUT",
        body: JSON.stringify({ title: project?.title, scenes }),
      });
      setProject(saved);
      setScenes(saved.scenes);
      setMsg("Script tersimpan.");
    } finally {
      setBusy(false);
    }
  };

  const reset = async () => {
    setBusy(true);
    setMsg(null);
    try {
      const seed = await apiJson<any>("/api/admin/video-studio/project/reset", { method: "POST" });
      setProject(seed);
      setScenes(seed.scenes);
      setMsg("Dipulihkan ke script default.");
    } finally {
      setBusy(false);
    }
  };

  const runValidate = async () => {
    setBusy(true);
    try {
      // validate the server's current saved copy
      const v = await apiJson<any>("/api/admin/video-studio/validate");
      setValidation(v);
    } finally {
      setBusy(false);
    }
  };

  const featureLabel = (fid: string) =>
    audit?.feature_map?.find((f: Feature) => f.id === fid)?.feature || fid;

  const TabBtn = ({ id, icon, label }: { id: any; icon: React.ReactNode; label: string }) => (
    <button
      type="button"
      data-testid={`vs-tab-${id}`}
      onClick={() => setTab(id)}
      className={`inline-flex items-center gap-2 rounded-lg border px-4 py-2.5 text-[0.66rem] uppercase tracking-[0.16em] transition-colors ${
        tab === id
          ? "border-gold/70 bg-gold/10 text-foreground"
          : "border-border bg-background text-muted-foreground hover:text-foreground"
      }`}
    >
      {icon}
      {label}
    </button>
  );

  return (
    <section data-testid="admin-video-studio" className="px-6 py-10 md:px-10 md:py-12">
      <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">{t("admin.title")}</p>
      <div className="mt-3 flex items-center gap-3">
        <FilmSlate size={30} weight="fill" className="text-gold" />
        <h1 className="font-serif text-4xl font-normal tracking-tight">Studio Video Walkthrough</h1>
      </div>
      <p className="mt-3 max-w-3xl text-sm text-muted-foreground">
        Hasilkan video demo produk 90 detik (TikTok 9:16) dari fitur nyata AZURIS. <b>Phase A</b>: audit, feature map,
        blueprint, dan script yang dapat diedit per-scene. Voice-over, screen recording, dan render MP4 tersedia di Phase B.
      </p>

      {/* Workflow stepper */}
      <div className="mt-6 flex flex-wrap items-center gap-2" data-testid="vs-workflow">
        {WORKFLOW.map((w, i) => (
          <React.Fragment key={w.key}>
            <span
              className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-[0.6rem] uppercase tracking-[0.15em] ${
                w.phase === "A"
                  ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-700"
                  : "border-border bg-secondary text-muted-foreground"
              }`}
            >
              {w.phase === "B" && <Lock size={11} weight="fill" />}
              {w.label}
            </span>
            {i < WORKFLOW.length - 1 && <span className="text-muted-foreground/40">→</span>}
          </React.Fragment>
        ))}
      </div>

      {/* Summary strip */}
      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Metric label="Halaman" value={audit?.counts?.pages ?? "—"} />
        <Metric label="Fitur" value={audit?.counts?.features ?? "—"} />
        <Metric label="Total Kata" value={totalWords} hint="target 210–225" />
        <Metric label="Durasi" value={`${totalDur.toFixed(1)}s`} hint="target 90 ± 1" />
      </div>

      {/* Tabs */}
      <div className="mt-8 flex flex-wrap gap-2">
        <TabBtn id="audit" icon={<ListChecks size={15} />} label="Audit & Fitur" />
        <TabBtn id="blueprint" icon={<MapTrifold size={15} />} label="Blueprint" />
        <TabBtn id="script" icon={<TextAlignLeft size={15} />} label="Script / Scene" />
        <TabBtn id="validate" icon={<ShieldCheck size={15} />} label="Validasi" />
      </div>

      {/* AUDIT + FEATURE MAP */}
      {tab === "audit" && audit && (
        <div className="mt-6 space-y-8" data-testid="vs-audit">
          <div>
            <h2 className="font-serif text-2xl">Peta Halaman ({audit.pages.length})</h2>
            <div className="mt-4 overflow-x-auto rounded-2xl border border-border">
              <table className="w-full text-left text-sm">
                <thead className="bg-secondary text-[0.6rem] uppercase tracking-[0.15em] text-muted-foreground">
                  <tr>
                    <th className="px-4 py-3">Grup</th>
                    <th className="px-4 py-3">Halaman</th>
                    <th className="px-4 py-3">Route</th>
                    <th className="px-4 py-3">Ringkasan</th>
                  </tr>
                </thead>
                <tbody>
                  {audit.pages.map((p: any, i: number) => (
                    <tr key={i} className="border-t border-border align-top">
                      <td className="px-4 py-3 text-xs text-muted-foreground">{p.group}</td>
                      <td className="px-4 py-3 font-medium">{p.name}</td>
                      <td className="px-4 py-3 font-mono text-xs text-royal">{p.route}</td>
                      <td className="px-4 py-3 text-xs text-muted-foreground">{p.summary}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <h2 className="font-serif text-2xl">Feature Map ({audit.feature_map.length})</h2>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {audit.feature_map.map((f: Feature) => (
                <div key={f.id} data-testid={`vs-feature-${f.id}`} className="rounded-xl border border-border bg-card p-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{f.feature}</span>
                    <span className="rounded-full border border-gold/40 px-2 py-0.5 text-[0.55rem] uppercase tracking-widest text-gold">
                      {f.priority}
                    </span>
                  </div>
                  <p className="mt-1 font-mono text-[0.7rem] text-royal">{f.route}</p>
                  <p className="mt-2 text-xs text-muted-foreground">{f.function}</p>
                  <p className="mt-1.5 text-xs"><b>Manfaat:</b> {f.benefit}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* BLUEPRINT */}
      {tab === "blueprint" && project && (
        <div className="mt-6 space-y-3" data-testid="vs-blueprint">
          {project.blueprint.map((b: any, i: number) => (
            <div key={i} className="flex items-start gap-4 rounded-xl border border-border bg-card p-4">
              <span className="mt-0.5 rounded-lg bg-primary px-3 py-1.5 font-mono text-xs text-primary-foreground">
                {b.start}s–{b.end}s
              </span>
              <div>
                <p className="text-[0.62rem] uppercase tracking-[0.2em] text-gold">{b.segment}</p>
                <p className="mt-1 text-sm text-muted-foreground">{b.goal}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* SCRIPT / SCENES */}
      {tab === "script" && (
        <div className="mt-6" data-testid="vs-script">
          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              data-testid="vs-save"
              onClick={save}
              disabled={busy}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-70"
            >
              {busy ? <CircleNotch size={14} className="animate-spin" /> : <FloppyDisk size={14} />}
              Simpan Script
            </button>
            <button
              type="button"
              data-testid="vs-reset"
              onClick={reset}
              disabled={busy}
              className="inline-flex items-center gap-2 rounded-lg border border-border px-5 py-2.5 text-[0.66rem] uppercase tracking-[0.2em] text-muted-foreground hover:text-foreground disabled:opacity-70"
            >
              <ArrowClockwise size={14} />
              Reset Default
            </button>
            {msg && <span className="text-sm text-emerald-600">{msg}</span>}
            <span className="ml-auto text-xs text-muted-foreground">
              {scenes.length} scene · {totalWords} kata · {totalDur.toFixed(1)}s
            </span>
          </div>

          <div className="mt-5 space-y-3">
            {scenes.map((s) => {
              const isOpen = open === s.id;
              return (
                <div key={s.id} data-testid={`vs-scene-${s.index}`} className="rounded-xl border border-border bg-card">
                  <button
                    type="button"
                    onClick={() => setOpen(isOpen ? null : s.id)}
                    className="flex w-full items-center gap-4 px-4 py-3 text-left"
                  >
                    <span className="rounded-lg bg-secondary px-2.5 py-1 font-mono text-xs">{String(s.index).padStart(2, "0")}</span>
                    <span className="font-mono text-xs text-royal">{fmt(s.start)}–{fmt(s.end)}</span>
                    <span className="text-[0.55rem] uppercase tracking-widest text-gold">{s.segment}</span>
                    <span className="min-w-0 flex-1 truncate text-sm text-muted-foreground">{s.narration}</span>
                    <span className="text-xs text-muted-foreground">{wc(s.narration)}k</span>
                  </button>

                  {isOpen && (
                    <div className="border-t border-border px-4 py-4">
                      <div className="grid gap-4 md:grid-cols-2">
                        <Field label="Narasi (voice-over)">
                          <textarea
                            data-testid={`vs-narration-${s.index}`}
                            value={s.narration}
                            onChange={(e) => patchScene(s.id, "narration", e.target.value)}
                            rows={3}
                            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-gold"
                          />
                        </Field>
                        <Field label="Visual">
                          <textarea
                            data-testid={`vs-visual-${s.index}`}
                            value={s.visual}
                            onChange={(e) => patchScene(s.id, "visual", e.target.value)}
                            rows={3}
                            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-gold"
                          />
                        </Field>
                        <Field label="Aksi Kursor / Interaksi">
                          <input
                            value={s.action}
                            onChange={(e) => patchScene(s.id, "action", e.target.value)}
                            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-gold"
                          />
                        </Field>
                        <Field label="Manfaat">
                          <input
                            value={s.benefit}
                            onChange={(e) => patchScene(s.id, "benefit", e.target.value)}
                            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-gold"
                          />
                        </Field>
                        <Field label="Route (untuk recording)">
                          <input
                            value={s.route}
                            onChange={(e) => patchScene(s.id, "route", e.target.value)}
                            className="w-full rounded-lg border border-border bg-background px-3 py-2 font-mono text-xs outline-none focus:border-gold"
                          />
                        </Field>
                        <Field label="Fitur">
                          <input
                            value={s.feature}
                            onChange={(e) => patchScene(s.id, "feature", e.target.value)}
                            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-gold"
                          />
                        </Field>
                      </div>
                      <div className="mt-3 flex flex-wrap items-center gap-2">
                        <span className="text-[0.6rem] uppercase tracking-widest text-muted-foreground">Cover fitur:</span>
                        {s.covers.length === 0 && <span className="text-xs text-muted-foreground/60">— (montase / penutup)</span>}
                        {s.covers.map((c) => (
                          <span key={c} className="rounded-full border border-royal/30 bg-royal/5 px-2 py-0.5 text-[0.6rem] text-royal">
                            {featureLabel(c)}
                          </span>
                        ))}
                        <span className="ml-auto inline-flex items-center gap-1 rounded-full border border-border px-2 py-0.5 text-[0.55rem] uppercase tracking-widest text-muted-foreground">
                          <Lock size={10} /> Regenerate scene · Phase B
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* VALIDATE */}
      {tab === "validate" && (
        <div className="mt-6" data-testid="vs-validate">
          <p className="text-sm text-muted-foreground">
            Validasi memeriksa versi <b>tersimpan</b> di server. Simpan script dulu jika baru diedit.
          </p>
          <button
            type="button"
            data-testid="vs-run-validate"
            onClick={runValidate}
            disabled={busy}
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-[0.66rem] uppercase tracking-[0.2em] text-primary-foreground disabled:opacity-70"
          >
            {busy ? <CircleNotch size={14} className="animate-spin" /> : <ShieldCheck size={14} />}
            Jalankan Validasi
          </button>

          {validation && (
            <div className="mt-6 space-y-3">
              <div
                className={`rounded-xl border p-4 text-sm ${
                  validation.ok ? "border-emerald-500/40 bg-emerald-500/5" : "border-red-500/40 bg-red-500/5"
                }`}
              >
                <b>{validation.ok ? "Semua pemeriksaan lolos" : "Ada pemeriksaan gagal"}</b> — {validation.passed}/{validation.total} ·{" "}
                {validation.word_count} kata · {validation.duration_sec}s
              </div>
              {validation.checks.map((c: any, i: number) => (
                <div key={i} className="flex items-start gap-3 rounded-lg border border-border bg-card px-4 py-3">
                  {c.pass ? (
                    <CheckCircle size={18} weight="fill" className="mt-0.5 shrink-0 text-emerald-600" />
                  ) : (
                    <XCircle size={18} weight="fill" className="mt-0.5 shrink-0 text-red-600" />
                  )}
                  <div>
                    <p className="text-sm font-medium">{c.check}</p>
                    <p className="text-xs text-muted-foreground">{c.detail}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}

const Metric = ({ label, value, hint }: { label: string; value: any; hint?: string }) => (
  <div className="rounded-xl border border-border bg-card p-4">
    <p className="text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">{label}</p>
    <p className="mt-1 font-serif text-2xl">{value}</p>
    {hint && <p className="text-[0.6rem] text-muted-foreground/70">{hint}</p>}
  </div>
);

const Field = ({ label, children }: { label: string; children: React.ReactNode }) => (
  <div>
    <label className="mb-1.5 block text-[0.6rem] uppercase tracking-[0.18em] text-muted-foreground">{label}</label>
    {children}
  </div>
);
