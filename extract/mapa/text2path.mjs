// Convierte rótulos a trazados SVG con EB Garamond (fontsource, woff) mediante opentype.js.
// Uso: node text2path.mjs <dir node_modules con opentype.js> < entrada.json > salida.json
//   entrada: [{id, text, size, weight, tracking}]   salida: {id: {d, width}}
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
const require = createRequire(process.argv[2].replace(/\/?$/, '/'));
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
const out = {};
for (const it of items) {
  const f = font(it.weight ?? 500);
  const scale = it.size / f.unitsPerEm;
  const tracking = it.tracking ?? 0;
  let x = 0, d = '';
  const glyphs = f.stringToGlyphs(it.text);
  glyphs.forEach((g, i) => {
    d += g.getPath(x, 0, it.size).toPathData(2);
    x += g.advanceWidth * scale + tracking;
    if (i < glyphs.length - 1) x += f.getKerningValue(g, glyphs[i + 1]) * scale;
  });
  out[it.id] = { d, width: x - tracking };
}
process.stdout.write(JSON.stringify(out));
