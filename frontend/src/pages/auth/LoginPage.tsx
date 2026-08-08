import * as React from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Lock, CircleNotch } from "@phosphor-icons/react";
import { useLanguage } from "@/i18n/LanguageContext";
import LanguageSwitcher from "@/components/layout/LanguageSwitcher";
import { TEST_IDS } from "@/constants/testIds";
import { useAuth } from "@/lib/auth";
import { useBusiness } from "@/lib/settings";

const PANEL_IMAGE =
  "https://images.unsplash.com/photo-1600287648597-d81be16a5a16?crop=entropy&cs=srgb&fm=jpg&q=90&w=1400";

export default function LoginPage() {
  const { t, locale } = useLanguage();
  const { login, admin } = useAuth();
  const { visuals } = useBusiness();
  const navigate = useNavigate();
  const panelImage = visuals?.login_image_url || PANEL_IMAGE;
  const panelAlt =
    (locale === "en" ? visuals?.login_image_alt_en : visuals?.login_image_alt_id) ||
    "Azuris gemstone";
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    if (admin) navigate("/admin/legalitas", { replace: true });
  }, [admin, navigate]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email.trim(), password);
      navigate("/admin/legalitas", { replace: true });
    } catch {
      setError(t("auth.error"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div data-testid={TEST_IDS.page.login} className="grid min-h-screen bg-background lg:grid-cols-2">
      <div className="relative hidden overflow-hidden bg-secondary lg:block">
        <img src={panelImage} alt={panelAlt} data-testid="login-panel-image" className="h-full w-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-background/40 via-transparent to-transparent" />
        <div className="absolute inset-0 flex flex-col justify-between p-14">
          <Link to="/" className="flex items-center gap-3">
            <img
              src="/azuris-logo.png"
              alt="Azuris Gemological"
              width={48}
              height={48}
              className="h-12 w-12 object-contain"
              data-testid="login-logo"
            />
            <span className="flex flex-col leading-none">
              <span className="font-serif text-2xl font-medium tracking-tight text-foreground">AZURIS</span>
              <span className="mt-1.5 text-[0.55rem] uppercase tracking-[0.45em] text-muted-foreground">
                Gemological
              </span>
            </span>
          </Link>
          <p className="max-w-sm font-serif text-4xl font-normal leading-tight tracking-tight text-foreground">
            {t("tagline")}
          </p>
        </div>
      </div>

      <div className="flex flex-col justify-center px-8 py-16 md:px-20">
        <div className="mb-14 flex items-center justify-between">
          <Link
            to="/"
            className="flex items-center gap-2 text-[0.7rem] uppercase tracking-[0.25em] text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft size={16} weight="thin" />
            {t("nav.home")}
          </Link>
          <LanguageSwitcher />
        </div>

        <div className="w-full max-w-sm">
          <div className="mb-6 flex items-center gap-4">
            <span className="h-px w-10 bg-gold" />
            <span className="flex items-center gap-2 text-[0.7rem] uppercase tracking-[0.3em] text-gold">
              <Lock size={16} weight="regular" />
              {t("admin.title")}
            </span>
          </div>
          <h1 className="font-serif text-5xl font-normal tracking-tight">{t("nav.login")}</h1>
          <p className="mt-4 text-sm leading-relaxed text-muted-foreground">{t("auth.subtitle")}</p>

          <form onSubmit={onSubmit} className="mt-10 space-y-5">
            <div>
              <label htmlFor="login-email" className="mb-2 block text-[0.62rem] uppercase tracking-[0.22em] text-muted-foreground">
                {t("auth.email")}
              </label>
              <input
                id="login-email"
                data-testid="login-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground outline-none focus:border-gold"
              />
            </div>
            <div>
              <label htmlFor="login-password" className="mb-2 block text-[0.62rem] uppercase tracking-[0.22em] text-muted-foreground">
                {t("auth.password")}
              </label>
              <input
                id="login-password"
                data-testid="login-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full rounded-lg border border-border bg-background px-4 py-3 text-sm text-foreground outline-none focus:border-gold"
              />
            </div>
            {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
            <button
              type="submit"
              data-testid="login-submit"
              disabled={loading}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-8 py-4 text-[0.7rem] uppercase tracking-[0.25em] text-primary-foreground transition-shadow duration-300 hover:shadow-xl disabled:opacity-70"
            >
              {loading ? <CircleNotch size={16} weight="bold" className="animate-spin" /> : null}
              {loading ? t("auth.signingIn") : t("auth.signIn")}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
