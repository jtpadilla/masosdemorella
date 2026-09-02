# Notas editoriales y hallazgos sobre el original

Registro de todo lo detectado en el PDF de origen. Nada de esto se "corrige" en el texto recuperado sin decisión explícita.

## Lagunas: ilustraciones perdidas en el propio PDF
El índice de ilustraciones lista 30 figuras; el PDF solo contiene 26 imágenes únicas. Cuatro tienen el pie de foto
pero un enlace de imagen roto (cuadrado vacío) — se perdieron antes de generar el PDF:

| Nº índice | Figura      | Pág. PDF (física) | Pág. impresa |
|-----------|-------------|-------------------|--------------|
| 10        | Dalla       | 28                | 23           |
| 12        | Carrejador  | 31                | 26           |
| 14        | Trill       | 32                | 27           |
| 15        | Garbells    | 33                | 28           |

Todas son fotos de aperos de labranza. Acción posible: pedir a la familia si conservan las fotos originales.

## Calidad de imágenes
- 25 de las 26 fotos están a resolución de origen (≈2350×1570 px o similar). Se conservan los bytes JPEG originales.
- **"Mapa dels Ports"** (nº 1) es de 394×330 px: muy baja. Candidata a sustituir por un mapa nuevo o mejor fuente.
- La foto de portada es la misma que la figura 21 "Mas de Julian" (bytes idénticos).
- Figuras 27, 28 y 29 son fotografías en escala de grises (fotos antiguas: 1925, romería, 1928).

## Paginación
- Págs. físicas 6–105 del PDF = págs. impresas 1–100 (offset 5). Físicas 3–4 = i–ii. Físicas 1, 2 y 5 sin numerar.
- El índice general y el de ilustraciones remiten a una paginación distinta (hasta la 105), probablemente la de la
  maqueta final a 17×23 cm. Divergencia creciente: ~+1 al principio, ~+5 al final. Se usa la paginación del PDF.

## Inconsistencias del original (se respetan)
- Portada: "MASOS de Morella". Cabecera corrida de todas las páginas: "Masies de Morella. Vida i costums en la Dena dels Llivis".
- Índice: "Ermita de San Pere màrtir" / texto: "Sant Pere Màrtir". "Les manses y l'esquella" (y castellana).
- Índice de ilustraciones: "l'’ermita" con doble apóstrofo.

## Extracción
- Fuentes por fragmento en `extract/text/book.xml` (pdftohtml -xml): prefijo `FAAAAA+LiberationSerif` = cursiva,
  `EAAAAA+LiberationSerif` = negrita, `DAAAAA+` = redonda. pdftohtml además envuelve cursivas en `<i>`.
- Notas al pie: cuerpo 7 pt (fontspec 18/19) al final de página, separadas por línea.

## Reconstrucción a Markdown (extract/to_markdown.py) — decisiones
- **Números de apartado**: en el PDF el "3.8." de cada apartado es un glifo vacío de la fuente Symbol (se perdió al
  exportar). Se reasignan por orden dentro de cada capítulo y el script comprueba que los 47 apartados coinciden
  con el índice de marcadores (`<outline>`) que sí conserva el PDF. Los subapartados 8.3.1–8.3.6 llevan el número
  en el propio texto.
- **Notas al pie**: el original las numera por página (casi siempre "1"). Se renumeran correlativamente por capítulo
  (`[^n]`); el script comprueba que llamadas y definiciones cuadran (36 notas en total).
- **Anclas de paginación**: `<a id="pNN"></a>` en el punto exacto del salto de página impreso (NN = paginación del PDF).
- **Cursiva parcial**: en 7.4 el original tiene "L" en redonda y "laurà" en cursiva (y "S"/"embrà"); se unifica en
  *Llaurà*, *Sembrà*. Regla general: un fragmento alfabético pegado a una palabra adopta el estilo de la palabra.
