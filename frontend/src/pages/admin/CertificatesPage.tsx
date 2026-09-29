import * as React from "react";
import {
  DownloadSimple,
  Eye,
  MagnifyingGlass,
  Printer,
} from "@phosphor-icons/react";

import { apiFetch, apiJson } from "@/lib/api";

interface Certificate {
  uuid: string;
  certificate_number: string;
  gemstone_id: string;
  gemstone_name: string;
  gemstone_type?: string;
  origin?: string;
  status: string;
  version: number;
  issued_at: string;
}

const asset = (
  c: Certificate,
  kind: "pdf" | "card"
) => `/api/admin/certificates/${c.uuid}/${kind}`;

export default function CertificatesPage() {
  const [items, setItems] = React.useState<Certificate[]>([]);
  const [query, setQuery] = React.useState("");
  const [preview, setPreview] = React.useState<Certificate | null>(null);
  const [previewUrl, setPreviewUrl] = React.useState("");
  const [tab, setTab] = React.useState<"pdf" | "card">("pdf");
  const [error, setError] = React.useState("");

  React.useEffect(() => {
    void apiJson<{ items: Certificate[] }>(
      "/api/admin/certificates"
    ).then(({ items: records }) => {
      setItems(records || []);
    });
  }, []);

  React.useEffect(
    () => () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    },
    [previewUrl]
  );

  const filtered = React.useMemo(() => {
    const q = query.trim().toLowerCase();

    if (!q) return items;

    return items.filter((c) =>
      [
        c.certificate_number,
        c.gemstone_name,
        c.gemstone_type,
        c.origin,
        c.status,
        c.issued_at?.slice(0, 10),
      ]
        .filter(Boolean)
        .some((value) =>
          String(value).toLowerCase().includes(q)
        )
    );
  }, [items, query]);

  const fetchPdf = async (
    c: Certificate,
    kind: "pdf" | "card"
  ) => {
    const r = await apiFetch(asset(c, kind));

    if (!r.ok) {
      throw new Error(await r.text());
    }

    return r.blob();
  };

  const show = async (
    c: Certificate,
    kind: "pdf" | "card"
  ) => {
    try {
      setError("");

      const blob = await fetchPdf(c, kind);

      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }

      setPreview(c);
      setTab(kind);
      setPreviewUrl(URL.createObjectURL(blob));
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Unable to open document."
      );
    }
  };

  const close = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setPreview(null);
    setPreviewUrl("");
  };

  const download = async (
    c: Certificate,
    kind: "pdf" | "card"
  ) => {
    const blob = await fetchPdf(c, kind);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");

    a.href = url;
    a.download =
      `${c.certificate_number}` +
      `${kind === "card" ? "-card" : ""}.pdf`;

    document.body.appendChild(a);
    a.click();
    a.remove();

    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const print = async (
    c: Certificate,
    kind: "pdf" | "card"
  ) => {
    // Open immediately from the user's click so popup blockers
    // do not block the PDF print window after the async fetch.
    const w = window.open("", "_blank");

    if (!w) {
      return;
    }

    try {
      const blob = await fetchPdf(c, kind);
      const url = URL.createObjectURL(blob);

      w.location.href = url;

      window.setTimeout(() => {
        try {
          w.focus();
          w.print();
        } catch {
          // Native PDF viewer still exposes its own Print command.
        }
      }, 1400);

      window.setTimeout(() => {
        URL.revokeObjectURL(url);
      }, 30000);

    } catch (error) {
      w.close();
      throw error;
    }
  };

  return (
    <section className="px-5 py-8 md:px-10 md:py-10">
      <p className="text-[0.65rem] uppercase tracking-[0.25em] text-gold">
        Published Documents
      </p>

      <h1 className="mt-2 font-serif text-4xl">
        Certificates
      </h1>

      <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
        Published certificate and two-sided gemstone card
        records. Create and edit source data from Gemstones.
      </p>

      <div className="relative mt-6 max-w-xl">
        <MagnifyingGlass
          size={17}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
        />

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search certificate number, gemstone, type or origin"
          className="w-full rounded-xl border border-border bg-card py-3 pl-10 pr-4 text-sm outline-none transition focus:border-gold"
        />
      </div>

      {error && (
        <p className="mt-4 text-sm text-red-600">
          {error}
        </p>
      )}

      <div className="mt-5 overflow-hidden rounded-xl border border-border bg-card">
        {filtered.length === 0 ? (
          <p className="p-6 text-sm text-muted-foreground">
            {items.length === 0
              ? "No published certificates yet."
              : "No certificates match your search."}
          </p>
        ) : (
          <ul className="divide-y divide-border">
            {filtered.map((c) => (
              <li
                key={c.uuid}
                className="flex flex-col gap-4 p-4 xl:flex-row xl:items-center xl:justify-between"
              >
                <div>
                  <p className="font-medium">
                    {c.certificate_number}
                  </p>

                  <p className="mt-1 text-xs text-muted-foreground">
                    {c.gemstone_name}
                    {c.gemstone_type
                      ? ` · ${c.gemstone_type}`
                      : ""}
                    {c.origin
                      ? ` · ${c.origin}`
                      : ""}
                    {` · Issued ${c.issued_at?.slice(0, 10)}`}
                    {` · Version ${c.version}`}
                  </p>
                </div>

                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => void show(c, "pdf")}
                    className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 text-xs"
                  >
                    <Eye size={15} />
                    View Certificate
                  </button>

                  <button
                    onClick={() => void show(c, "card")}
                    className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 text-xs"
                  >
                    <Eye size={15} />
                    View Card
                  </button>

                  <button
                    onClick={() => void download(c, "pdf")}
                    className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 text-xs"
                  >
                    <DownloadSimple size={15} />
                    Download Certificate
                  </button>

                  <button
                    onClick={() => void download(c, "card")}
                    className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 text-xs"
                  >
                    <DownloadSimple size={15} />
                    Download Card
                  </button>

                  <button
                    onClick={() => void print(c, "pdf")}
                    className="inline-flex items-center gap-1.5 rounded-md border border-gold bg-gold/10 px-3 py-2 text-xs"
                  >
                    <Printer size={15} />
                    Print Certificate
                  </button>

                  <button
                    onClick={() => void print(c, "card")}
                    className="inline-flex items-center gap-1.5 rounded-md border border-gold bg-gold/10 px-3 py-2 text-xs"
                  >
                    <Printer size={15} />
                    Print Card
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {preview && (
        <div className="fixed inset-0 z-50 flex flex-col bg-black/80 p-3 md:p-8">
          <div className="mx-auto flex w-full max-w-6xl flex-wrap items-center justify-between gap-3 rounded-t-lg bg-background p-3">
            <div className="flex gap-2">
              <button
                onClick={() => void show(preview, "pdf")}
                className={`rounded-md px-4 py-2 text-xs ${
                  tab === "pdf"
                    ? "bg-primary text-primary-foreground"
                    : "border border-border"
                }`}
              >
                Certificate
              </button>

              <button
                onClick={() => void show(preview, "card")}
                className={`rounded-md px-4 py-2 text-xs ${
                  tab === "card"
                    ? "bg-primary text-primary-foreground"
                    : "border border-border"
                }`}
              >
                Card Front & Back
              </button>
            </div>

            <button
              onClick={close}
              className="rounded-md border border-border px-4 py-2 text-xs uppercase"
            >
              Close
            </button>
          </div>

          {previewUrl && (
            <iframe
              title={`${preview.certificate_number} preview`}
              src={previewUrl}
              className="mx-auto h-full w-full max-w-6xl rounded-b-lg bg-white"
            />
          )}
        </div>
      )}
    </section>
  );
}
