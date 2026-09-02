#!/usr/bin/env bash
# Regenera los cuatro mapas SVG de esta edición (assets/images/01-mapa-dels-ports.svg y ed-*.svg).
# Requiere python3, node y las dependencias del sitio instaladas (cd site && npm install: aporta opentype.js).
# Con --png, exporta además una vista PNG de cada uno a extract/mapa/preview/ (requiere inkscape).
set -euo pipefail
cd "$(dirname "$0")"
[ -d ../../site/node_modules/opentype.js ] || { echo "Falta opentype.js: ejecuta 'npm install' en site/" >&2; exit 1; }
for m in ports denes llivis julian; do
  python3 "mapa_$m.py"
done
if [ "${1:-}" = "--png" ]; then
  mkdir -p preview
  for f in ../../assets/images/01-mapa-dels-ports.svg ../../assets/images/ed-*.svg; do
    inkscape --export-type=png --export-width=1200 --export-filename="preview/$(basename "${f%.svg}").png" "$f" >/dev/null 2>&1
  done
  echo "vistas en extract/mapa/preview/"
fi
