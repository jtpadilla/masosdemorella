# TODO — Masos de Morella

Lista de tareas pendientes. Cada una tiene un identificador (`T-nn`) para citarlo en commits, notas o conversaciones
("resuelve T-09"). Al cerrar una tarea: marcarla `[x]`, anotar fecha, y moverla a la sección "Resueltas".

Prioridad: **A** = bloquea la publicación · **B** = mejora clara · **C** = opcional.

Estado (2026-09-03): el libro completo está publicado en https://jtpadilla.github.io/masosdemorella/ con sus 30 fotografías
(ya a partir de los originales), el mapa dels Ports redibujado, tres ilustraciones añadidas por esta edición y licencias
definidas. El sitio reproduce la revisión de 2016 de la autora (decisión T-19 (a)); la edición impresa de 2006 queda
documentada, sin recuperar su texto (T-22 descartada). No queda ninguna tarea de prioridad A ni B que no dependa de la familia.

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
  en las tablas de los scripts y se regenera con `extract/mapa/genera.sh`.

### Recursos gráficos complementarios (propuesta del 2026-09-03)

Ilustraciones nuevas derivadas solo del texto del libro, sin tocarlo; entran como las tres existentes (figura
`ed-*.svg` marcada "Il·lustració d'esta edició", tabla `INSERTS` de `to_markdown.py`, generador en `extract/mapa/`).
Orden recomendado: T-24, T-25 (T-23 hecha).

- [ ] **T-24 (B) Árbol genealógico de la familia Julian** (8.2).
  Tres generaciones: Ramon Julian + Felipa Segura (Mas de Clara); hijos Antoni (hereu), Ramon (†Cuba), Josep (avi) + Manuela
  (mas de Sabater), Maria (casa de Morella), Benardo (maset de Conill); hijos de Josep: Francisco, Ramon, Tadeo + Encarna
  de Francho, Fidel, Juliana, Rosario (La Màquina), Josefina; la autora y sus dos hermanos; enlaces con Guardiola y Adell.
  Validar con la familia antes de publicar.

- [ ] **T-25 (B) Cronología de la dena y de Morella** (cap. 2 o transversal).
  Línea de tiempo con dos carriles (historia general / Dena dels Llivis) a partir de los ~30 hitos fechados del libro:
  218 a.C., 18 a.C., 476, 1084, 1232-33, 1256, 1270, 1345, 1360, <1370, 1412-14, 1460, Germanies, 1594, 1640, 1670, 1673,
  1691, 1705, 1741, 1786, 1809, 1833, 1882, 1895 (174 hab.), 1938, 1944, 1947-48, 1956-1974, 1980, 1986 (26 hab.).

- [ ] **T-26 (C) Mapa de ermitas, peirons y rogativas por denas** (7.1-7.2).
  Sobre `ed-mapa-de-les-denes.svg`: Sant Marc (Castellons, 25 abr), Sant Pere dels Llivis (29 abr), la Llàcua (1 may),
  Santa Creu del riu de les Corses (3 may), Sant Isidre d'Herbeset y peiró de Sant Isidre (15 may), Sant Antoni de la Vespa
  (13 jun), Sant Pere del Moll (24 jun), Sant Cristòfol (10 jul), Vallivana; rogativas desaparecidas como flechas a Bordó,
  Castellfort y la Mare de Déu de la Font. Topónimos en el Nomenclàtor y OSM.

- [ ] **T-27 (C) Ruta a pie de Cinctorres al Mas de Julian** (8.2).
  Carretera hacia Morella (2,5 km), desvío en Caldes, mas de La Màquina, cruce del río junto al Molí Vicent (dena de la
  Vespa), subida por la umbría de la Torre Massa hasta la Serra Calduch. Trazado a confirmar con la familia (junto a T-17).

- [ ] **T-28 (C) Relieve e hidrografía del término de Morella** (cap. 1).
  Siete cumbres con altitud (Carrascals 1263, Pinar 1081, Regafolet 1259, Morella la Vella 1068, Muixacre 1274, Fusters 1294,
  Nevera 1286), ríos Bergants y Cérvol, puerto de Torremiró y municipios limítrofes por puntos cardinales. Mismas fuentes
  que `mapa_ports.py`.

- [ ] **T-29 (C) Nombres del ganado por edad** (4.1).
  Línea: cabrit/corder → xoto/xota → primal/primala (1 año) → andosc/andosca → terserenc/terserenca (4.º año) → "ha tancat"
  (5.º) → "entra a vell"; boc y borrego aparte.

- [ ] **T-30 (C) Del campo al granero: diagrama de flujo del cereal** (3.6-3.9).
  Siembra → siega (falç, dalla) → garbes → carrejador → era → trill → forca y pala → garbell → barcella → granero / pallissa,
  enlazando las fotos de aperos.

- [ ] **T-31 (C) Planta esquemática de un mas** (5.1). Con reservas: sería una generalización a partir del texto
  (orientación, corrales adosados, entrada y escalera, cocina con recuina y pastador, secador al NE). Mejor si la familia
  dibuja la planta real del Mas de Julian.

