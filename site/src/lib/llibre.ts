import { getCollection, getEntry, render, type CollectionEntry } from 'astro:content';

export type Capitol = CollectionEntry<'llibre'>;

export const llibre = (await getEntry('meta', 'llibre'))!.data;

/** Enllaç intern respectant `base` (el lloc pot viure a /repositori/). */
export function href(path: string): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  return `${base}/${path.replace(/^\//, '')}`;
}

/** "03-agricultura" → "agricultura" */
export function slugOf(entry: Capitol): string {
  return entry.id.replace(/^\d+-/, '');
}

/** Títol del capítol tal com apareix a l'original (majúscules), i una forma més llegible per a la navegació. */
export function titolCurt(title: string): string {
  const t = title.replace(/^\d+\.\s*/, '');
  return t === t.toUpperCase() ? t.charAt(0) + t.slice(1).toLowerCase() : t;
}

export function numeroCapitol(title: string): string | null {
  const m = title.match(/^(\d+)\./);
  return m ? m[1] : null;
}

export async function capitols(): Promise<Capitol[]> {
  const all = await getCollection('llibre');
  return all.sort((a, b) => a.data.order - b.data.order);
}

export interface Figura {
  n: number;            // ordre dins del llibre
  caption: string;
  file: string | null;  // null = il·lustració perduda a l'original
  capitol: Capitol;
}

/** Llista de figures en ordre d'aparició, extreta del propi Markdown. */
export async function figures(): Promise<Figura[]> {
  const out: Figura[] = [];
  const re = /!\[(.*?)\]\(\.\.\/assets\/images\/(.*?)\)|<figure class="perduda">.*?<figcaption>(.*?)<\/figcaption>/gs;
  for (const capitol of await capitols()) {
    if (slugOf(capitol) === 'index-d-illustracions') continue;
    for (const m of capitol.body!.matchAll(re)) {
      out.push({ n: out.length + 1, caption: m[1] ?? m[3], file: m[2] ?? null, capitol });
    }
  }
  return out;
}

/** Il·lustracions afegides per esta edició (no existien en l'original). Fitxers assets/images/ed-*.svg. */
export const figuresEdicio = [
  {
    file: 'ed-mapa-de-les-denes.svg',
    caption: 'Les dotze denes del terme de Morella, amb la Dena dels Llivis destacada',
    note: 'Elaborat per a esta edició amb els límits de les denes d’OpenStreetMap (© col·laboradors d’OSM, ODbL), amb la numeració i els noms del capítol 1, on s’insereix.',
  },
  {
    file: 'ed-mapa-dena-llivis.svg',
    caption: 'La Dena dels Llivis: els vint-i-un masos, les fonts, els barrancs, els camins i les colades',
    note: 'Elaborat per a esta edició amb el Nomenclàtor Toponímic Valencià i les vies pecuàries oficials (Generalitat Valenciana, CC-BY) i OpenStreetMap (ODbL); noms segons l’apartat 1.1, on s’insereix.',
  },
];

export { render };
