#!/usr/bin/env node
/**
 * Genera el llibre en EPUB i PDF a partir dels masters (content/*.md + assets/images), T-11.
 *
 *   node scripts/llibre.mjs [dir de sortida]      (per defecte public/llibre/, que Astro copia a dist/llibre/)
 *
 * - Markdown → HTML amb la mateixa cadena que el lloc (remark-gfm, sense smartypants) i un plugin propi
 *   (figures amb peu, marques de pàgina de l'original, imatges reduïdes).
 * - EPUB 3: un XHTML per capítol, portada, pàgina de crèdits, nav amb índex i llista de pàgines de l'original
 *   (epub:type="pagebreak"), EB Garamond incrustada, imatges JPEG a 1400 px. Empaquetat ací mateix (zip amb zlib).
 * - PDF: un sol HTML a 17 × 23 cm (format del PDF de 2016) imprés amb Chrome headless (protocol DevTools):
 *   capçalera i número de pàgina als marges, marques de pàgina de l'original al marge, índex amb números de
 *   pàgina (es calculen imprimint cada part per separat) i marcadors (outline) a partir dels títols.
 * Requereix google-chrome (variable CHROME per a un altre binari). Ix a la carpeta de treball .llibre/ (ignorada).
 */
import { readFileSync, writeFileSync, mkdirSync, readdirSync, rmSync, statSync } from 'node:fs';
import { resolve, dirname, basename } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawn } from 'node:child_process';
import zlib from 'node:zlib';
import yaml from 'js-yaml';
import sharp from 'sharp';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkRehype from 'remark-rehype';
import rehypeRaw from 'rehype-raw';
import rehypeStringify from 'rehype-stringify';
import { visit } from 'unist-util-visit';
import { parseFrontmatter } from '@astrojs/markdown-remark';

const SITE = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ROOT = resolve(SITE, '..');
const OUT = resolve(SITE, process.argv[2] ?? 'public/llibre');
const TMP = resolve(SITE, '.llibre');
const IMG_SRC = resolve(ROOT, 'assets/images');
const FONTS = resolve(SITE, 'node_modules/@fontsource/eb-garamond/files');
const CHROME = process.env.CHROME ?? 'google-chrome';
const NOM = 'masos-de-morella';
const URL_LLOC = 'https://jtpadilla.github.io/masosdemorella/';
const meta = yaml.load(readFileSync(resolve(ROOT, 'content/llibre.yaml'), 'utf8')).llibre;
const ANY = new Date().getFullYear();
const AVUI = new Date().toISOString().slice(0, 10);
const AUTORA = 'Francisca Julián Querol';
const EDITOR = 'Juan Tadeo Padilla Julián';

rmSync(TMP, { recursive: true, force: true });
for (const d of ['imatges', 'fonts', 'html']) mkdirSync(resolve(TMP, d), { recursive: true });
mkdirSync(OUT, { recursive: true });

// --- capítols -----------------------------------------------------------------------------------------------------
const capitols = readdirSync(resolve(ROOT, 'content')).filter((f) => f.endsWith('.md')).sort().map((f) => {
  const { frontmatter, content } = parseFrontmatter(readFileSync(resolve(ROOT, 'content', f), 'utf8'));
  return { file: f, slug: f.replace(/^\d+-/, '').replace(/\.md$/, ''), title: frontmatter.title, order: frontmatter.order, pages: frontmatter.pages, md: content };
}).sort((a, b) => a.order - b.order);

const usades = new Set();
const pagines = [];   // [{p, slug}] marques de pàgina de l'original, en ordre

