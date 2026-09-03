#!/usr/bin/env python3
"""Genera assets/images/ed-relleu-i-rius.svg: relleu i hidrografia del terme de Morella (T-28), il·lustració nova
d'esta edició per al capítol 1. Dibuixa el terme (OpenStreetMap, extract/mapa/ports.osm.json) i els municipis veïns
(ports.osm.json + relleu.osm.json), els rius Bergants, Cérvol, Caldes i Torre Segura, el port de Torremiró, les set
muntanyes que cita el capítol amb les altituds del llibre, Xiva i Herbeset, i la Dena dels Llivis (denes.osm.json).

Identificació de les muntanyes del llibre amb els cims d'OSM (vegeu NOTES.md): Carrascals = Mola del Carrascal,
Regafolet = Regatxol (1259 m exactes), Muixacre = el Muixacre, Fusters = el Moletó (a les Moles de Fusters), Nevera =
Tossal de la Nevera. "Pinar" i "Morella la Vella" no tenen cim amb eixe nom en OSM: es marquen amb triangle buit en
una posició aproximada (el Pinar de Xiva i el mas de Morella la Vella).
Uso: python3 extract/mapa/mapa_relleu.py [dir node_modules con opentype.js; por defecto site/node_modules]
"""
import json, math, sys
from mapalib import (ROOT, FILL, FILL_HI, INK, INK_SOFT, PAPER, Projection, centroid, glyph_defs, label, labels_open,
                     rings_of, svg_open, text_paths)

PORTS = json.load(open(ROOT / "extract/mapa/ports.osm.json", encoding="utf-8"))
RELLEU = json.load(open(ROOT / "extract/mapa/relleu.osm.json", encoding="utf-8"))
DENES = json.load(open(ROOT / "extract/mapa/denes.osm.json", encoding="utf-8"))
OUT = ROOT / "assets/images/ed-relleu-i-rius.svg"
NODE_MODULES = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "site/node_modules")
AIGUA = "#4e6f8c"

# Muntanyes del capítol 1 (nom i altitud del llibre) → cim d'OSM o posició aproximada (lat, lon)
CIMS = [
    ("Carrascals", 1263, "Mola del Carrascal", None, (0, -8, "middle")),
    ("Pinar", 1081, None, (40.6533, -0.1155), (-9, 4, "end")),                # aprox.: el Pinar de Xiva
    ("Regafolet", 1259, "Regatxol", None, (9, 4, "start")),
    ("Morella la Vella", 1068, None, (40.6418, -0.1412), (-9, 4, "end")),    # aprox.: mas de Morella la Vella
    ("Muixacre", 1274, "el Muixacre", None, (9, 4, "start")),
    ("Fusters", 1294, "el Moletó", None, (9, 4, "start")),
    ("Nevera", 1286, "Tossal de la Nevera", None, (0, -8, "middle")),
]
ALTRES = [("Turmell", "el Turmell", (9, 4, "start")), ("Mola Garumba", "Mola de la Garumba", (0, 16, "middle"))]  # cap. 1 i 2, sense altitud al llibre
RIUS = {  # nom del llibre: (noms OSM, fracció del tram on va el rètol, desplaçament perpendicular)
    "Riu Bergants": (("Riu Bergantes", "Río Bergantes"), 0.30, -9),
    "Riu Cérvol": (("Riu Cervol",), 0.55, -9),
    "Riu Caldes": (("Riu de Calders",), 0.5, -8),
    "Riu Torre Segura": (("Barranc de la Torre Segura",), 0.5, 9),
}
# Municipis veïns: nom OSM → rètol (grafia del llibre quan el cita)
VEINS = {
    "Herbers": "HERBÉS", "Torre de Arcas / Torredarques": "TORRE D’ARQUES", "Ares del Maestrat": "ARES DEL MAESTRE",
    "Catí": "CATÍ", "Castell de Cabres": "CASTELL DE CABRES", "Vallibona": "VALLIBONA", "Xert": "XERT",
    "Castellfort": "CASTELLFORT", "Cinctorres": "CINCTORRES", "Forcall": "FORCALL", "Palanques": "PALANQUES",
    "Zorita del Maestrazgo": "ZORITA", "Villores": "VILLORES", "Todolella": "LA TODOLELLA", "la Mata de Morella": "LA MATA",
    "Portell de Morella": "PORTELL", "Vilafranca / Villafranca del Cid": "VILAFRANCA", "Olocau del Rey": "OLOCAU",
}
OFFSET = {"Castell de Cabres": (28, 14), "Palanques": (-6, -14), "Vallibona": (0, -12)}   # ajust manual dels rètols
W, H, MARGIN = 1000, 1000, 30


