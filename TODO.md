# TODO — Masos de Morella

Lista de tareas pendientes. Cada una tiene un identificador (`T-nn`) para citarlo en commits, notas o conversaciones
("resuelve T-09"). Al cerrar una tarea: marcarla `[x]`, anotar fecha, y moverla a la sección "Resueltas".

Prioridad: **A** = bloquea la publicación · **B** = mejora clara · **C** = opcional.

Estado (2026-09-02): el libro completo está publicado en https://jtpadilla.github.io/masosdemorella/ con sus 30 fotografías,
tres ilustraciones añadidas por esta edición y licencias definidas. Ninguna tarea abierta bloquea nada.

## Pendientes

### Depende de la familia

- [ ] **T-07 (B) Lectura del texto por la familia / un hablante nativo y decisión sobre las erratas.**
  El criterio actual es reproducir el original tal cual (erratas incluidas; lista en `NOTES.md` → "Errores del original
  que se conservan"). Si se decide corregir alguna, hacerlo en `extract/to_markdown.py` con una tabla de sustituciones
  documentada, nunca a mano en `content/`, y anotarlo en `NOTES.md` y en `site/src/pages/edicio.astro`.

- [ ] **T-17 (C) Confirmar con la familia los puntos dudosos de los mapas.**
  En el croquis del Mas de Julian (`extract/mapa/mapa_julian.py`): la posición de la bassa (marcada como aproximada) y
  el lugar exacto de cada toma; el edificio anexo del SE (¿pallissa, corral?), rotulado neutro como "edifici annex".
  En el mapa de la dena (`mapa_llivis.py`): la Font del Garró no aparece en ninguna fuente de datos; los collados de
  Llambroix y la Corralisa tampoco; "Mas de Solarreta" se ha situado en "la Solaneta" del Nomenclàtor. Todo se corrige
  en las tablas de los scripts y se regenera con `python3 extract/mapa/<script>.py <node_modules con opentype.js>`.

### Sitio y herramientas

- [ ] **T-18 (B) Hacer reproducible la generación de mapas sin pasos manuales.**
  Los generadores de `extract/mapa/` necesitan `opentype.js`, que hoy se instala a mano en un directorio temporal y se
  pasa como argumento. Añadirlo como dependencia de desarrollo de `site/` (`npm i -D opentype.js@1`) y que
  `text2path.mjs` lo resuelva desde `site/node_modules` por defecto; documentarlo en `CLAUDE.md` y en el docstring de
  `mapalib.py`. Opcional: un `make mapes` o script npm que regenere los cuatro SVG.

- [ ] **T-08 (C) Migrar la búsqueda a la "Component UI" de Pagefind.**
  Pagefind ≥ 1.5 avisa en cada build de que la Default UI (`pagefind-ui.js`) está soportada pero superada.
  Fichero: `site/src/pages/cerca.astro`; documentación: https://pagefind.app/docs/search-ui/.

- [ ] **T-09 (C) Bajar el peso del índice de ilustraciones en la búsqueda.**
  La página `/index-d-illustracions/` sale la primera para muchas palabras porque es una lista de nombres.
  Añadir `data-pagefind-weight="0.3"` (o excluirla con `data-pagefind-ignore`) en `site/src/pages/[slug].astro`
  cuando `slugOf(c) === 'index-d-illustracions'`.

- [ ] **T-10 (C) Metadatos sociales y sitemap.**
  `og:title`, `og:description`, `og:image` (portada) en `site/src/layouts/Base.astro`; `@astrojs/sitemap` en
  `astro.config.mjs`. La URL del sitio ya es definitiva (https://jtpadilla.github.io/masosdemorella/).

- [ ] **T-11 (C) Generar EPUB y PDF a partir del Markdown.**
  Los masters en `content/` permiten regenerar el libro: p. ej. `pandoc content/*.md -o llibre.epub` filtrando las
  anclas de página y las figuras editoriales (o incluyéndolas, ya con licencia definida: CC BY-NC-ND 4.0). Publicarlos
  junto al PDF original en `dist/original/` (ver script `build` en `site/package.json`).

- [ ] **T-12 (C) Repasar el sitio en móvil real y con lector de pantalla.**
  Conocido: el botón de tema salta de línea en pantallas estrechas (`.capcalera nav` en `global.css`). Las capturas de
  comprobación se han hecho solo con Chrome headless (`google-chrome --headless=new --screenshot`).

- [ ] **T-13 (C) Mantenimiento.**
  Revisar `npm outdated` en `site/` de vez en cuando; `npm run build` y `python3 extract/check.py` son la prueba de
  regresión. Astro emite varias copias del mismo SVG para el `srcset` de las figuras editoriales (unos 2 MB en `dist/`
  por mapa); si molesta, excluir los SVG del procesado responsive en `rehype-book.mjs`. Las acciones del workflow ya
  están en sus versiones actuales (checkout v7, setup-node v7, upload-pages-artifact v5, deploy-pages v5).

## Resueltas

- [x] **T-05** Las cuatro fotografías perdidas (Dalla, Carrejador, Trill, Garbells) aportadas por la familia e
  incorporadas como figuras 10, 12, 14 y 15; dalla y carrejador enderezadas (2026-09-02).
- [x] **T-04** Licencias: texto y fotos CC BY-NC-ND 4.0 (`LICENSE-CONTINGUT.md`), código MIT (`LICENSE`);
  mención en el pie del sitio y en "Sobre esta edició"; README (2026-09-02).
- [x] **T-03** Enlace al repositorio en el pie y en "Sobre esta edició" (2026-09-02).
- [x] **T-01 / T-02** Repositorio `jtpadilla/masosdemorella` (público) y GitHub Pages activado con origen
  "GitHub Actions"; sitio publicado en https://jtpadilla.github.io/masosdemorella/ (2026-09-02).
- [x] **T-16** Croquis del Mas de Julian con las siete fotografías del mas y el punto/dirección de cada toma,
  insertado en 5.1 (`extract/mapa/mapa_julian.py`, 2026-09-02).
- [x] **T-15** Mapa de la Dena dels Llivis (`extract/mapa/mapa_llivis.py` → `assets/images/ed-mapa-dena-llivis.svg`),
  insertado en 1.1 tras la lista de masos, en la galería y en "Sobre esta edició" (2026-09-02).
- [x] **T-14** Mapa de las denes incorporado: en el capítulo 1 tras la lista de las doce denes, como figura editorial
  marcada "Il·lustració d'esta edició" (tabla `INSERTS` de `to_markdown.py`), y además en la galería y en "Sobre esta
  edició" (2026-09-02).
- [x] **T-06** Mapa dels Ports redibujado en SVG a partir de límites municipales reales (OSM), mismo contenido y
  rótulos que el original, estilo del libro. Generador: `extract/mapa/mapa_ports.py`. Ver `NOTES.md` (2026-09-02).
- [x] **T-00** Extracción del PDF, reconstrucción a Markdown, verificación palabra a palabra, sitio Astro, revisión
  visual página a página — commits `4f51945`, `21db73f`, `caccb90`, `e121a90` (2026-09-02).