/** Plugin rehype: figures, marques de pàgina, imatges. */
function rehypeLlibre({ imgPrefix, xhtml, slug }) {
  return (tree) => {
    visit(tree, 'element', (node, index, parent) => {
      if (node.tagName === 'p' && parent) {
        const kids = node.children.filter((c) => !(c.type === 'text' && !c.value.trim()));
        if (kids.length === 1 && kids[0].tagName === 'img') {
          const img = kids[0];
          const file = String(img.properties.src).split('/').pop();
          const editorial = /^ed-/.test(file);
          usades.add(file);
          img.properties.src = imgPrefix + file;
          const caption = [{ type: 'text', value: img.properties.alt ?? '' }];
          if (editorial) caption.unshift({ type: 'element', tagName: 'span', properties: { className: ['ed'] }, children: [{ type: 'text', value: 'Il·lustració d’esta edició · ' }] });
          parent.children[index] = {
            type: 'element', tagName: 'figure', properties: { className: editorial ? ['figura', 'editorial', ...(/^ed-roda/.test(file) ? ['ampla'] : [])] : ['figura'] },
            children: [img, { type: 'element', tagName: 'figcaption', properties: {}, children: caption }],
          };
        }
      }
      if (node.tagName === 'a' && (node.properties.className ?? []).includes('pag')) {
        const p = String(node.properties.dataP ?? node.properties['data-p'] ?? '');
        pagines.push({ p, slug });
        node.tagName = 'span';
        node.properties = { id: `p${p}`, className: ['pag'], 'data-p': p };
        if (xhtml) Object.assign(node.properties, { 'epub:type': 'pagebreak', role: 'doc-pagebreak', 'aria-label': p });
      }
    });
  };
}

async function render(c, { imgPrefix, xhtml }) {
  const out = await unified()
    .use(remarkParse).use(remarkGfm)
    .use(remarkRehype, {
      allowDangerousHtml: true, clobberPrefix: `${c.slug}-`, footnoteLabel: 'Notes', footnoteLabelTagName: 'h2',
      footnoteLabelProperties: { className: ['notes-titol'] }, footnoteBackLabel: 'Torna al text',
    })
    .use(rehypeRaw)
    .use(rehypeLlibre, { imgPrefix, xhtml, slug: c.slug })
    .use(rehypeStringify, { closeSelfClosing: xhtml })
    .process(c.md);
  return String(out);
}

// --- imatges (reduïdes) i fonts --------------------------------------------------------------------------------------
async function preparaImatges() {
  for (const f of readdirSync(IMG_SRC)) {
    const src = resolve(IMG_SRC, f), dst = resolve(TMP, 'imatges', f);
    if (/\.jpe?g$/i.test(f)) await sharp(src).rotate().resize({ width: 1400, withoutEnlargement: true }).jpeg({ quality: 82, mozjpeg: true }).toFile(dst);
    else if (/\.svg$/i.test(f)) writeFileSync(dst, readFileSync(src));
  }
}
const FONT_FILES = { 400: 'eb-garamond-latin-400-normal.woff2', '400i': 'eb-garamond-latin-400-italic.woff2', 500: 'eb-garamond-latin-500-normal.woff2', 600: 'eb-garamond-latin-600-normal.woff2', '600i': 'eb-garamond-latin-600-italic.woff2' };
function fontFaces(urlOf) {
  return Object.entries(FONT_FILES).map(([k, f]) => `@font-face { font-family: "EB Garamond"; font-weight: ${parseInt(k)}; font-style: ${k.endsWith('i') ? 'italic' : 'normal'}; src: url("${urlOf(f)}") format("woff2"); }`).join('\n');
}

// --- text comú (portada, crèdits) ---------------------------------------------------------------------------------------
const e = meta.edicio_impresa;
const portadaHtml = (img) => `
<section class="portada" id="portada">
  <img src="${img}" alt="El Mas de Julian, amb un ramat d’ovelles davant" />
  <h1 class="titol">${meta.titol}</h1>
  <p class="subtitol">${meta.subtitol}</p>
  <p class="autora">${meta.autora}</p>
</section>`;
const creditsHtml = () => `
<section class="credits" id="credits">
  <p><strong>${meta.titol}. ${meta.subtitol}</strong>, de ${meta.autora}.</p>
  <p>Edició digital de recuperació, ${ANY}. Reprodueix la revisió de 2016 de l’autora, l’última versió del llibre en què va treballar; el text es dóna tal com ella el va deixar. ${meta.context.trim()}</p>
  <p>Edició impresa: <em>${e.titol}</em>. ${e.lloc}: ${e.editorial}, ${e.any}. ISBN ${e.isbn13}. Esgotada.</p>
  <p>Text i fotografies © ${AUTORA} i arxiu familiar. Llicència Creative Commons Reconeixement-NoComercial-SenseObraDerivada 4.0 Internacional (CC BY-NC-ND 4.0).</p>
  <p>Edició digital: ${EDITOR}. Lloc web, amb cerca i galeria: <a href="${URL_LLOC}">${URL_LLOC}</a>. Els mapes i diagrames marcats «Il·lustració d’esta edició» no eren en l’original i s’han fet per a esta edició amb dades d’OpenStreetMap i altres fonts obertes.</p>
  <p class="nota">Les marques de pàgina (<span class="pag-demo">23</span>) indiquen on començava cada pàgina del PDF de 2016, per a poder-lo citar. Fitxer generat el ${AVUI}.</p>
</section>`;

