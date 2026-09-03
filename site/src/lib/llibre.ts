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
    file: 'ed-relleu-i-rius.svg',
    caption: 'Relleu i rius del terme de Morella: les muntanyes, els rius i el port de Torremiró que cita el capítol, i els municipis veïns',
    note: 'Elaborat per a esta edició amb límits, cims i rius d’OpenStreetMap (© col·laboradors d’OSM, ODbL). Les altituds són les del llibre; «Pinar» i «Morella la Vella» no tenen cim amb eixe nom en les fonts i van en posició aproximada. S’insereix al capítol 1, després del Mapa dels Ports.',
  },
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
  {
    file: 'ed-mas-de-julian.svg',
    caption: 'El Mas de Julian: croquis de l’entorn i lloc des d’on es van fer les fotografies del llibre',
    note: 'Traçat per a esta edició sobre l’ortofotografia PNOA (IGN, CC-BY 4.0), amb el camí d’OpenStreetMap; les posicions de càmera són aproximades. S’insereix a l’apartat 5.1, després de la fotografia del mas.',
  },
  {
    file: 'ed-roda-de-l-any.svg',
    caption: 'L’any al mas: faenes del camp, del ramat i de la casa i festes de cada mes, segons el llibre',
    note: 'Diagrama fet per a esta edició que reuneix les dates i faenes que el llibre dóna disperses pels capítols 3 a 7 (sembra, sega, esquiló, matança, trufa, romeries, Sant Antoni, Sexenni, Fira…); no hi ha cap dada que no siga del text. S’insereix al final del capítol 6, on l’autora resumeix el cicle de l’any.',
  },
];

export { render };
