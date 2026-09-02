#!/usr/bin/env python3
"""Genera assets/images/01-mapa-dels-ports.svg: versión nueva del "Mapa dels Ports" del libro, con los límites
municipales reales (OpenStreetMap, extract/mapa/ports.osm.json) y el estilo del libro (tinta sobre papel,
rótulos en EB Garamond convertidos a trazados con text2path.mjs para que se vean igual en cualquier visor).

Reproduce los 13 municipios que dibujaba el mapa original (omite Vilafranca, como aquel) y sus mismos rótulos.
Uso: python3 extract/mapa/mapa_ports.py [dir node_modules con opentype.js; por defecto site/node_modules]
"""
import json, sys
from mapalib import ROOT, glyph_defs, Projection, label, labels_open, regions, rings_of, svg_open, text_paths

DATA = json.load(open(ROOT / "extract/mapa/ports.osm.json", encoding="utf-8"))
OUT = ROOT / "assets/images/01-mapa-dels-ports.svg"
NODE_MODULES = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "site/node_modules")

# Municipios del mapa original → nombre OSM, rótulo (como en el original) y núcleo urbano (lat, lon).
MUNIS = [
    ("Zorita del Maestrazgo", ["ZORITA"],            (40.7275, -0.1672)),
    ("Palanques",             ["PALANQUES"],         (40.7174, -0.1791)),
    ("Herbers",               ["HERBERS"],           (40.7207, -0.0044)),
    ("Villores",              ["VILLORES"],          (40.6763, -0.2007)),
    ("Forcall",               ["EL FORCALL"],        (40.6461, -0.1996)),
    ("Todolella",             ["LA", "TODOLELLA"],   (40.6470, -0.2468)),
    ("Olocau del Rey",        ["OLOCAU", "DEL REY"], (40.6376, -0.3399)),
    ("la Mata de Morella",    ["LA MATA"],           (40.6164, -0.2795)),
    ("Morella",               ["MORELLA"],           (40.6188, -0.0998)),
    ("Vallibona",             ["VALLIBONA"],         (40.6031, 0.0466)),
    ("Cinctorres",            ["CINCTORRES"],        (40.5826, -0.2161)),
    ("Portell de Morella",    ["PORTELL DE", "MORELLA"], (40.5328, -0.2622)),
    ("Castellfort",           ["CASTELLFORT"],       (40.5022, -0.1911)),
]
# Colocación del rótulo respecto al punto del núcleo: (dx, dy, anclaje)
PLACE = {
    "Zorita del Maestrazgo": (0, -12, "middle"),
    "Palanques":             (0, 20, "middle"),
    "Herbers":               (0, 22, "middle"),
    "Villores":              (0, -11, "middle"),
    "Forcall":               (10, 5, "start"),
    "Todolella":             (-9, -4, "end"),
    "Olocau del Rey":        (0, 22, "middle"),
    "la Mata de Morella":    (-10, 5, "end"),
    "Morella":               (0, 30, "middle"),
    "Vallibona":             (12, 6, "start"),
    "Cinctorres":            (0, 22, "middle"),
    "Portell de Morella":    (-10, -2, "end"),
    "Castellfort":           (0, 22, "middle"),
}
W, H, MARGIN = 1000, 900, 40

munis = {r["name"]: rings_of(r) for r in DATA["relations"]}
polys = [(n, munis[n]) for n, _, _ in MUNIS]
proj = Projection([p for _, rings in polys for ring in rings for p in ring], W, H, MARGIN)

req = [{"id": f"{n}|{i}", "text": line, "size": 19 if n == "Morella" else 12.5,
        "weight": 600 if n == "Morella" else 500, "tracking": 2.2 if n == "Morella" else 1.3}
       for n, lines, _ in MUNIS for i, line in enumerate(lines)]
glyphs = text_paths(req, NODE_MODULES)

svg = svg_open(W, H, "Mapa dels Ports", "Mapa dels Ports: els municipis de la comarca al voltant de Morella")
svg.append(glyph_defs())
svg += regions(proj, polys, highlight={"Morella"})
svg.append(labels_open())
for name, lines, (lat, lon) in MUNIS:
    x, y = proj(lon, lat)
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4.2 if name == "Morella" else 3.2}"/>')
    dx, dy, anchor = PLACE[name]
    lh = 23 if name == "Morella" else 15
    for i, line in enumerate(lines):
        svg.append(label(glyphs[f"{name}|{i}"], x + dx, y + dy + i * lh, anchor))
svg.append('</g></svg>')
OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size // 1024} KB")
