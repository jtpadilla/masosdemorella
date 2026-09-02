/**
 * Ajustos d'HTML per al text del llibre:
 * - <p><img></p>  →  <figure class="figura"><img><figcaption>alt</figcaption></figure>
 * - <img> del Markdown: amplada màxima de 1200 px (l'original va a ~2350 px)
 * - fitxers ed-*: il·lustracions d'esta edició → <figure class="figura editorial">
 * Les àncores de pàgina <a id="p23" class="pag" data-p="23"></a> arriben ja formades des del Markdown (són HTML en
 * brut i no passen per rehype).
 */
export default function rehypeBook() {
  return (tree) => walk(tree);
}

function walk(node) {
  if (!node.children) return;
  node.children = node.children.map((child) => {
    if (child.type !== 'element') return child;
    if (child.tagName === 'p') {
      const meaningful = child.children.filter((c) => !(c.type === 'text' && !c.value.trim()));
      if (meaningful.length === 1 && meaningful[0].type === 'element' && meaningful[0].tagName === 'img') {
        const img = meaningful[0];
        const caption = img.properties.alt ?? '';
        img.properties.width = 1200;
        const editorial = /(^|\/)ed-[^/]*$/.test(String(img.properties.src ?? ''));
        return {
          type: 'element',
          tagName: 'figure',
          properties: { className: editorial ? ['figura', 'editorial'] : ['figura'] },
          children: [
            img,
            { type: 'element', tagName: 'figcaption', properties: {}, children: [{ type: 'text', value: caption }] },
          ],
        };
      }
    }
    walk(child);
    return child;
  });
}
