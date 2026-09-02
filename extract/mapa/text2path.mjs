// Rótulos → glifos SVG con EB Garamond (fontsource, woff) mediante opentype.js. Cada glifo (peso, tamaño, carácter)
// se define una sola vez (<path id>) y los rótulos lo reutilizan con <use>, para que el SVG pese poco.
// Uso: node text2path.mjs [dir node_modules con opentype.js] < entrada.json > salida.json
//   (por defecto, site/node_modules: opentype.js es dependencia de desarrollo del sitio)
//   entrada: [{id, text, size, weight, tracking}]
//   salida:  {items: {id: {width, uses: "<use .../>..."}}, defs: "<path id=... d=.../>..."}
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
const nodeModules = process.argv[2] ?? new URL('../../site/node_modules/', import.meta.url).pathname;
const require = createRequire(nodeModules.replace(/\/?$/, '/'));
const opentype = require('opentype.js');
const fontsDir = new URL('../../site/node_modules/@fontsource/eb-garamond/files/', import.meta.url).pathname;
const fonts = {};
function font(weight) {
  if (!fonts[weight]) {
    const buf = readFileSync(`${fontsDir}eb-garamond-latin-${weight}-normal.woff`);
    fonts[weight] = opentype.parse(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength));
  }
  return fonts[weight];
}
const items = JSON.parse(readFileSync(0, 'utf8'));
const defs = {};
const out = {};
for (const it of items) {
  const f = font(it.weight ?? 500);
  const scale = it.size / f.unitsPerEm;
  const tracking = it.tracking ?? 0;
  let x = 0, uses = '';
  const glyphs = f.stringToGlyphs(it.text);
  glyphs.forEach((g, i) => {
    const gid = `g${it.weight ?? 500}-${String(it.size).replace('.', '_')}-${g.index}`;
    if (!(gid in defs)) defs[gid] = g.getPath(0, 0, it.size).toPathData(1);
    if (defs[gid]) uses += `<use xlink:href="#${gid}" href="#${gid}" x="${x.toFixed(1)}"/>`;
    x += g.advanceWidth * scale + tracking;
    if (i < glyphs.length - 1) x += f.getKerningValue(g, glyphs[i + 1]) * scale;
  });
  out[it.id] = { uses, width: x - tracking };
}
const defsSvg = Object.entries(defs).filter(([, d]) => d).map(([id, d]) => `<path id="${id}" d="${d}"/>`).join('');
process.stdout.write(JSON.stringify({ items: out, defs: defsSvg }));
