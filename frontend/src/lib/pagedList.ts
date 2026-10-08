import { apiJson } from "@/lib/api";

/** Load every server page while preserving the existing searchable list UI. */
export async function allPages<T>(path: string): Promise<T[]> {
  const records: T[] = [];
  let page = 1;
  for (;;) {
    const result = await apiJson<{ items: T[]; total?: number }>(
      `${path}${path.includes("?") ? "&" : "?"}page=${page}&page_size=100`
    );
    const items = result.items || [];
    records.push(...items);
    if (result.total == null || records.length >= result.total || items.length === 0) return records;
    page += 1;
  }
}