- [ ] **T-32 (C) Escenario del crimen de 1882** (8.1). Con reservas: ruta del recaudador desde Castellfort y Portell, Mas
  del Racó, "los cuatro caminos"; el punto exacto no se conoce, marcar como aproximado.

- [ ] **T-33 (C) Dibujos técnicos**: secciones del forn de calç (5.11) y de la carbonera (5.12), arreos de la caballería
  (3.4). Descripciones suficientes, pero exigen dibujo y son las que más fácilmente contradicen un detalle del original.

No se proponen gráficos de datos: las únicas cifras seriadas (174 hab. en 1895, 26 en 1986; 21 masías, 6 habitadas)
caben en la cronología.

### Sitio y herramientas

- [ ] **T-11 (C) Generar EPUB y PDF a partir del Markdown.**
  Los masters en `content/` permiten regenerar el libro: p. ej. `pandoc content/*.md -o llibre.epub` filtrando las
  anclas de página y las figuras editoriales (o incluyéndolas, ya con licencia definida: CC BY-NC-ND 4.0). Publicarlos
  junto al PDF original en `dist/original/` (ver script `build` en `site/package.json`).

- [ ] **T-12 (C) Repasar el sitio en móvil real y con lector de pantalla.**
  Conocido: el botón de tema salta de línea en pantallas estrechas (`.capcalera nav` en `global.css`). Las capturas de
  comprobación se han hecho solo con Chrome headless (`google-chrome --headless=new --screenshot`).

## Resueltas

- [x] **T-23** Rueda del año al mas: `extract/mapa/roda_any.py` → `assets/images/ed-roda-de-l-any.svg`, insertada al final
  del capítulo 6 (tras "una altra vegada a començar"), en la galería y en "Sobre esta edició". Cada entrada de la tabla
  `MESOS` lleva el apartado del libro del que sale (2026-09-03).

- [x] **T-13** Mantenimiento (2026-09-03): `npm outdated` solo señala `opentype.js` 2.0 (**no actualizar**: cambia la
  serialización de los trazados y los cuatro SVG dejan de ser reproducibles; se queda en 1.3.4). `check.py` limpio
  (ver NOTES). Acciones del workflow en su última mayor. Los SVG ya no generan `srcset` (`layout: 'none'` en
  `rehype-book.mjs`, galería y "Sobre esta edició"): de 36 copias / ~10 MB a 15 / 3,5 MB en `dist/`. Rutina: `npm run
  build` + `python3 extract/check.py` antes de cualquier cambio de dependencias.

- [x] **T-10** Open Graph / Twitter card en `Base.astro` (título, descripción, URL canónica, portada recortada a 1200×630
  con `getImage`), `image` en el JSON-LD, `@astrojs/sitemap` en `astro.config.mjs` (`sitemap-index.xml`) y
  `robots.txt` generado con la URL del sitemap (`src/pages/robots.txt.ts`) (2026-09-03).

- [x] **T-09** El índice de ilustraciones lleva `data-pagefind-weight="0.3"` (`[slug].astro`): para "trill", "mas" o
  "era" pasa de las primeras posiciones a la última; sigue apareciendo cuando es pertinente ("foto") (2026-09-03).

- [x] **T-08** Búsqueda migrada a la Component UI de Pagefind (`pagefind-component-ui.js`, elementos `<pagefind-input>`,
  `<pagefind-summary>`, `<pagefind-results>`); traducciones en valenciano vía `setTranslations`, tema claro/oscuro con las
  variables `--pf-*` ligadas a las del sitio, y `/cerca/?q=paraula` lanza la búsqueda (2026-09-03).

- [x] **T-21** Cerrada: el mapa manuscrito `source/Fotos/Mapa_Dena.jpg` no se publica; lo sustituye el mapa de la dena
  generado por esta edición (`assets/images/ed-mapa-dena-llivis.svg`, `extract/mapa/mapa_llivis.py`) (2026-09-03).

- [x] **T-22** Descartada: no se recupera el texto de la edición impresa de 2006; queda documentada en NOTES.md y en
  "Sobre esta edició" (2026-09-03).

- [x] **T-20** Cerrada: el sitio ofrece el PDF de 2016 (15 MB); el escaneo de 2006 y el PDF a resolución completa no se
  publican enlazados (2026-09-03).

- [x] **T-19** Opción (a): el sitio reproduce la revisión de 2016; "Sobre esta edició" explica las dos versiones
  (impresa UJI 2006 / revisión 2016) y de dónde sale cada cosa; README y CLAUDE.md alineados (2026-09-02).

- [x] **T-18** Generación de mapas reproducible: `opentype.js` es dependencia de desarrollo de `site/`, los scripts la
  resuelven solos, y `extract/mapa/genera.sh` (= `npm run mapes`) regenera los cuatro SVG; salida byte a byte idéntica (2026-09-02).

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
