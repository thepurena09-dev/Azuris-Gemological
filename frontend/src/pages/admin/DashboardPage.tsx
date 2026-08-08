import * as React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import {
  ArrowClockwise,
  Certificate,
  SealCheck,
  Users,
  Diamond,
  Crown,
  ShieldCheck,
  ArrowsLeftRight,
  IdentificationCard,
  Image as ImageIcon,
  CircleNotch,
} from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";
import { apiJson } from "@/lib/api";

interface Overview {
  generated_at: string;
  totals: Record<string, number>;
  gemstones_by_status: Record<string, number>;
  certificates_by_status: Record<string, number>;
  warranties_by_status: Record<string, number>;
  transfers_by_status: Record<string, number>;
  memberships_by_status: Record<string, number>;
  verification: {
    total: number;
    by_result: Record<string, number>;
    series: { date: string; count: number; success: number }[];
  };
  admin_activity: { total: number; by_action: Record<string, number> };
  certificate_counter: { last_number: number; next_number: string; year: number };
}

const fmt = (n: number) => new Intl.NumberFormat().format(n);
const sumVals = (o: Record<string, number> = {}) =>
  Object.values(o).reduce((a, b) => a + b, 0);

function MetricCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-[0_20px_60px_-48px_rgba(13,27,42,0.4)]">
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/5 text-primary">
          {icon}
        </span>
        <p className="text-[0.62rem] uppercase tracking-[0.18em] text-muted-foreground">
          {label}
        </p>
      </div>
      <p className="mt-4 font-serif text-3xl font-normal tracking-tight text-foreground">
        {value}
      </p>
    </div>
  );
}

