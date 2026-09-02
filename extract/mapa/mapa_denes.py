#!/usr/bin/env python3
"""Genera assets/images/ed-mapa-de-les-denes.svg: les dotze denes del terme de Morella (cap. 1 del llibre), amb
els límits d'OpenStreetMap (extract/mapa/denes.osm.json; són entitats singulars amb codi INE) i l'estil del llibre.
Il·lustració nova d'esta edició (no existia en l'original). La Dena dels Llivis, tema del llibre, va destacada.
Uso: python3 extract/mapa/mapa_denes.py <dir node_modules con opentype.js>
"""
import json, sys
from mapalib import (ROOT, INK, PAPER, Projection, centroid, label, labels_open, regions, rings_of, svg_open,
                     text_paths)

DATA = json.load(open(ROOT / "extract/mapa/denes.osm.json", encoding="utf-8"))
OUT = ROOT / "assets/images/ed-mapa-de-les-denes.svg"
NODE_MODULES = sys.argv[1] if len(sys.argv) > 1 else "node_modules"

# Orden y nombres del libro (cap. 1) → nombre OSM. Rótulo en una o dos líneas.
DENES = [
    (1, "Dena de la Pobleta",           ["LA POBLA", "D’ALCOLEA"]),
    (2, "Dena dels Castellons",         ["ELS CASTELLONS"]),
    (3, "Dena d'Herbeset",              ["HERBESET"]),
    (4, "Dena de la Font d'en Torres",  ["FONT", "D’EN TORRES"]),
    (5, "Dena de Morella la Vella",     ["MORELLA", "LA VELLA"]),
    (6, "Dena de la Roca",              ["LA ROCA"]),
    (7, "Dena Primera del Riu",         ["PRIMERA", "DEL RIU"]),
    (8, "Dena Segona del Riu",          ["SEGONA", "DEL RIU"]),
    (9, "Dena de la Vespa",             ["LA VESPA"]),
    (10, "Dena de Coll i Moll",         ["COLL I MOLL"]),
    (11, "Dena dels Llivis",            ["ELS LLIVIS"]),
    (12, "Dena de Muixacre",            ["MUIXACRE"]),
]
# Desplazamiento del rótulo respecto al centroide (dx, dy), ajustado a mano
OFFSET = {"Dena Segona del Riu": (22, 16), "Dena de Morella la Vella": (0, 4)}
MORELLA = (40.6188, -0.0998)
W, H, MARGIN = 1000, 900, 40

munis = {r["name"]: rings_of(r) for r in DATA["relations"]}
missing = [n for _, n, _ in DENES if n not in munis]
assert not missing, f"faltan en OSM: {missing}"
polys = [(n, munis[n]) for _, n, _ in DENES]
proj = Projection([p for _, rings in polys for ring in rings for p in ring], W, H, MARGIN)

req = [{"id": f"{n}|{i}", "text": line, "size": 12.5, "weight": 500, "tracking": 1.3}
       for _, n, lines in DENES for i, line in enumerate(lines)]
req += [{"id": f"{n}|num", "text": str(k), "size": 11, "weight": 600, "tracking": 0} for k, n, _ in DENES]
req.append({"id": "morella", "text": "Morella", "size": 15, "weight": 600, "tracking": 0.3})
glyphs = text_paths(req, NODE_MODULES)

svg = svg_open(W, H, "Les denes de Morella",
               "Mapa de les dotze denes del terme municipal de Morella, amb la Dena dels Llivis destacada")
svg += regions(proj, polys, highlight={"Dena dels Llivis"})
svg.append(labels_open())
for k, n, lines in DENES:
    big = max(munis[n], key=len)
    cx, cy = centroid(proj.ring(big, 0.3))
    dx, dy = OFFSET.get(n, (0, 0))
    y0 = cy + dy - (len(lines) - 1) * 7.5
    for i, line in enumerate(lines):
        svg.append(label(glyphs[f"{n}|{i}"], cx + dx, y0 + i * 15 + 4))
    # número de orden del libro, encima del rótulo
    svg.append(label(glyphs[f"{n}|num"], cx + dx, y0 - 13))
x, y = proj(MORELLA[1], MORELLA[0])
svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5"/>')
svg.append(label(glyphs["morella"], x - 9, y + 5, "end"))
svg.append('</g></svg>')
OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size // 1024} KB")
