# Masos de Morella — recuperación digital

## Qué es este proyecto

Recuperar y publicar online el libro de Francisca Julián i Querol, impreso como **"Masies de Morella. Vida i costums en
la Dena dels Llivis"** (Publicacions de la Universitat Jaume I, 2006; edición única y pequeña, sin ejemplares localizables)
y revisado por la autora en 2016 como **"Masos de Morella"** (PDF). **El sitio reproduce la revisión de 2016**
(`source/Masos_de_Morella_val1_17x23.pdf`, validada contra el `.doc` de la autora); decisión T-19 (a), ver NOTES.md.
La edición impresa solo existe como escaneo sin capa de texto (`source/Masos de Morella_Copia impressio.pdf`); su
texto no se recupera (T-22 descartada). `source/` guarda además el máster Word de 2016, el PDF de 2006 tal como se envió
a la editorial (antes de su revisión) y las fotografías originales de la familia (`source/Fotos/`); inventario en NOTES.md.

Objetivo doble:
1. **Reconstruir los masters** (texto + imágenes) en formatos abiertos y longevos (Markdown + JPEG originales),
   versionados en git. Esto es lo importante: el sitio web es solo una vista de esos masters.
2. **Publicar el libro en GitHub Pages** como sitio estático legible, buscable y navegable por capítulos.

Idioma del libro: valenciano/catalán. Idioma de trabajo con el usuario: castellano.
No se modifica el contenido del libro: la reconstrucción es fiel al PDF (errores y todo, salvo que se decida
lo contrario explícitamente y se documente en `NOTES.md`).

## Diagnóstico del PDF (hecho 2026-09-02, no repetir)

- Generado con **LibreOffice Writer 4.2** el 17/05/2016. **No es un escaneo**: tiene capa de texto nativa,
  fuentes embebidas (Liberation Serif, FreeSans, Calligraphic421BT en títulos). `pdftotext` extrae el texto
  limpio con acentos, `l·l`, diéresis, etc. **No hace falta OCR.**
- 105 páginas físicas, tamaño A4, pero el bloque de texto es el de 17×23 cm, alineado arriba y con márgenes
  espejo (recto/verso). Numeración impresa: págs. físicas 3-4 = i-ii; **págs. físicas 6-105 = impresas 1-100**
  (offset = 5). Páginas 1-2 y 5 sin número (portada, blanco, portadilla).
- **El índice general y el índice de ilustraciones NO cuadran con esta paginación** (el índice dice que
  "Conclusions" está en la 101 e "Índex d'il·lustracions" en la 105; en el PDF están en la 96 y 99). Los índices
  reflejan otra maquetación, que tampoco es la impresa de 2006 (~150 págs., "Conclusions" en la 148). Se usa la
  paginación del PDF como referencia y se documenta la discrepancia.
- Título inconsistente en el propio original: portada **"MASOS de Morella"**, cabecera de página
  **"Masies de Morella"**. Se respeta tal cual.
- **Imágenes**: 27 imágenes raster JPEG, 26 únicas (la de portada, "Mas de Julian", se repite en pág. física 48).
  Calidad muy buena: la mayoría ~2350×1570 px a ~600 ppi efectivos. Se extraen sin recomprimir con
  `pdfimages -all`. Excepción: **"Mapa dels Ports"** (pág. física 8) es de solo 394×330 px — baja calidad;
  sustituido por el SVG redibujado `01-mapa-dels-ports.svg` (T-06).
- **4 ilustraciones perdidas en el PDF**: el índice lista 30, pero las figuras **"Dalla"** (pág. física 28),
  **"Carrejador"** (pág. 31), **"Trill"** (pág. 32) y **"Garbells"** (pág. 33) solo tienen el pie y un enlace de imagen roto
  (cuadradito vacío). **Ya recuperadas**: la familia aportó los originales (T-05) y están en `assets/images/`
  (10, 12, 14, 15); las 30 ilustraciones del índice están completas.
- Hay notas al pie, cursivas (términos locales), listas, citas y un poema/canciones al final. Ninguna tabla.

## Tecnología elegida

**Astro** (sitio estático) + contenido en **Markdown** + búsqueda **Pagefind** + despliegue con
**GitHub Actions → GitHub Pages**.

Por qué:
- Los masters recuperados quedan en Markdown/JPEG planos, independientes del generador: si Astro desaparece,
  el libro sigue ahí. Es la prioridad del proyecto (preservación).
- Astro genera HTML puro sin JS por defecto → rápido, indexable, accesible, imprimible; control total de
  tipografía de libro (figuras con pie, notas al pie, anclas de página original).
- `astro:assets` genera derivados responsive (webp/avif) a partir de los JPEG originales sin tocarlos.
- Pagefind da búsqueda de texto completo 100 % estática y maneja bien los diacríticos del catalán.
- Alternativa descartada: publicar el PDF con un visor (no reflow en móvil, no buscable, no recupera masters).
  Alternativa secundaria válida si se quiere menos mantenimiento: **mdBook** (binario único, menos control visual).

## Estructura del repositorio