- **Puntuación**: hereda el estilo de sus vecinos cuando ambos coinciden (evita `*.*`).
- **Saltos de línea manuales**: las citas de prensa de 8.1 y algún pasaje de 7.4 tienen saltos de línea dentro del
  párrafo; se detectan por línea corta seguida de interlineado normal y se conservan como salto duro (`\`).
- **Rayas de diálogo** ("- On has estat?") se escapan (`\-`) para que Markdown no las convierta en lista.
- **Remedios (5.7)**: "Ingredients: - x" se convierte en etiqueta en negrita + lista; "Preparació:" en negrita.
- **Índice de ilustraciones**: se conserva como lista "Nombre — página", con los números de página del original
  (que no coinciden con esta paginación, ver arriba). El índice general (págs. i-ii) no se transcribe: lo genera el sitio.
- **Portada y portadilla** (págs. físicas 1 y 5): transcritas en `content/llibre.yaml`.
- Página impresa 81 (física 86) está en blanco en el original; el ancla `p81` se emite junto a la de la 82.
- Verificación: `extract/check.py` compara palabra a palabra PDF ↔ Markdown (recuento y orden). Resultado limpio:
  las únicas diferencias son guiones de clítico que pdftotext elimina (posar-lo), exponentes (m²) y números de nota.

## Revisión visual página a página (2026-09-02)
Cotejadas las 100 páginas impresas del PDF (`extract/render/`) contra el Markdown (`extract/segment.py N` imprime el
segmento entre anclas). Defectos encontrados y corregidos en `to_markdown.py`:
- **Dos figuras enlazadas a la foto equivocada**: "Pastador del Mas de Julian…" (nº 22) y "Foto familiar del Mas de
  Julian (1925)" (nº 27) mostraban la foto nº 21 porque el pie se emparejaba por subcadena ("Mas de Julian"). Ahora
  se empareja por el inicio exacto del pie.
- **Puntuación dentro de la cursiva** (`*alcaldillo.*`, `*, els topins*`, `germinar”.*`): en el original la puntuación
  contigua a una palabra en cursiva a veces lleva cursiva y a veces no; se saca siempre fuera del énfasis. Es la
  única normalización tipográfica además de la cursiva parcial (ver arriba).
- **Llamadas de nota** a caballo de dos líneas (pág. 11): el superíndice va más alto que la línea y se agrupaba con la
  siguiente; tolerancia mayor para superíndices.
- **Listas con guion sangrado** (págs. 20, 74): ahora son listas Markdown; las rayas de diálogo a margen (contes) siguen
  siendo párrafos con `\-`, y el programa de gremios del Sexenni (pág. 77-78) conserva sus saltos de línea.
- **Ancla de página mal situada** cuando un párrafo acababa justo al final de página con la última línea llena y la
  página siguiente empezaba con un título (págs. 37, 100): el ancla se colocaba antes del párrafo en vez de después.
- **`383.549 Km²`** (pág. 2): el PDF pinta el 2 elevado pero lo almacena en línea con el texto; se corrige de forma
  puntual (el otro caso, `3333m²`, sí venía como superíndice).
Errores del original que se conservan tal cual: "Km." por "km" (pág. 5: "650 Km."), "1194-95" por "1994-95" (pág. 82),
"cas urbà" (pág. 69), "l’’ermita" en el índice de ilustraciones, "(20 m2)" en línea (pág. 13), ausencia de punto en
"de la pluja Aquestes" (pág. 39), "posarlo"/"acostumarlos" van con guion en el PDF (posar-lo) aunque pdftotext lo pierda.

## Mapa dels Ports redibujado (2026-09-02, T-06)
El mapa original (fig. 1) era una imagen de 394×330 px. Se ha sustituido en el texto y en la galería por
`assets/images/01-mapa-dels-ports.svg`, generado por `extract/mapa/mapa_ports.py` a partir de los límites
municipales de OpenStreetMap (`extract/mapa/ports.osm.json`, descargados de Overpass; © colaboradores de OSM, ODbL).
Reproduce el contenido del original: los mismos 13 municipios y rótulos (Zorita, Palanques, Herbers, Villores,
El Forcall, La Todolella, Olocau del Rey, La Mata, Morella, Vallibona, Cinctorres, Portell de Morella, Castellfort).
El original omitía Vilafranca, que también pertenece a la comarca; se respeta esa elección. Estilo: tinta sobre
papel, Morella destacada, rótulos en EB Garamond convertidos a trazados (`extract/mapa/text2path.mjs`, opentype.js).
El JPEG original se conserva sin tocar en `assets/images/01-mapa-dels-ports.jpg`.

## Mapa de les denes (2026-09-02) — ilustración nueva de esta edición
OSM contiene las doce denes de Morella como relaciones `boundary=historic` (con código INE: siguen siendo entidades
singulares de población). Coinciden una a una con la lista del capítulo 1. Geometría en `extract/mapa/denes.osm.json`
(incluye 25 masos con nombre de la zona de los Llivis, por si se hace un mapa de detalle de la dena).
`extract/mapa/mapa_denes.py` genera `assets/images/ed-mapa-de-les-denes.svg` (prefijo `ed-` = ilustración de esta
edición, no del original) con la numeración y los nombres del libro y la Dena dels Llivis destacada.
Equivalencias de nombre: "Dena de la Pobla d'Alcolea" (libro) = "Dena de la Pobleta" (OSM); "Dena del Herbeset" =
"Dena d'Herbeset". El núcleo urbano de Morella no pertenece a ninguna dena (hueco en el centro del mapa).
Los dos mapas comparten `extract/mapa/mapalib.py`.
Colocación: se inserta en el capítulo 1 tras la lista de las doce denes (tabla `INSERTS` de `to_markdown.py`; el sitio
la marca "Il·lustració d'esta edició" en el pie por el prefijo `ed-` del fichero) y además en la galería (apartado
propio) y en "Sobre esta edició". Es la única adición al texto del original; `check.py` la excluye del cotejo.

## Datos para un mapa de la Dena dels Llivis (2026-09-02)
Inventario de fuentes, todas descargadas y recortadas a la dena en `extract/mapa/llivis/` (2,7 MB):
- **Nomenclàtor Toponímic Valencià** (ICV/AVL, CC-BY) — `ntv-puntos/lineas/poligonos.geojson`, vía WFS
  `https://terramapas.icv.gva.es/0103_NTV` (capas `ms:NTV.Puntos|Lineas|Poligonos`, campos `elemento`,
  `texto_normalizado`). Es la fuente principal: **los 21 masos del libro** (Solarreta aparece como "la Solaneta";
  Julian como "Mas de Julià"; Olivares como "Hostal d'Olivares"), 8 fuentes y ullals, 6 eras, 4 balsas, 3 pozos,
  3 corrales, 2 sénies, 19 "mitgeres" (paredes medianeras), árboles singulares, 20 collados/lomas, 32 barrancos con
  nombre, 27 caminos/sendas/entradores, **6 assagadors** (Serra dels Llivis, Candeales, Llivis, Canada, Carrascals,
  Hostal de la Roja), sierras (Calduc, Marinet), ermitas de Sant Pere Màrtir y Sant Isidre, la escuela, y 110 polígonos
  de partidas (bancales, bosques, solanas, umbrías, devesas, foies).
