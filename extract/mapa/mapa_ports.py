#!/usr/bin/env python3
"""Genera assets/images/01-mapa-dels-ports.svg: versión nueva del "Mapa dels Ports" del libro, con los límites
municipales reales (OpenStreetMap, extract/mapa/ports.osm.json) y el estilo del libro (tinta sobre papel,
rótulos en EB Garamond convertidos a trazados con text2path.mjs para que se vean igual en cualquier visor).

Reproduce los 13 municipios que dibujaba el mapa original (omite Vilafranca, como aquel) y sus mismos rótulos.
Uso: python3 extract/mapa/mapa_ports.py <dir node_modules con opentype.js>
"""
import json, math, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = json.load(open(ROOT / "extract/mapa/ports.osm.json", encoding="utf-8"))
OUT = ROOT / "assets/images/01-mapa-dels-ports.svg"
NODE_MODULES = sys.argv[1] if len(sys.argv) > 1 else "node_modules"

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
PAPER, FILL, FILL_MORELLA, INK, INK_SOFT = "#fbf8f2", "#ece6d8", "#d3c7b0", "#2b2620", "#5b554b"


def rings_of(rel):
    """Encadena los tramos «outer» de la relación en anillos cerrados."""
    segs = [[(p["lon"], p["lat"]) for p in m["geometry"]] for m in rel["members"] if m["role"] in ("outer", "")]
    rings = []
    while segs:
        ring = segs.pop(0)
        while ring[0] != ring[-1]:
            for i, s in enumerate(segs):
                if s[0] == ring[-1]:
                    ring += s[1:]; segs.pop(i); break
                if s[-1] == ring[-1]:
                    ring += s[-2::-1]; segs.pop(i); break
            else:
                break
        rings.append(ring)
    return rings


def simplify(pts, tol):
    """Douglas-Peucker."""
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy) or 1e-9
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / norm
        if d > dmax:
            dmax, idx = d, i
    if dmax > tol:
        return simplify(pts[: idx + 1], tol)[:-1] + simplify(pts[idx:], tol)
    return [pts[0], pts[-1]]


munis = {r["name"]: rings_of(r) for r in DATA["relations"]}
names = [m[0] for m in MUNIS]
allpts = [p for n in names for ring in munis[n] for p in ring]
lat0 = sum(p[1] for p in allpts) / len(allpts)
kx = math.cos(math.radians(lat0))
xs = [p[0] * kx for p in allpts]; ys = [-p[1] for p in allpts]
scale = min((W - 2 * MARGIN) / (max(xs) - min(xs)), (H - 2 * MARGIN) / (max(ys) - min(ys)))
ox = (W - (max(xs) - min(xs)) * scale) / 2 - min(xs) * scale
oy = (H - (max(ys) - min(ys)) * scale) / 2 - min(ys) * scale


def proj(lon, lat):
    return (lon * kx * scale + ox, -lat * scale + oy)


def path_of(rings, tol=0.6):
    d = ""
    for ring in rings:
        pp = [proj(*p) for p in ring]
        h = len(pp) // 2                     # anillo cerrado: se simplifica por mitades (DP degenera si inicio == fin)
        pts = simplify(pp[: h + 1], tol)[:-1] + simplify(pp[h:], tol)
        d += "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"
    return d


# Rótulos → trazados
req = []
for name, lines, _ in MUNIS:
    big = name == "Morella"
    for i, line in enumerate(lines):
        req.append({"id": f"{name}|{i}", "text": line, "size": 19 if big else 12.5,
                    "weight": 600 if big else 500, "tracking": 2.2 if big else 1.3})
glyphs = json.loads(subprocess.run(["node", str(ROOT / "extract/mapa/text2path.mjs"), NODE_MODULES],
                                   input=json.dumps(req), capture_output=True, text=True, check=True).stdout)

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="Mapa dels Ports: els municipis de la comarca al voltant de Morella">',
       f'<title>Mapa dels Ports</title>',
       f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']
# Contorno exterior de la comarca: trazo grueso debajo de los rellenos (estos tapan los tramos interiores)
svg.append(f'<g fill="none" stroke="{INK}" stroke-width="4" stroke-linejoin="round">')
for name in names:
    svg.append(f'<path d="{path_of(munis[name])}"/>')
svg.append('</g>')
# Términos municipales
svg.append(f'<g stroke="{INK_SOFT}" stroke-width="0.9" stroke-linejoin="round">')
for name in names:
    fill = FILL_MORELLA if name == "Morella" else FILL
    svg.append(f'<path d="{path_of(munis[name])}" fill="{fill}"/>')
svg.append('</g>')
# Núcleos y rótulos
svg.append(f'<g fill="{INK}" stroke="{PAPER}" stroke-width="3" stroke-linejoin="round" paint-order="stroke">')
for name, lines, (lat, lon) in MUNIS:
    x, y = proj(lon, lat)
    r = 4.2 if name == "Morella" else 3.2
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')
    dx, dy, anchor = PLACE[name]
    lh = 23 if name == "Morella" else 15
    for i, line in enumerate(lines):
        g = glyphs[f"{name}|{i}"]
        tx = x + dx - (g["width"] if anchor == "end" else g["width"] / 2 if anchor == "middle" else 0)
        ty = y + dy + i * lh
        svg.append(f'<path transform="translate({tx:.1f} {ty:.1f})" d="{g["d"]}"/>')
svg.append('</g></svg>')
OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size // 1024} KB")