```
source/                 originales (intocables): PDF de 2016, .doc, PDF de 2006, escaneo de la edición impresa, Fotos/, fuente TTF
extract/                salida de extract/extract.sh: text/pNNN.txt, text/book.xml (fuentes), images/, render/ (ignorado en git)
content/                MASTERS RECUPERADOS: un .md por capítulo, frontmatter con título/número
assets/images/          las 30 fotos del índice de ilustraciones, NN-figura.jpg (NN = orden en el índice), a partir de los originales de source/Fotos/;
                        SVG generados: 01-mapa-dels-ports.svg (sustituye al JPEG de baja calidad), ed-*.svg (ilustraciones de esta edición)
extract/mapa/           generadores SVG (mapalib.py, mapa_ports/denes/llivis/julian/relleu.py, roda_any.py, text2path.mjs) y datos filtrados;
                        `extract/mapa/genera.sh [--png]` (o `npm run mapes` en site/) regenera los seis; opentype.js viene con `npm install` en site/
site/                   proyecto Astro 7 (lee content/ y assets/); .github/workflows/deploy.yml lo publica
NOTES.md                decisiones editoriales, lagunas, discrepancias detectadas
TODO.md                 tareas pendientes numeradas (T-nn)
LICENSE / LICENSE-CONTINGUT.md  MIT para el código; CC BY-NC-ND 4.0 para texto (© Francisca Julián Querol) y fotos (© Tadeo Julián Querol y archivo familiar)
```

## Estado y flujo de trabajo

**Hecho** (commit inicial + reconstrucción, 2026-09-02):
1. `extract/extract.sh` — extracción reproducible desde el PDF (poppler: `pdftotext`, `pdftohtml -xml`, `pdfimages`,
   `pdftoppm`). No hay tesseract ni qpdf en la máquina; no hacen falta.
2. `extract/to_markdown.py` — genera `content/*.md` (12 ficheros: pròleg, 8 capítulos, conclusions, bibliografia,
   índex d'il·lustracions) a partir de `extract/text/book.xml`. Las reglas están documentadas en su docstring y las
   decisiones editoriales en `NOTES.md`. Es idempotente: borra y regenera `content/*.md`. **Las correcciones se hacen
   en el script, no a mano en content/**, para que sigan siendo reproducibles.
3. `extract/check.py` — verificación palabra a palabra PDF ↔ Markdown (recuento y orden). Debe seguir limpio tras
   cualquier cambio en el script.

4. `site/` — sitio Astro 7 (**hecho**, 2026-09-02). `npm run build` = astro build + copia de los PDF de `source/` a `dist/original/` +
   índice Pagefind. `npm run dev` para desarrollo (la búsqueda solo funciona en el build). Piezas:
   - `astro.config.mjs`: procesador Markdown `unified()` de `@astrojs/markdown-remark` (Astro 7 usa otro por defecto),
     smartypants desactivado (no tocar la tipografía del original), `site`/`base` derivados de `GITHUB_REPOSITORY`;
     integración `@astrojs/sitemap`.
   - `src/content.config.ts`: colección `llibre` (glob sobre `../content/*.md`) y `meta` (file sobre `../content/llibre.yaml`,
     que por eso tiene la clave superior `llibre:`). Vite tiene `fs.allow: ['..']` porque content/ y assets/ están fuera.
   - `src/lib/rehype-book.mjs`: `<p><img></p>` → `<figure class="figura">` + figcaption, ancho máx. 1200 px; los SVG
     (`ed-*`) llevan su ancho real, sin srcset, y enlace a `/imatges/<fichero>` (endpoint `src/pages/imatges/[file].ts`)
     para abrirlos a tamaño completo; recibe `{ base }` desde `astro.config.mjs`.
     Las anclas de página llegan ya formadas desde el Markdown (HTML en bruto, rehype no las ve).
   - `src/lib/llibre.ts`: helpers (`href()` respeta `base`, `slugOf`, `figures()` extrae las figuras del propio Markdown).
   - Páginas: `/` portada+índice, `/[slug]/` capítulo con anterior/siguiente, `/il-lustracions/`, `/cerca/`, `/edicio/`, `/autora/`,
     `robots.txt` (endpoint). `Base.astro` emite canonical, Open Graph (portada 1200×630) y JSON-LD schema.org/Book.
   - Estilo en `src/styles/global.css`: EB Garamond (fontsource, autoalojada), claro/oscuro con botón, números de
     página al margen (`a.pag::after`), impresión. UI del sitio en valenciano, como el libro.
5. `.github/workflows/deploy.yml` publica en GitHub Pages en cada push a `main` (**hecho**). Repositorio público
   `jtpadilla/masosdemorella`; sitio en https://jtpadilla.github.io/masosdemorella/ (Pages con origen GitHub Actions).

6. Revisión visual página a página contra `extract/render/` (**hecha**, 2026-09-02; hallazgos en NOTES.md).
   `extract/segment.py N [N…]` imprime el Markdown de una página impresa para cotejarlo con `render/p-0NN.png` (NN = N+5).

**Pendiente**: ver `TODO.md` (tareas numeradas `T-nn`; citarlas en commits y notas al resolverlas).

Capturas de comprobación: `google-chrome --headless=new --screenshot=x.png --window-size=1280,3000 URL` contra `npx astro preview`.

Formato de `content/*.md`: frontmatter `title`, `order`, `pages: [primera, última]` (paginación del PDF);
anclas `<a id="pNN"></a>` en línea; figuras `![pie](../assets/images/NN-x.jpg)`; notas `[^n]` al final del fichero;
saltos de línea duros con `\` al final de línea; rayas de diálogo escapadas `\-`.

## Convenciones

- Commits y ficheros en castellano; contenido del libro en el valenciano original, sin normalizar ortografía.
- Nombres de imágenes: `NN-descripcion-corta.jpg` donde NN es el orden en el índice de ilustraciones.
- No se sube nada derivado (webp, dist/) al repo: se genera en CI.
- Todo hallazgo sobre el original (erratas, lagunas, discrepancias) va a `NOTES.md`, no se silencia.
