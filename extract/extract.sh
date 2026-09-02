#!/usr/bin/env bash
# Extracción reproducible del PDF original. Requiere poppler-utils (pdftotext, pdfimages, pdftoppm, pdfinfo).
# Salida:
#   extract/text/pNNN.txt      texto por página física (pdftotext -layout)
#   extract/text/pNNN.raw.txt  texto por página en orden de lectura (pdftotext sin -layout)
#   extract/text/book.xml      pdftohtml -xml: texto con fuente por fragmento (detecta cursivas/negritas)
#   extract/images/            imágenes embebidas, bytes originales sin recomprimir (pdfimages -all)
#   extract/images.txt         listado de imágenes con página, tamaño, ppi
#   extract/render/pNNN.png    render de cada página a 150 ppi, referencia visual para revisar
set -euo pipefail
cd "$(dirname "$0")"
PDF=../source/Masos_de_Morella_val1_17x23.pdf
N=$(pdfinfo "$PDF" | awk '/^Pages:/{print $2}')

rm -rf text images render; mkdir -p text images render
pdfinfo "$PDF" > pdfinfo.txt
pdffonts "$PDF" > fonts.txt
pdfimages -list "$PDF" > images.txt

for i in $(seq 1 "$N"); do
  p=$(printf 'p%03d' "$i")
  pdftotext -layout -f "$i" -l "$i" "$PDF" "text/$p.txt"
  pdftotext         -f "$i" -l "$i" "$PDF" "text/$p.raw.txt"
done

pdftohtml -xml -i -q "$PDF" text/book
pdfimages -all "$PDF" images/img
pdftoppm -r 150 -png "$PDF" render/p

echo "Páginas: $N"; echo "Imágenes: $(ls images | wc -l)"; echo "Renders: $(ls render | wc -l)"