// --- EPUB ---------------------------------------------------------------------------------------------------------
const xhtmlDoc = (title, body) => `<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="ca" lang="ca">
<head><meta charset="utf-8"/><title>${esc(title)}</title><link rel="stylesheet" href="style.css"/></head>
<body>${body}</body>
</html>`;
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const CSS_EPUB = `
${fontFaces((f) => `fonts/${f}`)}
body { font-family: "EB Garamond", Georgia, serif; line-height: 1.5; }
h1 { font-size: 1.6em; font-weight: 600; margin: 1.5em 0 1em; }
h2 { font-size: 1.25em; font-weight: 600; margin: 1.6em 0 0.6em; }
h3 { font-size: 1.1em; font-weight: 600; margin: 1.4em 0 0.5em; }
p { margin: 0 0 0.8em; text-align: justify; }
blockquote { margin: 1em 0 1em 1.2em; font-style: italic; }
blockquote em { font-style: normal; }
.figura { margin: 1.5em 0; text-align: center; page-break-inside: avoid; }
.figura img { max-width: 100%; max-height: 90vh; }
.figura figcaption { font-style: italic; font-size: 0.9em; margin-top: 0.4em; }
.figura .ed { font-style: normal; font-size: 0.75em; letter-spacing: 0.08em; text-transform: uppercase; }
.pag { }
.notes-titol { font-size: 1em; margin-top: 2em; }
.footnotes { font-size: 0.9em; }
.footnotes ol { padding-left: 1.4em; }
.portada { text-align: center; }
.portada img { max-width: 100%; margin: 0 0 1.5em; }
.portada .titol { font-size: 2.2em; font-weight: 600; margin: 0.3em 0 0.2em; }
.portada .subtitol { font-size: 1.3em; font-style: italic; margin: 0 0 1.5em; }
.portada .autora { font-size: 1.15em; letter-spacing: 0.08em; }
.credits { font-size: 0.9em; }
.credits .nota { font-size: 0.85em; }
.pag-demo { font-size: 0.8em; color: #777; }
.toc ol { list-style: none; padding-left: 0; }
.toc li { margin: 0.4em 0; }
`;

