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
