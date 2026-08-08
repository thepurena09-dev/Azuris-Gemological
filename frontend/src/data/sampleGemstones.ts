import type { Locale } from "@/config";

export interface SampleStone {
  id: string;
  certNumber: string;
  image: string;
  type: string;
  name: Record<Locale, string>;
  carat: string;
  cut: Record<Locale, string>;
  color: Record<Locale, string>;
  origin: Record<Locale, string>;
}

/**
 * Demo-only sample catalog (RC1). Frontend content for client review;
 * no backend, no prices (WhatsApp handoff per business rules).
 */
export const SAMPLE_STONES: SampleStone[] = [
  {
    id: "blue-sapphire",
    certNumber: "AZR-GEM-000101-26",
    image:
      "https://images.unsplash.com/photo-1605821771565-35e0d046a2fb?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
    type: "sapphire",
    name: { id: "Safir Biru", en: "Blue Sapphire" },
    carat: "3.15 ct",
    cut: { id: "Cushion", en: "Cushion" },
    color: { id: "Royal Blue", en: "Royal Blue" },
    origin: { id: "Ceylon, Sri Lanka", en: "Ceylon, Sri Lanka" },
  },
  {
    id: "ruby",
    certNumber: "AZR-GEM-000102-26",
    image:
      "https://images.unsplash.com/photo-1705575490492-4e91fd97bbb4?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
    type: "ruby",
    name: { id: "Ruby (Merah Delima)", en: "Ruby" },
    carat: "2.04 ct",
    cut: { id: "Oval", en: "Oval" },
    color: { id: "Pigeon Blood", en: "Pigeon Blood" },
    origin: { id: "Mozambik", en: "Mozambique" },
  },
  {
    id: "emerald",
    certNumber: "AZR-GEM-000103-26",
    image:
      "https://static.prod-images.emergentagent.com/jobs/6572b450-f0e7-4d20-83da-0f44a5e44dfd/images/8138fec9a0cfedc223c4896ebd58852071928246a1875cecdb3ce5aaebe929ad.jpeg",
    type: "emerald",
    name: { id: "Zamrud", en: "Emerald" },
    carat: "1.88 ct",
    cut: { id: "Emerald Cut", en: "Emerald Cut" },
    color: { id: "Hijau Pekat", en: "Vivid Green" },
    origin: { id: "Kolombia", en: "Colombia" },
  },
  {
    id: "diamond",
    certNumber: "AZR-GEM-000104-26",
    image:
      "https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
    type: "diamond",
    name: { id: "Berlian", en: "Diamond" },
    carat: "1.02 ct",
    cut: { id: "Round Brilliant", en: "Round Brilliant" },
    color: { id: "D · VVS1", en: "D · VVS1" },
    origin: { id: "Alami", en: "Natural" },
  },
  {
    id: "yellow-sapphire",
    certNumber: "AZR-GEM-000105-26",
    image:
      "https://images.unsplash.com/photo-1705575472028-d92d0bba6608?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
    type: "sapphire",
    name: { id: "Safir Kuning", en: "Yellow Sapphire" },
    carat: "4.22 ct",
    cut: { id: "Emerald Cut", en: "Emerald Cut" },
    color: { id: "Kuning Cerah", en: "Vivid Yellow" },
    origin: { id: "Ceylon, Sri Lanka", en: "Ceylon, Sri Lanka" },
  },
  {
    id: "pink-sapphire",
    certNumber: "AZR-GEM-000106-26",
    image:
      "https://images.unsplash.com/photo-1705575463786-474f9271b1e1?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
    type: "sapphire",
    name: { id: "Safir Merah Muda", en: "Pink Sapphire" },
    carat: "2.35 ct",
    cut: { id: "Oval", en: "Oval" },
    color: { id: "Merah Muda Cerah", en: "Vivid Pink" },
    origin: { id: "Madagaskar", en: "Madagascar" },
  },
];