async function epub() {
  const files = [];   // {name, data, store}
  files.push({ name: 'mimetype', data: Buffer.from('application/epub+zip'), store: true });
  files.push({ name: 'META-INF/container.xml', data: Buffer.from(`<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>`) });
  const manifest = [], spine = [], tocs = [];
  const add = (id, href, type, data, props) => { manifest.push({ id, href, type, props }); files.push({ name: `OEBPS/${href}`, data }); };
  add('css', 'style.css', 'text/css', Buffer.from(CSS_EPUB));
  for (const [k, f] of Object.entries(FONT_FILES)) add(`font${k}`, `fonts/${f}`, 'font/woff2', readFileSync(resolve(FONTS, f)));
  // portada (imatge de coberta + pàgina)
  add('coberta', 'coberta.jpg', 'image/jpeg', readFileSync(resolve(TMP, 'coberta.jpg')), 'cover-image');
  add('portada', 'portada.xhtml', 'application/xhtml+xml', Buffer.from(xhtmlDoc(meta.titol, portadaHtml('imatges/21-mas-de-julian.jpg'))));
  spine.push('portada');
  usades.add('21-mas-de-julian.jpg');
  add('credits', 'credits.xhtml', 'application/xhtml+xml', Buffer.from(xhtmlDoc('Crèdits', creditsHtml())));
  spine.push('credits');
  pagines.length = 0;
  for (const c of capitols) {
    const body = await render(c, { imgPrefix: 'imatges/', xhtml: true });
    const id = `c${String(c.order).padStart(2, '0')}`;
    add(id, `${id}-${c.slug}.xhtml`, 'application/xhtml+xml', Buffer.from(xhtmlDoc(c.title, `<section class="capitol" id="${c.slug}">${body}</section>`)));
    spine.push(id); tocs.push({ id, href: `${id}-${c.slug}.xhtml`, title: c.title, slug: c.slug });
  }
  for (const f of [...usades].sort()) add(`img-${f.replace(/[^a-z0-9]/gi, '-')}`, `imatges/${f}`, /\.svg$/i.test(f) ? 'image/svg+xml' : 'image/jpeg', readFileSync(resolve(TMP, 'imatges', f)));
  // nav: índex, llista de pàgines de l'original, punts de referència
  const hrefOf = Object.fromEntries(tocs.map((t) => [t.slug, t.href]));
  const nav = `<nav epub:type="toc" id="toc" class="toc"><h1>Índex</h1><ol>${tocs.map((t) => `<li><a href="${t.href}">${esc(t.title)}</a></li>`).join('')}</ol></nav>
<nav epub:type="page-list" hidden="hidden"><h1>Pàgines del PDF de 2016</h1><ol>${pagines.map((x) => `<li><a href="${hrefOf[x.slug]}#p${x.p}">${x.p}</a></li>`).join('')}</ol></nav>
<nav epub:type="landmarks" hidden="hidden"><h1>Punts de referència</h1><ol><li><a epub:type="cover" href="portada.xhtml">Portada</a></li><li><a epub:type="toc" href="nav.xhtml">Índex</a></li><li><a epub:type="bodymatter" href="${tocs[0].href}">Inici del text</a></li></ol></nav>`;
  add('nav', 'nav.xhtml', 'application/xhtml+xml', Buffer.from(xhtmlDoc('Índex', nav)), 'nav');
  spine.splice(2, 0, 'nav');
  add('ncx', 'toc.ncx', 'application/x-dtbncx+xml', Buffer.from(`<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="${URL_LLOC}"/></head><docTitle><text>${esc(meta.titol)}</text></docTitle><navMap>${tocs.map((t, i) => `<navPoint id="np${i}" playOrder="${i + 1}"><navLabel><text>${esc(t.title)}</text></navLabel><content src="${t.href}"/></navPoint>`).join('')}</navMap></ncx>`));
  const opf = `<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid" xml:lang="ca" prefix="rendition: http://www.idpf.org/vocab/rendition/#">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="uid">${URL_LLOC}</dc:identifier>
<dc:title id="t">${esc(meta.titol)}. ${esc(meta.subtitol)}</dc:title>
<dc:creator id="cre">${esc(AUTORA)}</dc:creator><meta refines="#cre" property="role" scheme="marc:relators">aut</meta>
<dc:contributor id="edt">${esc(EDITOR)}</dc:contributor><meta refines="#edt" property="role" scheme="marc:relators">edt</meta>
<dc:language>ca</dc:language>
<dc:date>${AVUI}</dc:date>
<dc:publisher>Edició digital (${URL_LLOC})</dc:publisher>
<dc:rights>Text i fotografies © ${esc(AUTORA)} i arxiu familiar. CC BY-NC-ND 4.0.</dc:rights>
<dc:description>${esc(meta.edicio_impresa.sinopsi ?? `${meta.titol}. ${meta.subtitol}`)}</dc:description>
<dc:source>${esc(`${e.titol}. ${e.lloc}: ${e.editorial}, ${e.any}. ISBN ${e.isbn13}`)}</dc:source>
<meta property="dcterms:modified">${new Date().toISOString().replace(/\.\d+Z$/, 'Z')}</meta>
<meta name="cover" content="coberta"/>
</metadata>
<manifest>${manifest.map((m) => `<item id="${m.id}" href="${m.href}" media-type="${m.type}"${m.props ? ` properties="${m.props}"` : ''}/>`).join('\n')}</manifest>
<spine toc="ncx">${spine.map((s) => `<itemref idref="${s}"/>`).join('')}</spine>
</package>`;
  add('opf', 'content.opf', 'application/oebps-package+xml', Buffer.from(opf));
  files.splice(files.findIndex((f) => f.name === 'OEBPS/content.opf'), 1);   // l'OPF no va al manifest
  files.push({ name: 'OEBPS/content.opf', data: Buffer.from(opf) });
  manifest.splice(manifest.findIndex((m) => m.id === 'opf'), 1);
  const out = resolve(OUT, `${NOM}.epub`);
  writeFileSync(out, zip(files));
  return out;
}

