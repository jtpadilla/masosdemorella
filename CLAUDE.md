# Masos de Morella — recuperación digital

## Qué es este proyecto

Recuperar y publicar online el libro **"Masos de Morella. Vida i costums en la Dena dels Llivis"**
de Francisca Julián i Querol (edición única y pequeña, sin ejemplares localizables; masters del editor
perdidos). La única fuente que queda es `source/Masos_de_Morella_val1_17x23.pdf`, el PDF previo a imprenta.

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
  reflejan una maquetación final distinta (probablemente la impresa a 17×23, ~105 págs.). Se usa la paginación
  del PDF como referencia y se documenta la discrepancia.
- Título inconsistente en el propio original: portada **"MASOS de Morella"**, cabecera de página
  **"Masies de Morella"**. Se respeta tal cual.
- **Imágenes**: 27 imágenes raster JPEG, 26 únicas (la de portada, "Mas de Julian", se repite en pág. física 48).
  Calidad muy buena: la mayoría ~2350×1570 px a ~600 ppi efectivos. Se extraen sin recomprimir con
  `pdfimages -all`. Excepción: **"Mapa dels Ports"** (pág. física 8) es de solo 394×330 px — baja calidad,
  candidata a sustituir/redibujar si se localiza una fuente mejor.
- **4 ilustraciones perdidas ya en el original**: el índice lista 30, pero las figuras **"Dalla"** (pág. física 28),
  **"Carrejador"** (pág. 31), **"Trill"** (pág. 32) y **"Garbells"** (pág. 33) solo tienen el pie y un enlace de imagen roto
  (cuadradito vacío). No son recuperables desde el PDF. En el sitio se dejan como lagunas documentadas
  (placeholder + nota) por si la familia conserva las fotos.
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
source/                 PDF original (intocable, artefacto de archivo)
extract/                salida de extract/extract.sh: text/pNNN.txt, text/book.xml (fuentes), images/, render/ (ignorado en git)
content/                MASTERS RECUPERADOS: un .md por capítulo, frontmatter con título/número
assets/images/          JPEG originales renombrados NN-figura.jpg (NN = orden en el índice de ilustraciones; faltan 10,12,14,15)
site/                   proyecto Astro (lee content/ y assets/)
NOTES.md                decisiones editoriales, lagunas, discrepancias detectadas
```

## Flujo de trabajo de la reconstrucción

1. **Extracción** (herramientas disponibles en la máquina: poppler `pdftotext`/`pdfimages`/`pdftoppm`,
   `gs`, ImageMagick, python3, node 24; **no** hay tesseract ni qpdf):
   - `pdftotext -layout` por página a `extract/text/pNNN.txt`.
   - `pdfimages -all` a `extract/images/` (bytes JPEG originales, sin recomprimir).
   - `pdftoppm -r 150 -png` de todas las páginas a `extract/render/` como referencia visual para corregir.
2. **Reconstrucción** en `content/`: un fichero por capítulo (Pròleg, 1-8, Conclusions, Bibliografia,
   Índex d'il·lustracions). Reglas:
   - Quitar cabeceras corridas ("Masies de Morella. Vida i costums…") y pies de página.
   - Conservar la paginación original como ancla: `<span class="pag" id="p23"></span>` al inicio de cada página
     impresa (permite citar "pág. 23" del original).
   - Unir líneas partidas por la justificación; deshacer guiones de partición de palabra solo si la palabra
     no lleva guion real (comprobar contra el render).
   - Notas al pie → notas Markdown `[^n]`, numeradas por capítulo.
   - Figuras → `![Pie](../assets/images/xx.jpg)` con el pie exacto del índice de ilustraciones.
   - Cursivas y negritas: preservarlas (no se ven en `pdftotext`; hay que cotejar con el render o usar
     `pdftotext -bbox-layout` / fuentes por span).
3. **Revisión** capítulo a capítulo contra `extract/render/`. Anotar dudas en `NOTES.md`, no "corregir" el original.
4. **Sitio**: Astro en `site/`, un `[slug].astro` por capítulo, índice general, galería de ilustraciones,
   búsqueda, página "Sobre esta edición" explicando la recuperación y las lagunas, enlace al PDF original.
   Estilo: tipografía serif de libro, ancho de lectura ~65 caracteres, modo claro/oscuro, CSS de impresión.

## Convenciones

- Commits y ficheros en castellano; contenido del libro en el valenciano original, sin normalizar ortografía.
- Nombres de imágenes: `NN-descripcion-corta.jpg` donde NN es el orden en el índice de ilustraciones.
- No se sube nada derivado (webp, dist/) al repo: se genera en CI.
- Todo hallazgo sobre el original (erratas, lagunas, discrepancias) va a `NOTES.md`, no se silencia.
