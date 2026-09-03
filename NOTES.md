# Notas editoriales y hallazgos sobre el original

Registro de todo lo detectado en el PDF de origen. Nada de esto se "corrige" en el texto recuperado sin decisión explícita.

## Lagunas: ilustraciones perdidas en el propio PDF (resuelto el 2026-09-02, T-05)
**Ya no faltan**: la familia aportó las cuatro fotos y están en `assets/images/` (ver "Las cuatro fotografías perdidas,
recuperadas", más abajo). Se conserva el hallazgo como registro del estado del PDF de origen.
El índice de ilustraciones lista 30 figuras; el PDF solo contiene 26 imágenes únicas. Cuatro tienen el pie de foto
pero un enlace de imagen roto (cuadrado vacío) — se perdieron antes de generar el PDF:

| Nº índice | Figura      | Pág. PDF (física) | Pág. impresa |
|-----------|-------------|-------------------|--------------|
| 10        | Dalla       | 28                | 23           |
| 12        | Carrejador  | 31                | 26           |
| 14        | Trill       | 32                | 27           |
| 15        | Garbells    | 33                | 28           |

Todas son fotos de aperos de labranza.

## Calidad de imágenes
- 25 de las 26 fotos están a resolución de origen (≈2350×1570 px o similar). Se conservan los bytes JPEG originales.
- **"Mapa dels Ports"** (nº 1) es de 394×330 px: muy baja. Sustituido por un mapa redibujado (T-06, ver más abajo).
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
  las únicas diferencias son guiones de clítico que pdftotext elimina (posar-lo), exponentes (m²), números de nota y
  la lista de días del Sexenni (pág. 78, `p083.txt`), que pdftotext lee por columnas (primero los días, luego los
  gremios) y por eso da 12 "desajustes de orden" que no son tales. Comprobado el 2026-09-03 (T-13).

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

## Las cuatro fotografías perdidas, recuperadas (2026-09-02, T-05)
La familia ha aportado los originales de "Dalla", "Carrejador", "Trill" y "Garbells" (JPEG de 2048 px de lado mayor,
sin EXIF). Se incorporan sin recomprimir como `assets/images/10-dalla.jpg`, `12-carrejador.jpg`, `14-trill.jpg` y
`15-garbells.jpg`; `FIGURES` en `to_markdown.py` deja de tener entradas `None` y los placeholders desaparecen del texto,
de la galería y de "Sobre esta edició". La sección "Lagunas" de arriba queda como registro histórico. Los ficheros de la dalla y el carrejador llegaron girados 90° (sin EXIF); se han enderezado con `convert -rotate 90`
(sentido horario) y guardado con calidad 95; los originales recibidos siguen en `temp/` (fuera de git).

## Nuevo material de la familia en `source/` (2026-09-02)
Además del PDF de 2016 con el que se hizo la reconstrucción, la familia ha aportado:
- `Fotos/`: **los 31 ficheros de imagen originales** (30 fotos del libro + `Mapa_Dena.jpg`). Casi todas a más resolución
  que las incrustadas en el PDF (p. ej. 3072×2048 frente a 2353×1569) y, las de igual tamaño, menos comprimidas. Se han
  sustituido las 30 de `assets/images/` por estos originales, byte a byte, salvo cinco (aixades, forques, falç, dalla,
  carrejador) que llevaban una etiqueta EXIF de orientación errónea —los píxeles ya estaban bien orientados— y a las que
  se ha quitado el segmento EXIF sin recomprimir para que los navegadores no las giren. `Mapa_Morella.JPG` es la misma
  imagen de 394×330 del PDF (se mantiene el mapa redibujado). `Llegeix-me.txt`: "Fotografies antigues arxiu familiar de
  Francisca Julian Querol. Fotografies noves de Tadeo Julian Querol. Dedicatòria: Als meus parents i amics que són o han
  segut masovers" (la dedicatoria no aparece en el PDF de 2016).
- `Mapa_Dena.jpg` (2368×3376): mapa de la Dena dels Llivis dibujado a mano, con leyenda en castellano ("Signos
  convencionales"), masías, pistas, caminos, vías pecuarias, río, barrancos, ermita, tejería, molino, fuentes, bosque y
  escala. No está entre las 30 ilustraciones del libro; procedencia por confirmar (¿Gamundí, *Morella, guía del antiguo
  término*, 1991?). Coincide con el mapa de esta edición en la posición de "Solaneta", "Cantalà" (entre Cardona y
  Modesto), etc. No se publica: lo sustituye el mapa de la dena generado por esta edición (T-21 cerrada el
  2026-09-03); sigue sirviendo de referencia para T-17.
- `Masos_de_Morella_val1_17x23.doc`: el máster de texto de 2016 (Word). Su texto coincide con el Markdown reconstruido
  (las únicas diferencias son artefactos del índice: HYPERLINK, TOC…).
- `Masies_de_Morella_val1_17x23.pdf` (17/05/2016 14:10, 107 págs., 31 MB): versión 38 minutos anterior a la nuestra,
  con las mismas 27 imágenes pero a resolución completa (3072×2048).
- `Masies_de_Morella_val1_17x23a.pdf` (3/04/2006, Acrobat PDFWriter desde Word, 110 págs.): el texto tal como se envió a
  la editorial en 2006, con capa de texto. Frente a 2016 tiene 199 palabras distintas: la autora revisó formas
  dialectales (via→havia, vien→havien, cuina→cuinava…).
- **`Masos de Morella_Copia impressio.pdf` (escaneo de 2019, 150 págs., sin capa de texto): la edición impresa.**
  Es *Masies de Morella. Vida i costums en la Dena dels Llivis*, **Publicacions de la Universitat Jaume I, 2006**,
  ISBN 84-8021-570-4, impreso por Gràfiques Color Imprés (Castelló), "Tractament de textos: Lari Orenga Suliano",
  fotografías antiguas del archivo familiar y nuevas de Tadeo Julian Querol. Pruebas de imprenta fechadas 19/6/06.
  ~150 páginas a 17×23, con una **Presentació de Lluís Meseguer (págs. 9-10)** que no está en el PDF de 2016, y con el
  texto revisado por la editorial (el pròleg impreso empieza "Seria, a hores d'ara, interessant recordar…"; el de 2016,
  "Quan vaig decidir preparar el projecte…"). Índice impreso: Presentació 9, Pròleg 11, cap. 1 p. 13 … Conclusions 148,
  Bibliografia 149, Índex d'il·lustracions 151. Es decir: **el libro que se imprimió es la edición UJI de 2006, y el PDF
  de 2016 ("Masos de Morella") es una reelaboración posterior de la autora**, con título y texto distintos.
- `TT1139M_.TTF`: la fuente Calligraph421 BT usada en la cita del privilegio del Ligalló.

## Página "L'autora" (2026-09-02)
Biografía y retratos tomados de los proyectos hermanos de la familia, `jtpadilla/ramblacelumbres` (página "Els autors":
Francisca «Paquita» y Tadeo Julián Querol, hermanos nacidos en Cinctorres; cita de la presentación del blog, marzo 2014)
y `jtpadilla/santjoans`. Datos del libro: pròleg (padre Tadeo Julian, del Mas de Julian; UJI, Meseguer) y 8.2 (ferrer de
Cinctorres, Encarna de Francho). El colofón de 2006 acredita "Fotografies noves: Tadeo Julian Querol; antigues: arxiu
familiar": se acredita así en pie, licencia y galería. Retratos en `site/src/assets/autors/` (de ramblacelumbres,
src/assets/uploads/2014/03/2.jpg y 12.jpg). Editor y contacto: Juan Tadeo Padilla Julián, hijo de la autora.

## Referencia bibliográfica de la edición impresa (2026-09-02)
Única ficha localizada en línea: la tienda de Publicacions de la UJI (tenda.uji.es, id_art=720), con estado "ESGOTAT":
*Masos de Morella. Vida i costums en la dena dels Llivis*, Julian Querol, Francisca; Fora de col·lecció; 1ª ed. 2006;
152 págs.; 15 × 20 cm; rústica cosida; 10,00 €; ISBN 978-84-8021-570-1 (ISBN-10 84-8021-570-4, el del colofón). Nótese
que la editorial titula "Masos" aunque las pruebas de imprenta escaneadas digan "Masies". No aparece en Google Books, Open
Library, Todostuslibros, Iberlibro, Uniliber, Casa del Libro ni Dialnet (búsquedas del 2 de septiembre de 2026); Amazon,
WorldCat y la BNE no respondieron a la consulta automática. Datos en `content/llibre.yaml` (`edicio_impresa`), mostrados
en "Sobre esta edició" y como JSON-LD (schema.org/Book) en todas las páginas.

## Decisiones sobre las ediciones y los originales (2026-09-03)
- "Sobre esta edició" decía que la autora preparó el PDF de 2016 "per a una reimpressió que no va arribar a fer-se", y
  CLAUDE.md lo llamaba "PDF nunca impreso". La familia lo considera inexacto y se ha retirado: del PDF de 2016 solo se
  afirma que es la última revisión del texto en que trabajó la autora, sin decir para qué se preparó.
- **T-22 descartada**: no se recupera el texto de la edición impresa de 2006 (OCR del escaneo). La edición impresa
  queda documentada aquí (sección anterior sobre `source/`) y en "Sobre esta edició", con su ficha bibliográfica.
- **T-20 cerrada**: el sitio ofrece para descarga solo el PDF de 2016 (15 MB). El escaneo de la edición impresa (50 MB)
  y el PDF de 2016 a resolución completa (31 MB) no se enlazan, aunque el script `build` de `site/` copia todos los
  PDF de `source/` a `dist/original/`. La dedicatoria del `Llegeix-me.txt` no se incorpora.
- **T-21 cerrada**: el mapa manuscrito `source/Fotos/Mapa_Dena.jpg`, de procedencia sin confirmar, no se publica;
  su función la cumple `assets/images/ed-mapa-dena-llivis.svg`.

## Roda de l'any al mas (2026-09-03, T-23) — ilustración nueva de esta edición
`extract/mapa/roda_any.py` genera `assets/images/ed-roda-de-l-any.svg` con la misma librería que los mapas (rótulos en
EB Garamond como trazados). Es un diagrama circular con los doce meses, cuatro anillos (camp, ramat, casa, festes) y un
bloque de texto por mes. Todo el contenido sale del libro; cada línea de la tabla `MESOS` del script cita el apartado
(3.6 sembra, 3.8 sega, 4.11 esquiló, 5.5 bolets y calç, 5.6 matança, 5.8 llenya y ferramentes, 5.9 trufa, 5.10 mel,
5.12 carboneres, 6.4 arrendament, parròquia, venda de corders, caça, 7.1-7.5 festes). Decisiones: la venta de corderos
se fecha en junio-julio como dice 6.4 (4.6 la sitúa en "primavera", a los 4-5 meses); el Sexenni y el Anunci se marcan
como "cada sis anys"; los días fijos van como puntos sobre el anillo de fiestas; los periodos cortos (Fira, Vallivana) se
dibujan con la duración de una semana para que se vean. No se representan como arcos la caza ni las carboneras (solo
en el texto del mes) para no amontonar el anillo de invierno. Se inserta al final del capítulo 6, después del párrafo
que resume el ciclo del año ("…i una altra vegada a començar"), mediante la tabla `INSERTS` de `to_markdown.py`.
Presentación en el sitio: a la anchura de la columna (36rem) los rótulos no se leen, así que desde este cambio las
figuras `ed-*` salen de la columna hasta su anchura real (`.figura.editorial` en `global.css`; `rehype-book.mjs` toma
la anchura del `viewBox`) y todo SVG del texto va enlazado a `/imatges/<fichero>` (endpoint `src/pages/imatges/[file].ts`,
sin hash) para abrirlo a tamaño completo, como ya hacían la galería y "Sobre esta edició".