/** Zip mínim (stored per a mimetype, deflate per a la resta). */
function zip(entries) {
  const parts = [], cd = []; let off = 0;
  for (const e of entries) {
    const crc = zlib.crc32(e.data), method = e.store ? 0 : 8;
    const comp = e.store ? e.data : zlib.deflateRawSync(e.data, { level: 9 });
    const name = Buffer.from(e.name, 'utf8');
    const lh = Buffer.alloc(30);
    lh.writeUInt32LE(0x04034b50, 0); lh.writeUInt16LE(20, 4); lh.writeUInt16LE(0x0800, 6); lh.writeUInt16LE(method, 8);
    lh.writeUInt16LE(0, 10); lh.writeUInt16LE(0x21, 12); lh.writeUInt32LE(crc, 14); lh.writeUInt32LE(comp.length, 18);
    lh.writeUInt32LE(e.data.length, 22); lh.writeUInt16LE(name.length, 26); lh.writeUInt16LE(0, 28);
    const ch = Buffer.alloc(46);
    ch.writeUInt32LE(0x02014b50, 0); ch.writeUInt16LE(20, 4); ch.writeUInt16LE(20, 6); ch.writeUInt16LE(0x0800, 8);
    ch.writeUInt16LE(method, 10); ch.writeUInt16LE(0, 12); ch.writeUInt16LE(0x21, 14); ch.writeUInt32LE(crc, 16);
    ch.writeUInt32LE(comp.length, 20); ch.writeUInt32LE(e.data.length, 24); ch.writeUInt16LE(name.length, 28);
    ch.writeUInt32LE(off, 42);
    parts.push(lh, name, comp); cd.push(ch, name);
    off += lh.length + name.length + comp.length;
  }
  const cdBuf = Buffer.concat(cd), eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0); eocd.writeUInt16LE(entries.length, 8); eocd.writeUInt16LE(entries.length, 10);
  eocd.writeUInt32LE(cdBuf.length, 12); eocd.writeUInt32LE(off, 16);
  return Buffer.concat([...parts, cdBuf, eocd]);
}

// --- Chrome (protocol DevTools) ---------------------------------------------------------------------------------------
async function ambChrome(fn) {
  const port = 9600 + Math.floor(Math.random() * 200);
  const args = ['--headless=new', `--remote-debugging-port=${port}`, '--no-first-run', '--hide-scrollbars', '--disable-gpu',
    `--user-data-dir=${resolve(TMP, 'chrome')}`, 'about:blank'];
  if (process.env.CI) args.push('--no-sandbox');
  const chrome = spawn(CHROME, args, { stdio: 'ignore' });
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  let list;
  for (let i = 0; i < 40 && !list; i++) { await sleep(250); list = await fetch(`http://127.0.0.1:${port}/json`).then((r) => r.json()).catch(() => null); }
  if (!list) throw new Error('no s’ha pogut connectar amb Chrome');
  const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
  await new Promise((r) => (ws.onopen = r));
  let id = 0; const pending = {};
  ws.onmessage = (ev) => { const m = JSON.parse(ev.data); if (m.id && pending[m.id]) { pending[m.id](m); delete pending[m.id]; } };
  const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending[i] = r; ws.send(JSON.stringify({ id: i, method, params })); })
    .then((m) => { if (m.error) throw new Error(`${method}: ${m.error.message}`); return m.result; });
  await send('Page.enable');
  const obri = async (file) => {
    await send('Page.navigate', { url: pathToFileURL(file).href });
    await send('Runtime.evaluate', { expression: 'new Promise(r => { const f = () => document.fonts.ready.then(() => setTimeout(r, 300)); document.readyState === "complete" ? f() : addEventListener("load", f); })', awaitPromise: true });
  };
  try {
    return await fn({
      pdf: async (file) => { await obri(file); const r = await send('Page.printToPDF', { preferCSSPageSize: true, printBackground: true, displayHeaderFooter: false, generateDocumentOutline: true }); return Buffer.from(r.data, 'base64'); },
      captura: async (file, width, height) => {
        await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
        await obri(file);
        const r = await send('Page.captureScreenshot', { format: 'png' }); return Buffer.from(r.data, 'base64');
      },
    });
  } finally { ws.close(); chrome.kill(); }
}
const numPagines = (pdf) => (pdf.toString('latin1').match(/\/Type\s*\/Page(?![s\w])/g) ?? []).length;

