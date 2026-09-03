/**
 * Ajustos d'HTML per al text del llibre:
 * - <p><img></p>  →  <figure class="figura"><img><figcaption>alt</figcaption></figure>
 * - <img> del Markdown: amplada màxima de 1200 px (l'original va a ~2350 px)
 * - fitxers ed-*: il·lustracions d'esta edició → <figure class="figura editorial">
 * - SVG: amplada real del dibuix (viewBox) i enllaç a /imatges/<fitxer> per a obrir-lo a mida completa (els rètols
 *   no es lligen a l'amplada de la columna). Opció { base } = base del lloc, per a l'enllaç.
 * Les àncores de pàgina <a id="p23" class="pag" data-p="23"></a> arriben ja formades des del Markdown (són HTML en
 * brut i no passen per rehype).
 */
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

export default function rehypeBook({ base = '/' } = {}) {
  return (tree, file) => walk(tree, { base: base.replace(/\/$/, ''), dir: file?.path ? dirname(file.path) : process.cwd() });
}

function svgWidth(path) {
  try {
    const m = readFileSync(path, 'utf8').match(/viewBox="[\d.]+ [\d.]+ ([\d.]+) /);
    return m ? Math.round(Number(m[1])) : null;
  } catch {
    return null;
  }
}

function walk(node, ctx) {
  if (!node.children) return;
  node.children = node.children.map((child) => {
    if (child.type !== 'element') return child;
    if (child.tagName === 'p') {
      const meaningful = child.children.filter((c) => !(c.type === 'text' && !c.value.trim()));
      if (meaningful.length === 1 && meaningful[0].type === 'element' && meaningful[0].tagName === 'img') {
        const img = meaningful[0];
        const caption = img.properties.alt ?? '';
        const src = String(img.properties.src ?? '');
        const editorial = /(^|\/)ed-[^/]*$/.test(src);
        const svg = /\.svg$/i.test(src);
        // Els SVG no necessiten srcset (Astro en copiava una desena de variants idèntiques per mapa): layout fix
        if (svg) img.properties.layout = 'none';
        img.properties.width = (svg && svgWidth(resolve(ctx.dir, src))) || 1200;
        const visual = svg
          ? { type: 'element', tagName: 'a', properties: { href: `${ctx.base}/imatges/${src.split('/').pop()}`, title: 'Obri la imatge a mida completa' }, children: [img] }
          : img;
        return {
          type: 'element',
          tagName: 'figure',
          properties: { className: editorial ? ['figura', 'editorial'] : ['figura'] },
          children: [
            visual,
            { type: 'element', tagName: 'figcaption', properties: {}, children: [{ type: 'text', value: caption }] },
          ],
        };
      }
    }
    walk(child, ctx);
    return child;
  });
}