- **Vies pecuàries oficiales** (Conselleria de Medi Ambient vía ICV, CC-BY) — `vies-pecuaries-capa9.geojson`
  (trazados, con nombre, situación legal, longitud y anchura) y `capa8` (elementos pecuarios: abrevaderos, descansaderos),
  desde el ArcGIS REST `https://carto.icv.gva.es/arcgis/rest/services/tm_medio_ambiente/forestal/MapServer` (capas 9 y 8).
  Cubre las coladas del libro (Campello, Candeales, Cana d'Ares, Serra dels Llivis, Sendera dels Llivis).
- **Nomenclátor Geográfico Básico de España** (IGN, CC-BY 4.0) — `ngbe.json`, 72 topónimos (40 dentro), vía WFS INSPIRE
  `https://www.ign.es/wfs-inspire/ngbe` (bbox en orden lon,lat). Formas castellanizadas (Masía Torre-Segura, Barranco
  Billota…); útil como contraste, no como fuente principal.
- **Catastro** (INSPIRE WFS de edificios, `http://ovc.catastro.meh.es/INSPIRE/wfsBU.aspx`) — `catastro-edificis.gml`,
  46 edificios con huella y uso (12 residenciales, 29 agrarios): permite dibujar las masías como planta real.
- **OpenStreetMap** (ODbL) — `osm.json`, 129 elementos: 25 pistas, GR-7, la carretera Ares–Morella, 14 tramos de
  barranco, límite de la dena, ermita, escuela, Toll de la Giroveta; solo 7 masos. Aporta sobre todo la red de caminos
  con geometría continua.
- No usados: MDT/curvas de nivel del ICV (BCV05) y ortofoto PNOA, si se quisiera relieve o sombreado.
Cotejo con el libro: las 4 fuentes citadas (Ullals de Torre Segura, Cardona, Llivis, Marín) están en el NTV; Grèvol y
Garró solo en el NGBE ("Font del Grevol") o sin localizar. Los 4 barrancos (Bellota, Garró, Racó, Creus) están.
Turó de la Clotxa, Collet de Llambroix y Collet de la Corralisa: la Clotxa sí; los otros dos, pendientes de localizar.

## Mapa de la Dena dels Llivis (2026-09-02, T-15)
`extract/mapa/mapa_llivis.py` → `assets/images/ed-mapa-dena-llivis.svg`, insertado en 1.1 tras la lista de los 21 masos
(`INSERTS`). Contenido: los 21 masos con los nombres del libro (Solarreta = "la Solaneta" del NTV; Llivis por el NGBE),
Mas de Julian destacado; las fuentes del libro localizadas (Ullals de Torre Segura, Cardona, Llivis, Marín; Grèvol por el
NGBE; Garró no localizada); los barrancos del libro rotulados con su nombre (Bellota, Garró, Racó, Creus) más el riu Torre
Segura y la Rambla de la Cana d'Ares; las colades oficiales con los nombres del libro (Sendera dels Llivis = "Vereda de los
Llivis"); Serra Calduch y Serra de Marinet; ermitas de Sant Pere Màrtir y Sant Isidre; caminos y pistas de OSM; CV-12.
Leyenda, escala (1 km) y norte. Los rótulos usan glifos definidos una vez y reutilizados con <use> (text2path.mjs) para
que los SVG pesen poco.

## Croquis del Mas de Julian amb las fotos (2026-09-02, T-16)
`extract/mapa/mapa_julian.py` → `assets/images/ed-mas-de-julian.svg`, insertado en 5.1 tras la foto 21 "Mas de Julian".
Catastro no tiene el edificio, así que la casa, el anexo, el huerto cercado, la era circular y las paredes principales se
han trazado a mano sobre la ortofoto PNOA (IGN) centrada en el punto "Mas de Julià" del NTV (coordenadas en el script,
sistema de la ventana ampliada); el camino es de OSM (`llivis/cami-julia.json`). Miniaturas de las fotos 13, 16, 19, 20,
21, 22 y 27 en `llivis/thumbs/` (360 px, embebidas en el SVG). Direcciones de las fotos deducidas de ellas mismas: la Mola
de la Garumba (OSM: 40.6162, -0.1600) está justo al norte del mas, Cinctorres al oeste-suroeste; la bassa no se distingue en
la ortofoto y va marcada como posición aproximada; el pastador es interior. Los números de las fotos son los del índice
de ilustraciones.