// --- PDF ---------------------------------------------------------------------------------------------------------
const CSS_PDF = `
${fontFaces((f) => `data:font/woff2;base64,${readFileSync(resolve(FONTS, f)).toString('base64')}`)}
@page { size: 170mm 230mm; margin: 20mm 20mm 22mm; @top-center { content: "${meta.titol}. ${meta.subtitol}"; font: 8.5pt "EB Garamond"; letter-spacing: 0.06em; color: #666; } @bottom-center { content: counter(page); font: 10pt "EB Garamond"; color: #444; } }
@page :left { margin-left: 10mm; margin-right: 22mm; }
@page :right { margin-left: 14mm; margin-right: 18mm; }
@page coberta { margin: 0; @top-center { content: none; } @bottom-center { content: none; } }
@page neta { @top-center { content: none; } @bottom-center { content: none; } }
@page figura { margin: 14mm 12mm 18mm; }
@page apaisada { size: 230mm 170mm; margin: 12mm 12mm 16mm; }
html { font-family: "EB Garamond", Georgia, serif; font-size: 10.5pt; line-height: 1.42; color: #1a1613; }
body { margin: 0; }
.part { break-before: page; padding-left: 10mm; }
.part.portada { padding-left: 0; }
h1 { font-size: 20pt; font-weight: 600; margin: 3em 0 1.5em; line-height: 1.2; }
h2 { font-size: 13.5pt; font-weight: 600; margin: 1.8em 0 0.6em; break-after: avoid; }
h3 { font-size: 11.5pt; font-weight: 600; margin: 1.5em 0 0.5em; break-after: avoid; }
p { margin: 0 0 0.55em; text-align: justify; hyphens: auto; -webkit-hyphens: auto; position: relative; orphans: 2; widows: 2; }
li { position: relative; }
blockquote { margin: 0.8em 0 0.8em 1.2em; font-style: italic; color: #333; }
blockquote em { font-style: normal; }
ul, ol { padding-left: 1.4em; margin: 0 0 0.6em; }
sup { font-size: 0.7em; line-height: 0; }
a { color: inherit; text-decoration: none; }
.figura { margin: 1.2em 0; text-align: center; break-inside: avoid; }
.figura img { max-width: 100%; max-height: 150mm; }
.figura.editorial { page: figura; break-before: page; break-after: page; margin: 0 0 0 -10mm; }
.figura.editorial img { max-height: 172mm; }
.figura.editorial.ampla { page: apaisada; }
.figura.editorial.ampla img { max-height: 118mm; }
.figura figcaption { font-style: italic; font-size: 9.5pt; color: #444; margin-top: 0.4em; }
.figura .ed { font-style: normal; font-size: 7pt; letter-spacing: 0.1em; text-transform: uppercase; color: #777; }
.pag { position: absolute; left: -10mm; top: 0.15em; width: 7mm; text-align: right; font-size: 7pt; color: #999; font-variant-numeric: tabular-nums; }
.pag::after { content: attr(data-p); }
.notes-titol { font-size: 9.5pt; margin-top: 2.5em; letter-spacing: 0.06em; text-transform: uppercase; color: #666; }
.footnotes { font-size: 9pt; color: #333; }
.footnotes ol { padding-left: 1.3em; }
.footnotes p { text-align: left; }
.footnotes [data-footnote-backref] { display: none; }
.portada { page: coberta; break-before: auto; height: 230mm; position: relative; overflow: hidden; text-align: center; background: #fbf8f2; }
.portada p, .portada h1 { text-align: center; }
.portada img { width: 170mm; height: 128mm; object-fit: cover; display: block; }
.portada .titol { font-size: 30pt; font-weight: 600; margin: 16mm 0 3mm; letter-spacing: 0.04em; }
.portada .subtitol { font-size: 15pt; font-style: italic; margin: 0 0 14mm; }
.portada .autora { font-size: 13pt; letter-spacing: 0.12em; }
.credits { page: neta; font-size: 9pt; color: #333; display: flex; flex-direction: column; justify-content: flex-end; min-height: 185mm; }
.credits p { text-align: left; }
.credits .nota { font-size: 8.5pt; color: #666; }
.pag-demo { font-size: 7pt; color: #999; }
.toc h1 { margin-top: 1.5em; }
.toc ol { list-style: none; padding: 0; }
.toc li { display: flex; justify-content: space-between; margin: 0.5em 0; }
.toc li .punts { flex: 1; border-bottom: 1px dotted #999; margin: 0 0.4em 0.35em; }
`;
const htmlDoc = (body) => `<!doctype html><html lang="ca"><head><meta charset="utf-8"><title>${esc(meta.titol)}. ${esc(meta.subtitol)}</title><style>${CSS_PDF}</style></head><body>${body}</body></html>`;
const tocHtml = (nums) => `<section class="part toc"><h1>Índex</h1><ol>${capitols.map((c) => `<li><span>${esc(c.title)}</span><span class="punts"></span><span>${nums ? nums[c.slug] : ''}</span></li>`).join('')}</ol></section>`;

