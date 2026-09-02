# TODO — Masos de Morella

Lista de tareas pendientes. Cada una tiene un identificador (`T-nn`) para citarlo en commits, notas o conversaciones
("resuelve T-03"). Al cerrar una tarea: marcarla `[x]`, anotar fecha y commit, y dejarla en la sección "Resueltas".

Prioridad: **A** = bloquea la publicación · **B** = mejora clara · **C** = opcional.

## Pendientes

### Publicación

- [ ] **T-01 (A) Crear el repositorio en GitHub y hacer el primer push.**
  El repositorio local está en `main`. Nombre sugerido: `masosdemorella`. La configuración de Astro deduce la URL
  del sitio de `GITHUB_REPOSITORY`, así que no hay que tocar nada si es `<usuario>/masosdemorella`
  (→ `https://<usuario>.github.io/masosdemorella/`). Si fuera `<usuario>.github.io`, se publica en la raíz.
  Ficheros: `site/astro.config.mjs` (`site`, `base`).

- [ ] **T-02 (A) Activar GitHub Pages con origen "GitHub Actions".**
  En el repositorio: Settings → Pages → Build and deployment → Source: *GitHub Actions*. El workflow
  `.github/workflows/deploy.yml` se dispara en cada push a `main`; comprobar en la pestaña Actions que el primer
  build termina en verde (instala con `npm ci`, construye y ejecuta Pagefind). Depende de T-01.

- [ ] **T-03 (B) Enlazar el repositorio desde el sitio.**
  Añadir la URL del repositorio en `site/src/pages/edicio.astro` (párrafo "Com s'ha fet": "documentats al
  repositori del projecte") y en el pie de `site/src/layouts/Base.astro`. Depende de T-01.

- [ ] **T-04 (B) Decidir la licencia y la mención de derechos.**
  El texto y las fotos son de Francisca Julián i Querol (2016). Hace falta decidir, con la familia, bajo qué
  condiciones se publica (p. ej. CC BY-NC-ND para texto e imágenes; el código del sitio puede ir con MIT) y
  reflejarlo en `LICENSE`, en el pie del sitio (`Base.astro`) y en la página "Sobre esta edició" (`edicio.astro`).

### Material que solo puede aportar la familia

- [ ] **T-05 (B) Recuperar las cuatro fotografías perdidas: Dalla, Carrejador, Trill, Garbells.**
  Faltaban ya dentro del PDF (solo quedaba el pie y un enlace roto). Ver `NOTES.md` → "Lagunas". Si aparecen:
  1. guardar el JPEG en `assets/images/` como `10-dalla.jpg`, `12-carrejador.jpg`, `14-trill.jpg`, `15-garbells.jpg`;
  2. en `extract/to_markdown.py`, tabla `FIGURES`, sustituir el `None` de esa entrada por el nombre del fichero;
  3. `python3 extract/to_markdown.py && python3 extract/check.py`;
  4. retocar el texto de `site/src/pages/edicio.astro` (apartado "Què s'ha perdut") y `NOTES.md`.
  La galería y los placeholders se actualizan solos (los genera `figures()` en `site/src/lib/llibre.ts`).

- [ ] **T-07 (C) Lectura del texto por la familia / un hablante nativo y decisión sobre las erratas.**
  El criterio actual es reproducir el original tal cual (erratas incluidas; lista en `NOTES.md` → "Errores del original
  que se conservan"). Si se decide corregir alguna, hacerlo en `extract/to_markdown.py` con una tabla de sustituciones
  documentada, nunca a mano en `content/`, y anotarlo en `NOTES.md` y en `edicio.astro`.

- [ ] **T-14 (B) Decidir dónde va el mapa de las denes (`assets/images/ed-mapa-de-les-denes.svg`).**
  Es una ilustración nueva de esta edición (el original no la tenía), así que insertarla en el texto rompe la regla
  de no añadir nada. Opciones: (a) figura editorial tras la lista de las doce denes del cap. 1, con pie que lo declare
  ("mapa elaborat per a esta edició") y estilo propio (`figure.editorial`), añadida desde `to_markdown.py`;
  (b) solo en la página "Sobre esta edició" y en la galería como apartado "Il·lustracions d'esta edició";
  (c) página nueva "Mapes". Ficheros: `extract/to_markdown.py`, `site/src/pages/edicio.astro`, `il-lustracions.astro`.

### Sitio

- [ ] **T-08 (C) Migrar la búsqueda a la "Component UI" de Pagefind.**
  Pagefind ≥ 1.5 avisa en cada build de que la Default UI (`pagefind-ui.js`) está soportada pero superada.
  Fichero: `site/src/pages/cerca.astro`; documentación: https://pagefind.app/docs/search-ui/.

- [ ] **T-09 (C) Bajar el peso del índice de ilustraciones en la búsqueda.**
  La página `/index-d-illustracions/` sale la primera para muchas palabras porque es una lista de nombres.
  Añadir `data-pagefind-weight="0.3"` (o excluirla con `data-pagefind-ignore`) en `site/src/pages/[slug].astro`
  cuando `slugOf(c) === 'index-d-illustracions'`.

- [ ] **T-10 (C) Metadatos sociales y sitemap.**
  `og:title`, `og:description`, `og:image` (portada) en `Base.astro`; `@astrojs/sitemap` en `astro.config.mjs`.
  Requiere `site` correcto (T-01).

- [ ] **T-11 (C) Generar EPUB y PDF a partir del Markdown.**
  Los masters en `content/` permiten regenerar el libro: p. ej. `pandoc content/*.md -o llibre.epub` con las
  anclas de página filtradas. Publicarlos junto al PDF original en `dist/original/` (ver script `build` en
  `site/package.json`). Decidir antes T-04.

- [ ] **T-12 (C) Repasar el sitio en móvil real y con lector de pantalla.**
  Conocido: el botón de tema salta de línea en pantallas estrechas (`.capcalera nav` en `global.css`); las
  capturas se hicieron con Chrome headless (`google-chrome --headless=new --screenshot`).

- [ ] **T-13 (C) Mantenimiento de dependencias.**
  Astro 7 marca como obsoletas las opciones `markdown.remarkPlugins/rehypePlugins`; el sitio ya usa
  `markdown.processor: unified(...)` de `@astrojs/markdown-remark`, que es la vía vigente. Revisar `npm outdated`
  de vez en cuando; `npm run build` y `python3 extract/check.py` son la prueba de regresión.

## Resueltas

- [x] **T-06** Mapa dels Ports redibujado en SVG a partir de límites municipales reales (OSM), mismo contenido y
  rótulos que el original, estilo del libro. Generador: `extract/mapa/mapa_ports.py`. Ver `NOTES.md` (2026-09-02).

- [x] **T-00** Extracción del PDF, reconstrucción a Markdown, verificación palabra a palabra, sitio Astro, revisión
  visual página a página — commits `4f51945`, `21db73f`, `caccb90`, `e121a90` (2026-09-02).