function Breakdown({ title, data }: { title: string; data: Record<string, number> }) {
  const { t } = useLanguage();
  const entries = Object.entries(data || {}).sort((a, b) => b[1] - a[1]);
  const total = sumVals(data) || 1;
  return (
    <div className="rounded-2xl border border-border bg-card p-6">
      <p className="text-[0.62rem] uppercase tracking-[0.22em] text-gold">{title}</p>
      {entries.length === 0 ? (
        <p className="mt-4 text-sm text-muted-foreground">{t("admin.dash.noData")}</p>
      ) : (
        <ul className="mt-4 space-y-3">
          {entries.map(([k, v]) => (
            <li key={k}>
              <div className="mb-1 flex items-center justify-between text-sm">
                <span className="capitalize text-foreground">{k.replace(/_/g, " ")}</span>
                <span className="font-medium text-muted-foreground">{fmt(v)}</span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
                <div
                  className="h-full rounded-full bg-primary/70"
                  style={{ width: `${Math.max((v / total) * 100, 4)}%` }}
                />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const { t } = useLanguage();
  const [data, setData] = React.useState<Overview | null>(null);
  const [busy, setBusy] = React.useState(true);
  const [err, setErr] = React.useState(false);

  const load = React.useCallback(async () => {
    setBusy(true);
    setErr(false);
    try {
      const d = await apiJson<Overview>("/api/admin/analytics/overview");
      setData(d);
    } catch {
      setErr(true);
    } finally {
      setBusy(false);
    }
  }, []);

  React.useEffect(() => {
    load();
  }, [load]);

  const totals = data?.totals || {};

  return (
    <section
      data-testid={TEST_IDS.page.adminDashboard}
      className="px-6 py-10 md:px-10 md:py-12"
    >
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-[0.7rem] uppercase tracking-[0.3em] text-muted-foreground">
            {t("admin.dash.eyebrow")}
          </p>
          <h1 className="mt-3 font-serif text-4xl font-normal tracking-tight md:text-5xl">
            {t("admin.dashboard")}
          </h1>
          <p className="mt-3 max-w-2xl text-sm text-muted-foreground">
            {t("admin.dash.subtitle")}
          </p>
        </div>
        <button
          data-testid={TEST_IDS.admin.dashRefresh}
          onClick={load}
          className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-5 py-3 text-[0.66rem] uppercase tracking-[0.2em] text-foreground transition-colors hover:border-gold"
        >
          <ArrowClockwise size={14} className={busy ? "animate-spin" : ""} />
          {t("admin.dash.refresh")}
        </button>
      </div>

      {busy && !data ? (
        <div className="mt-16 flex items-center justify-center gap-3 text-muted-foreground">
          <CircleNotch size={20} className="animate-spin" />
          {t("admin.dash.loading")}
        </div>
      ) : err ? (
        <div className="mt-10 rounded-2xl border border-red-200 bg-red-50 p-8 text-sm text-red-700">
          {t("admin.dash.error")}
        </div>
      ) : data ? (
        <div className="mt-10 space-y-10" data-testid="dash-loaded">
          {/* Metric cards */}
          <div
            data-testid={TEST_IDS.admin.dashMetrics}
            className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
          >
            <MetricCard icon={<Certificate size={20} />} label={t("admin.dash.certificates")} value={fmt(totals.certificates ?? 0)} />
            <MetricCard icon={<SealCheck size={20} />} label={t("admin.dash.verifications")} value={fmt(data.verification.total)} />
            <MetricCard icon={<Users size={20} />} label={t("admin.dash.customers")} value={fmt(totals.customers ?? 0)} />
            <MetricCard icon={<Diamond size={20} />} label={t("admin.dash.gemstones")} value={fmt(totals.gemstones ?? 0)} />
            <MetricCard icon={<Crown size={20} />} label={t("admin.dash.jewelry")} value={fmt(totals.jewelry ?? 0)} />
            <MetricCard icon={<ShieldCheck size={20} />} label={t("admin.dash.warranties")} value={fmt(totals.warranties ?? 0)} />
            <MetricCard icon={<ArrowsLeftRight size={20} />} label={t("admin.dash.transfers")} value={fmt(totals.ownership_transfers ?? 0)} />
            <MetricCard icon={<IdentificationCard size={20} />} label={t("admin.dash.memberships")} value={fmt(totals.membership_cards ?? 0)} />
          </div>

          {/* Verification trend */}
          <div className="rounded-2xl border border-border bg-card p-6">
            <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
              <p className="text-[0.62rem] uppercase tracking-[0.22em] text-gold">
                {t("admin.dash.verifyTrend")}
              </p>
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <span className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#0D1B2A]" /> {t("admin.dash.verifyTotal")}
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#C7A247]" /> {t("admin.dash.verifySuccess")}
                </span>
              </div>
            </div>
            <div data-testid={TEST_IDS.admin.dashVerifyChart} className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%" minHeight={256}>
                <LineChart data={data.verification.series} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E7E7E7" vertical={false} />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 11, fill: "#666" }}
                    tickFormatter={(d: string) => d.slice(5)}
                    tickLine={false}
                    axisLine={{ stroke: "#E7E7E7" }}
                  />
                  <YAxis
                    allowDecimals={false}
                    tick={{ fontSize: 11, fill: "#666" }}
                    tickLine={false}
                    axisLine={false}
                    width={40}
                  />
                  <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #E7E7E7", fontSize: 12 }} />
                  <Line type="monotone" dataKey="count" stroke="#0D1B2A" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="success" stroke="#C7A247" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Status breakdowns */}
          <div className="grid gap-6 lg:grid-cols-3">
            <Breakdown title={t("admin.dash.gemStatus")} data={data.gemstones_by_status} />
            <Breakdown title={t("admin.dash.certStatus")} data={data.certificates_by_status} />
            <Breakdown title={t("admin.dash.warrantyStatus")} data={data.warranties_by_status} />
            <Breakdown title={t("admin.dash.transferStatus")} data={data.transfers_by_status} />
            <Breakdown title={t("admin.dash.membershipStatus")} data={data.memberships_by_status} />
            <Breakdown title={t("admin.dash.verifyResults")} data={data.verification.by_result} />
          </div>

          {/* Admin activity + counter */}
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <Breakdown title={t("admin.dash.adminActivity")} data={data.admin_activity.by_action} />
            </div>
            <div className="rounded-2xl border border-border bg-primary p-6 text-primary-foreground">
              <p className="text-[0.62rem] uppercase tracking-[0.22em] text-gold">
                {t("admin.dash.counter")}
              </p>
              <p className="mt-5 text-[0.6rem] uppercase tracking-[0.18em] text-primary-foreground/50">
                {t("admin.dash.nextCertificate")}
              </p>
              <p className="mt-2 font-mono text-2xl tracking-tight text-gold">
                {data.certificate_counter.next_number}
              </p>
              <p className="mt-5 flex items-center gap-2 text-xs text-primary-foreground/60">
                <ImageIcon size={13} /> {t("admin.dash.media")}: {fmt(totals.media ?? 0)}
              </p>
            </div>
          </div>

          <p className="text-xs text-muted-foreground">
            {t("admin.dash.generatedAt")}: {new Date(data.generated_at).toLocaleString()}
          </p>
        </div>
      ) : null}
    </section>
  );
}