async function pdf(chrome) {
  const parts = [{ id: 'portada', html: portadaHtml(pathToFileURL(resolve(TMP, 'imatges/21-mas-de-julian.jpg')).href) },
                 { id: 'credits', html: `<section class="part credits">${creditsHtml().replace(/<\/?section[^>]*>/g, '')}</section>` },
                 { id: 'toc', html: tocHtml(null) }];
  for (const c of capitols) parts.push({ id: c.slug, html: `<section class="part capitol" id="${c.slug}">${await render(c, { imgPrefix: pathToFileURL(resolve(TMP, 'imatges')).href + '/', xhtml: false })}</section>` });
  // 1a passada: pàgines de cada part → números de l'índex
  const nums = {}; let p = 1;
  for (const part of parts) {
    const f = resolve(TMP, 'html', `${part.id}.html`);
    writeFileSync(f, htmlDoc(part.html));
    nums[part.id] = p;
    p += numPagines(await chrome.pdf(f));
  }
  parts[2].html = tocHtml(nums);
  const f = resolve(TMP, 'html', 'llibre.html');
  writeFileSync(f, htmlDoc(parts.map((x) => x.html).join('\n')));
  const data = await chrome.pdf(f);
  const out = resolve(OUT, `${NOM}.pdf`);
  writeFileSync(out, data);
  return { out, pagines: numPagines(data) };
}

// --- coberta (imatge per a l'EPUB) ----------------------------------------------------------------------------------------
async function coberta(chrome) {
  const f = resolve(TMP, 'html', 'coberta.html');
  writeFileSync(f, `<!doctype html><html><head><meta charset="utf-8"><style>${CSS_PDF} html, body { width: 1200px; height: 1800px; margin: 0; } .portada { width: 1200px; height: 1800px; } .portada img { width: 1200px; height: 1000px; } .portada .titol { font-size: 96px; margin: 120px 0 20px; } .portada .subtitol { font-size: 46px; margin-bottom: 110px; } .portada .autora { font-size: 40px; }</style></head><body>${portadaHtml(pathToFileURL(resolve(TMP, 'imatges/21-mas-de-julian.jpg')).href)}</body></html>`);
  const png = await chrome.captura(f, 1200, 1800);
  await sharp(png).jpeg({ quality: 85 }).toFile(resolve(TMP, 'coberta.jpg'));
}

// --- main ------------------------------------------------------------------------------------------------------------
await preparaImatges();
const res = await ambChrome(async (chrome) => {
  await coberta(chrome);
  return pdf(chrome);
});
const ep = await epub();
const kb = (f) => Math.round(statSync(f).size / 1024);
console.log(`${basename(res.out)}: ${res.pagines} pàgines, ${kb(res.out)} KB · ${basename(ep)}: ${kb(ep)} KB → ${OUT}`);
