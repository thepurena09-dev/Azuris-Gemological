import * as React from "react";
import { ShieldCheck, Certificate, Info, CircleNotch } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import { TEST_IDS } from "@/constants/testIds";

const CERT_RE = /^AZR-GEM-\d{4}-\d{6}$/;

type ResultState = "idle" | "loading" | "unavailable";

export default function VerificationForm() {
  const { t } = useLanguage();
  const [cert, setCert] = React.useState("");
  const [code, setCode] = React.useState("");
  const [state, setState] = React.useState<ResultState>("idle");
  const [error, setError] = React.useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const normalized = cert.trim().toUpperCase();
    if (!CERT_RE.test(normalized)) {
      setError(t("verify.formatError"));
      return;
    }
    if (!code.trim()) {
      setError(t("verify.codeRequired"));
      return;
    }

    setState("loading");
    // FASE 2 integration point: replace with real call to the verification API.
    // No fake VALID/INVALID result is produced while the backend is not available.
    await new Promise((r) => setTimeout(r, 700));
    setState("unavailable");
  };

  return (
    <div className="rounded-2xl border border-border bg-card p-7 shadow-[0_30px_70px_-45px_rgba(13,27,42,0.4)] md:p-9">
      <form data-testid={TEST_IDS.verify.form} onSubmit={onSubmit} noValidate className="space-y-5">
        <div>
          <label
            htmlFor="verify-cert"
            className="mb-2 block text-[0.62rem] uppercase tracking-[0.22em] text-muted-foreground"
          >
            {t("verify.certLabel")}
          </label>
          <div className="flex items-center gap-3 rounded-lg border border-border bg-background px-4 py-3 focus-within:border-gold">
            <Certificate size={18} weight="regular" className="shrink-0 text-gold" />
            <input
              id="verify-cert"
              data-testid={TEST_IDS.verify.certInput}
              value={cert}
              onChange={(e) => setCert(e.target.value)}
              placeholder={t("verify.certPlaceholder")}
              autoComplete="off"
              spellCheck={false}
              className="w-full bg-transparent text-sm uppercase tracking-wide text-foreground outline-none placeholder:text-muted-foreground/60"
            />
          </div>
        </div>

        <div>
          <label
            htmlFor="verify-code"
            className="mb-2 block text-[0.62rem] uppercase tracking-[0.22em] text-muted-foreground"
          >
            {t("verify.codeLabel")}
          </label>
          <div className="flex items-center gap-3 rounded-lg border border-border bg-background px-4 py-3 focus-within:border-gold">
            <ShieldCheck size={18} weight="regular" className="shrink-0 text-gold" />
            <input
              id="verify-code"
              data-testid={TEST_IDS.verify.codeInput}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder={t("verify.codePlaceholder")}
              autoComplete="off"
              className="w-full bg-transparent text-sm tracking-wide text-foreground outline-none placeholder:text-muted-foreground/60"
            />
          </div>
        </div>

        {error && (
          <p role="alert" className="text-sm text-red-600">
            {error}
          </p>
        )}

        <button
          type="submit"
          data-testid={TEST_IDS.verify.submit}
          disabled={state === "loading"}
          className="inline-flex w-full items-center justify-center gap-3 rounded-lg bg-primary px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground transition-shadow duration-300 hover:shadow-xl disabled:opacity-70"
        >
          {state === "loading" ? (
            <>
              <CircleNotch size={16} weight="bold" className="animate-spin" />
              {t("verify.submitting")}
            </>
          ) : (
            <>
              <ShieldCheck size={16} weight="regular" className="text-gold" />
              {t("verify.submit")}
            </>
          )}
        </button>
      </form>

      {/* Result area — neutral unavailable state only (no fake VALID/INVALID) */}
      <div data-testid={TEST_IDS.verify.result} aria-live="polite" className="mt-5">
        {state === "unavailable" && (
          <div className="flex items-start gap-3 rounded-lg border border-gold/40 bg-secondary p-5">
            <Info size={20} weight="regular" className="mt-0.5 shrink-0 text-gold" />
            <div>
              <p className="text-sm font-medium text-foreground">
                {t("verify.unavailableTitle")}
              </p>
              <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
                {t("verify.unavailable")}
              </p>
            </div>
          </div>
        )}
        {state === "idle" && (
          <p className="text-xs leading-relaxed text-muted-foreground/80">
            {t("verify.emptyHint")}
          </p>
        )}
      </div>
    </div>
  );
}
