interface LogoProps {
  size?: number;
  withText?: boolean;
  variant?: "dark" | "light";
  className?: string;
  testId?: string;
}

/** Azuris official emblem (faceted-gem monogram) + optional wordmark. */
export function Logo({
  size = 42,
  withText = true,
  variant = "dark",
  className = "",
  testId = "azuris-logo",
}: LogoProps) {
  const textColor = variant === "light" ? "text-primary-foreground" : "text-foreground";
  const subColor = variant === "light" ? "text-primary-foreground/50" : "text-muted-foreground";
  return (
    <span className={`flex items-center gap-3 ${className}`} data-testid={testId}>
      <img
        src="/azuris-logo.png"
        alt="Azuris Gemological"
        width={size}
        height={size}
        style={{ width: size, height: size }}
        className="shrink-0 object-contain"
      />
      {withText && (
        <span className="flex flex-col leading-none">
          <span className={`font-serif text-[1.5rem] font-semibold tracking-tight ${textColor}`}>
            AZURIS
          </span>
          <span className={`mt-1 text-[0.5rem] uppercase tracking-[0.45em] ${subColor}`}>
            Gemological
          </span>
        </span>
      )}
    </span>
  );
}

export default Logo;