def clip(poly, box):
    """Sutherland-Hodgman: retalla un polígon (x, y) al rectangle (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    edges = [(lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
             (lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
             (lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
             (lambda p: p[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1))]
    for inside, cross in edges:
        out = []
        for a, b in zip(poly, poly[1:] + poly[:1]):
            if inside(b):
                if not inside(a):
                    out.append(cross(a, b))
                out.append(b)
            elif inside(a):
                out.append(cross(a, b))
        poly = out
        if not poly:
            return []
    return poly


munis = {r["name"]: rings_of(r) for r in PORTS["relations"]}
munis.update({r["name"]: rings_of(r) for r in RELLEU["relations"]})
morella = munis["Morella"]
lats = [p[1] for r in morella for p in r]; lons = [p[0] for r in morella for p in r]
pad_lat, pad_lon = 0.045, 0.06                                       # ≈ 5 km al voltant del terme
frame = [(min(lons) - pad_lon, min(lats) - pad_lat), (max(lons) + pad_lon, max(lats) + pad_lat)]
proj = Projection(frame, W, H, MARGIN)
box = (MARGIN, MARGIN, W - MARGIN, H - MARGIN)
km = proj.scale / 111.2                                              # píxels per quilòmetre (latitud)
nodes = {n["name"]: n for n in RELLEU["nodes"]}
llivis = rings_of(next(r for r in DENES["relations"] if r["name"] == "Dena dels Llivis"))

# --- rètols -----------------------------------------------------------------------------------------------------
req = [{"id": "morella", "text": "MORELLA", "size": 17, "weight": 600, "tracking": 2.2}]
req += [{"id": f"vei|{n}", "text": t, "size": 10.5, "weight": 500, "tracking": 1.6} for n, t in VEINS.items()]
req += [{"id": f"cim|{n}", "text": f"{n}  {alt} m", "size": 11.5, "weight": 500, "tracking": 0.2} for n, alt, *_ in CIMS]
req += [{"id": f"alt|{n}", "text": n, "size": 11, "weight": 400, "tracking": 0.2} for n, *_ in ALTRES]
req += [{"id": f"riu|{n}", "text": n, "size": 11.5, "weight": 500, "tracking": 0.6} for n in RIUS]
req += [{"id": "torremiro", "text": "Port de Torremiró", "size": 11, "weight": 400, "tracking": 0.2},
        {"id": "xiva", "text": "Xiva", "size": 11, "weight": 400, "tracking": 0.2},
        {"id": "herbeset", "text": "Herbeset", "size": 11, "weight": 400, "tracking": 0.2},
        {"id": "llivis", "text": "DENA DELS LLIVIS", "size": 10, "weight": 600, "tracking": 2},
        {"id": "guadalop", "text": "cap al Guadalop", "size": 10, "weight": 400, "tracking": 0.2},
        {"id": "vinaros", "text": "cap a Vinaròs", "size": 10, "weight": 400, "tracking": 0.2},
        {"id": "n", "text": "N", "size": 13, "weight": 600, "tracking": 0},
        {"id": "escala", "text": "5 km", "size": 10.5, "weight": 400, "tracking": 0.2},
        {"id": "lleg1", "text": "Cim, amb l’altitud que dóna el llibre", "size": 10.5, "weight": 400, "tracking": 0},
        {"id": "lleg2", "text": "Posició aproximada (sense cim d’eixe nom en les fonts)", "size": 10.5, "weight": 400, "tracking": 0},
        {"id": "lleg3", "text": "Port de muntanya", "size": 10.5, "weight": 400, "tracking": 0}]
G = text_paths(req, NODE_MODULES)

svg = svg_open(W, H, "Relleu i rius del terme de Morella",
               "Mapa del terme de Morella amb les muntanyes, els rius i el port de Torremiró que cita el capítol 1, i els municipis veïns")
svg.append(glyph_defs())

# --- municipis --------------------------------------------------------------------------------------------------
svg.append(f'<g stroke="{INK_SOFT}" stroke-width="0.9" stroke-linejoin="round" fill="{FILL}">')
for n, rings in munis.items():
    if n != "Morella":
        svg.append(f'<path d="{proj.path(rings)}"/>')
svg.append('</g>')
svg.append(f'<path d="{proj.path(morella)}" fill="{FILL_HI}" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>')
svg.append(f'<path d="{proj.path(llivis)}" fill="none" stroke="{INK}" stroke-width="1.2" stroke-dasharray="5 3"/>')

# --- rius ---------------------------------------------------------------------------------------------------------
svg.append(f'<g fill="none" stroke="{AIGUA}" stroke-linecap="round" stroke-linejoin="round">')
for w in RELLEU["ways"]:
    pts = [proj(p["lon"], p["lat"]) for p in w["geometry"]]
    width = 2.2 if w["waterway"] == "river" else 1.3
    svg.append(f'<path stroke-width="{width}" d="M{"L".join(f"{x:.1f} {y:.1f}" for x, y in pts)}"/>')
svg.append('</g>')


def riu_label(nom, osm_names, frac, off):
    ways = [w for w in RELLEU["ways"] if w["name"] in osm_names]
    w = max(ways, key=lambda w: len(w["geometry"]))
    pts = [proj(p["lon"], p["lat"]) for p in w["geometry"]]
    i = max(1, min(len(pts) - 2, int(frac * len(pts))))
    (x1, y1), (x2, y2) = pts[max(0, i - 3)], pts[min(len(pts) - 1, i + 3)]
    a = math.degrees(math.atan2(y2 - y1, x2 - x1))
    if a > 90 or a < -90:
        a += 180
    x, y = pts[i]
    nx, ny = -math.sin(math.radians(a)), math.cos(math.radians(a))
    return f'<g transform="rotate({a:.1f} {x + nx * off:.1f} {y + ny * off:.1f})">{label(G[f"riu|{nom}"], x + nx * off, y + ny * off)}</g>'


svg.append(f'<g fill="{AIGUA}" stroke="{PAPER}" stroke-width="3" stroke-linejoin="round" paint-order="stroke">')
for nom, (osm, frac, off) in RIUS.items():
    svg.append(riu_label(nom, osm, frac, off))
svg.append('</g>')

# --- rètols dels municipis (centroide de la part visible) --------------------------------------------------------
svg.append(f'<g fill="{INK_SOFT}" stroke="{PAPER}" stroke-width="3" stroke-linejoin="round" paint-order="stroke">')
for n, t in VEINS.items():
    if n not in munis:
        continue
    big = max(munis[n], key=len)
    poly = clip(proj.ring(big, 0.3), box)
    if len(poly) < 3:
        continue
    cx, cy = centroid(poly)
    dx, dy = OFFSET.get(n, (0, 0))
    svg.append(label(G[f"vei|{n}"], cx + dx, cy + dy + 4))
svg.append('</g>')

# --- cims, port, poblacions --------------------------------------------------------------------------------------
svg.append(labels_open())


def triangle(x, y, s=6.5, hollow=False):
    fill = PAPER if hollow else INK
    return (f'<path d="M{x:.1f} {y - s:.1f}L{x + s * 0.95:.1f} {y + s * 0.6:.1f}L{x - s * 0.95:.1f} {y + s * 0.6:.1f}Z" '
            f'fill="{fill}" stroke="{INK}" stroke-width="1.4"/>')


for nom, alt, osm, pos, (dx, dy, anc) in CIMS:
    lat, lon = (nodes[osm]["lat"], nodes[osm]["lon"]) if osm else pos
    x, y = proj(lon, lat)
    svg.append(triangle(x, y, hollow=osm is None))
    svg.append(label(G[f"cim|{nom}"], x + dx, y + dy + (-4 if anc == "middle" else 0), anc))
for nom, osm, (dx, dy, anc) in ALTRES:
    x, y = proj(nodes[osm]["lon"], nodes[osm]["lat"])
    svg.append(triangle(x, y, s=5))
    svg.append(label(G[f"alt|{nom}"], x + dx, y + dy, anc))
# port de Torremiró: símbol de coll ")(" i rètol
pt = nodes["Port de Torre Miró"]; x, y = proj(pt["lon"], pt["lat"])
svg.append(f'<path d="M{x - 7:.1f} {y - 6:.1f}q5 6 0 12M{x + 7:.1f} {y - 6:.1f}q-5 6 0 12" fill="none" stroke="{INK}" stroke-width="1.6"/>')
svg.append(label(G["torremiro"], x + 11, y + 4, "start"))
# poblacions
for key, nom in (("xiva", "Xiva de Morella"), ("herbeset", "Herbeset")):
    n = nodes[nom]; x, y = proj(n["lon"], n["lat"])
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3"/>')
    svg.append(label(G[key], x + 7, y + 4, "start"))
n = nodes["Morella"]; x, y = proj(n["lon"], n["lat"])
svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5"/>')
svg.append(label(G["morella"], x, y + 24))
# Dena dels Llivis: rètol al centroide
cx, cy = centroid(proj.ring(max(llivis, key=len), 0.3))
svg.append(label(G["llivis"], cx, cy + 4))
# on van a parar els rius: rètol on el riu ix del marc
def eixida(names, vora):
    pts = [proj(p["lon"], p["lat"]) for w in RELLEU["ways"] if w["name"] in names for p in w["geometry"]]
    dins = [(x, y) for x, y in pts if MARGIN <= x <= W - MARGIN and MARGIN <= y <= H - MARGIN]
    return min(dins, key=lambda p: p[1]) if vora == "dalt" else max(dins, key=lambda p: p[0])
x, y = eixida(("Riu Bergantes", "Río Bergantes"), "dalt")
svg.append(f'<g fill="{INK_SOFT}">{label(G["guadalop"], x + 12, y + 14, "start")}</g>')
x, y = eixida(("Riu Cervol",), "dreta")
svg.append(f'<g fill="{INK_SOFT}">{label(G["vinaros"], x - 4, y + 16, "end")}</g>')
svg.append('</g>')

# --- nord, escala i llegenda ---------------------------------------------------------------------------------------
x, y = W - MARGIN - 40, MARGIN + 40
svg.append(f'<g fill="{INK}" stroke="{INK}"><path d="M{x} {y + 22}L{x} {y - 14}" stroke-width="1.4"/>'
           f'<path d="M{x} {y - 22}L{x - 5} {y - 10}L{x + 5} {y - 10}Z" stroke="none"/>{label(G["n"], x, y + 38)}</g>')
x, y = MARGIN + 20, H - MARGIN - 22
svg.append(f'<g stroke="{INK}" stroke-width="1.4"><path d="M{x} {y}h{5 * km:.1f}M{x} {y - 5}v10M{x + 5 * km:.1f} {y - 5}v10"/></g>')
svg.append(f'<g fill="{INK}">{label(G["escala"], x + 5 * km / 2, y - 8)}</g>')
x, y = MARGIN + 20, H - MARGIN - 90
svg.append(f'<g fill="{INK}">{triangle(x + 6, y)}{label(G["lleg1"], x + 20, y + 4, "start")}'
           f'{triangle(x + 6, y + 20, hollow=True)}{label(G["lleg2"], x + 20, y + 24, "start")}'
           f'<path d="M{x - 1} {y + 34}q5 6 0 12M{x + 13} {y + 34}q-5 6 0 12" fill="none" stroke="{INK}" stroke-width="1.6"/>'
           f'{label(G["lleg3"], x + 20, y + 44, "start")}</g>')
svg.append('</svg>')
OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size // 1024} KB")
