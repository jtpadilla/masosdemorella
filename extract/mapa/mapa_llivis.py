#!/usr/bin/env python3
"""Genera assets/images/ed-mapa-dena-llivis.svg: mapa de la Dena dels Llivis (apartat 1.1 del llibre), il·lustració
nova d'esta edició. Dades (extract/mapa/llivis/): Nomenclàtor Toponímic Valencià (masos, fonts, barrancs, serres),
vies pecuàries oficials (colades), OpenStreetMap (límit de la dena, camins, carretera CV-12).
Uso: python3 extract/mapa/mapa_llivis.py [dir node_modules con opentype.js; por defecto site/node_modules]
"""
import json, math, sys
from mapalib import (ROOT, glyph_defs, FILL, FILL_HI, INK, INK_SOFT, PAPER, Projection, label, labels_open, rings_of, svg_open,
                     text_paths)

D = ROOT / "extract/mapa/llivis"
OUT = ROOT / "assets/images/ed-mapa-dena-llivis.svg"
NODE_MODULES = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "site/node_modules")
W, H, MARGIN = 1000, 980, 70

# Els 21 masos tal com els enumera el llibre (1.1) → nom en el Nomenclàtor. Rètol = forma curta del llibre.
MASOS = [
    ("Marín", "Mas de Marín"), ("Adell", "Mas d’Adell"), ("Cros", "Mas de Cros"), ("Llivis", "Mas dels Llivis"),
    ("Torre Querol", "Torre Querol"), ("Modest", "Mas de Modest"), ("Cardona", "Mas de Cardona"),
    ("Marinet", "Mas de Marinet"), ("Torre Segura", "Torre Segura"), ("Planet", "Mas del Planet"),
    ("Solarreta", "Mas de Solarreta"), ("Julian", "Mas de Julian"), ("Oronal", "Mas de l’Oronal"),
    ("Racó", "Mas del Racó"), ("Mas Nou", "Mas Nou"), ("Torre Montserrat", "Torre Montserrat"),
    ("Torre Blanca", "Torre Blanca"), ("Guardiola", "Mas de Guardiola"), ("Giroveta", "Mas de Giroveta"),
    ("Garró", "Mas del Garró"), ("Olivares", "Mas d’Olivares"),
]
NTV_NAME = {"Marín": "Mas de Marín", "Adell": "Mas d'Adell", "Cros": "Mas de Cros", "Torre Querol": "Torre Querol",
            "Modest": "Mas de Modest", "Cardona": "Mas de Cardona", "Marinet": "Mas de Marinet",
            "Torre Segura": "Torre Segura", "Planet": "Mas de Planet", "Solarreta": "la Solaneta",
            "Julian": "Mas de Julià", "Oronal": "l'Oronal", "Racó": "Mas de Racó", "Mas Nou": "Mas Nou",
            "Torre Montserrat": "Torre Montserrat", "Torre Blanca": "Torre Blanca", "Guardiola": "Mas de Guardiola",
            "Giroveta": "Mas de la Giroveta", "Garró": "Mas del Garro", "Olivares": "Hostal d'Olivares"}
EXTRA_POINTS = {"Llivis": (-0.113709, 40.563293)}          # Masía dels Llivis (NGBE)
# Desplaçament del rètol respecte al punt (dx, dy, ancoratge); per defecte a la dreta
OFFSET = {"Llivis": (2, 17, "middle"), "Torre Segura": (-8, 4, "end"), "Torre Blanca": (-8, 4, "end"),
          "Garró": (8, -3, "start"), "Mas Nou": (8, 0, "start"), "Planet": (8, 6, "start"),
          "Cardona": (-8, 4, "end"), "Olivares": (8, -2, "start"), "Marín": (8, 8, "start"), "Racó": (2, -8, "middle")}
FONT_OFFSET = {"Font de Marín": (-6, 4, "end"), "Font dels Llivis": (6, 9, "start")}
# Posició (fracció de la longitud del tram interior) dels rètols de línia
FRAC = {"Vereda de los Llivis": 0.55, "Colada de la Rambla de Lacanar / Colada de la Cana de Ares": 0.75,
        "Rambla de la Canada d'Ares": 0.2, "cv12": 0.12, "Barranc de la Bellota": 0.7, "Riu de la Torre Segura": 0.62,
        "Serra de Marinet": 0.45, "Serra de Calduc": 0.5, "Colada del Campello": 0.5, "Colada de Candeales": 0.22,
        "Colada de la Sierra dels Llivis": 0.3}
# Fonts que cita el llibre (1.1) → nom NTV (o coordenada NGBE)
FONTS = [("Ullals de Torre Segura", "Ullals de la Torre Segura"), ("Font de Cardona", "Font de Cardona"),
         ("Font del Grèvol", (-0.106384, 40.528687)), ("Font dels Llivis", "Font dels Llivis"),
         ("Font de Marín", "Font del Mas de Marín")]
# Cursos d'aigua i colades amb rètol (nom del llibre → nom en la font de dades)
AIGUA_LABEL = {"Riu de la Torre Segura": "Riu Torre Segura", "Barranc de la Bellota": "Barranc de la Bellota",
               "Barranc del Garro": "Barranc de Garró", "Barranc del Mas de Racó": "Barranc de Racó",
               "Barranc de la Creu": "Barranc de Creus", "Rambla de la Canada d'Ares": "Rambla de la Cana d’Ares"}
COLADES = {"Vereda de los Llivis": "Sendera dels Llivis", "Colada del Campello": "Colada del Campello",
           "Colada de Candeales": "Colada de Candeales", "Colada de la Sierra dels Llivis": "Colada de la Serra dels Llivis",
           "Colada de la Rambla de Lacanar / Colada de la Cana de Ares": "Colada de la Cana d’Ares"}
SERRES = {"Serra de Calduc": "SERRA CALDUCH", "Serra de Marinet": "SERRA DE MARINET"}

ntv_p = json.load(open(D / "ntv-puntos.geojson", encoding="utf-8"))["features"]
ntv_l = json.load(open(D / "ntv-lineas.geojson", encoding="utf-8"))["features"]
vp = json.load(open(D / "vies-pecuaries-capa9.geojson", encoding="utf-8"))["features"]
osm = json.load(open(D / "osm.json", encoding="utf-8"))["elements"]
denes = json.load(open(ROOT / "extract/mapa/denes.osm.json", encoding="utf-8"))["relations"]
dena = max(rings_of(next(r for r in denes if r["name"] == "Dena dels Llivis")), key=len)

proj = Projection(dena, W, H - 60, MARGIN)          # deixa lloc a la llegenda (60 px) a baix


def lines_of(geom):
    if geom["type"] == "LineString":
        return [geom["coordinates"]]
    if geom["type"] == "MultiLineString":
        return geom["coordinates"]
    return []


def inside(lon, lat):
    n = len(dena); c = False; j = n - 1
    for i in range(n):
        xi, yi = dena[i]; xj, yj = dena[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi):
            c = not c
        j = i
    return c


def clip_runs(coords):
    """Trams d'una polilínia amb vèrtexs dins de la dena (més un vèrtex fora a cada extrem, per continuïtat)."""
    flags = [inside(*c[:2]) for c in coords]
    runs, cur = [], []
    for i, (c, f) in enumerate(zip(coords, flags)):
        if f:
            if not cur and i > 0:
                cur.append(coords[i - 1])
            cur.append(c)
        elif cur:
            cur.append(c); runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def pline(coords, tol=0.5):
    from mapalib import simplify
    pts = simplify([proj(*c[:2]) for c in coords], tol)
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def along(coords, frac=0.5):
    """Punt i angle (graus) a una fracció de la longitud d'una polilínia projectada."""
    pts = [proj(*c[:2]) for c in coords]
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(seg) or 1
    target, acc = total * frac, 0
    for (a, b), s in zip(zip(pts, pts[1:]), seg):
        if acc + s >= target:
            t = (target - acc) / (s or 1)
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            if ang > 90 or ang < -90:
                ang += 180
            return x, y, ang
        acc += s
    return pts[-1][0], pts[-1][1], 0


def longest(feats):
    return max(feats, key=lambda f: sum(len(l) for l in lines_of(f["geometry"])))


def rlabel(g, x, y, ang, dy=-5):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) translate({-g["width"] / 2:.1f} {dy})">'
            f'{g["uses"]}</g>')


# ---- rètols → traçats -------------------------------------------------------------------------------------------
req = [{"id": f"mas|{k}", "text": v, "size": 12, "weight": 600 if k == "Julian" else 500, "tracking": 0.2}
       for k, v in MASOS]
req += [{"id": f"font|{k}", "text": k, "size": 9.5, "weight": 400, "tracking": 0.2} for k, _ in FONTS]
req += [{"id": f"aigua|{k}", "text": v, "size": 10, "weight": 400, "tracking": 0.3} for k, v in AIGUA_LABEL.items()]
req += [{"id": f"colada|{k}", "text": v, "size": 10, "weight": 500, "tracking": 1.0} for k, v in COLADES.items()]
req += [{"id": f"serra|{k}", "text": v, "size": 11, "weight": 500, "tracking": 2.5} for k, v in SERRES.items()]
req += [{"id": "ermita", "text": "Ermita de Sant Pere Màrtir", "size": 10, "weight": 500, "tracking": 0.2},
        {"id": "isidre", "text": "Ermita de Sant Isidre", "size": 9.5, "weight": 400, "tracking": 0.2},
        {"id": "cv12", "text": "CV-12 (Morella – Ares)", "size": 9.5, "weight": 400, "tracking": 0.5},
        {"id": "km", "text": "1 km", "size": 10, "weight": 500, "tracking": 0.5},
        {"id": "N", "text": "N", "size": 12, "weight": 600, "tracking": 0}]
LEG = [("mas", "Mas"), ("julian", "Mas de Julian"), ("font", "Font"), ("ermita", "Ermita"), ("aigua", "Riu, barranc"),
       ("cami", "Camí, pista"), ("colada", "Assagador, colada"), ("carretera", "Carretera")]
req += [{"id": f"leg|{k}", "text": v, "size": 10, "weight": 400, "tracking": 0.2} for k, v in LEG]
G = text_paths(req, NODE_MODULES)

# ---- SVG ----------------------------------------------------------------------------------------------------------
svg = svg_open(W, H, "La Dena dels Llivis", "Mapa de la Dena dels Llivis: masos, fonts, barrancs, camins i colades")
svg.append(glyph_defs())
dpath = proj.path([dena], 0.4)
svg.append(f'<defs><clipPath id="dena"><path d="{dpath}"/></clipPath></defs>')
svg.append(f'<path d="{dpath}" fill="{FILL}" stroke="none"/>')
svg.append('<g clip-path="url(#dena)">')
# camins (OSM)
svg.append(f'<g fill="none" stroke="{INK_SOFT}" stroke-width="0.7" stroke-dasharray="3 2" opacity="0.8">')
for e in osm:
    if e.get("tags", {}).get("highway") in ("track", "unclassified", "path", "service") and e.get("geometry"):
        for run in clip_runs([(p["lon"], p["lat"]) for p in e["geometry"]]):
            svg.append(f'<path d="{pline(run, 0.9)}"/>')
svg.append('</g>')
# carretera CV-12
svg.append(f'<g fill="none" stroke="{INK_SOFT}" stroke-width="1.8">')
cv = [e for e in osm if e.get("tags", {}).get("highway") in ("primary", "primary_link") and e.get("geometry")]
for e in cv:
    for run in clip_runs([(p["lon"], p["lat"]) for p in e["geometry"]]):
        svg.append(f'<path d="{pline(run, 0.9)}"/>')
svg.append('</g>')
# cursos d'aigua (NTV)
svg.append(f'<g fill="none" stroke="#6f8797" stroke-width="0.8" stroke-linecap="round">')
aigua = [f for f in ntv_l if f["properties"]["elemento"].startswith(("Riu", "Rambla"))]
for f in aigua:
    w = 1.7 if f["properties"]["texto_normalizado"] in ("Riu de la Torre Segura", "Rambla de la Canada d'Ares", "Rambla de Sellumbres") else 0.8
    for l in lines_of(f["geometry"]):
        for run in clip_runs(l):
            svg.append(f'<path d="{pline(run, 0.8)}" stroke-width="{w}"/>')
svg.append('</g>')
# colades (vies pecuàries)
svg.append(f'<g fill="none" stroke="{INK}" stroke-width="1.3" stroke-dasharray="7 3 1.5 3" opacity="0.85">')
for f in vp:
    if f["properties"]["nomb_vp"] in COLADES:
        for l in lines_of(f["geometry"]):
            for run in clip_runs(l):
                svg.append(f'<path d="{pline(run, 0.8)}"/>')
svg.append('</g></g>')
# límit de la dena
svg.append(f'<path d="{dpath}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>')

# ---- punts i rètols -------------------------------------------------------------------------------------------------
svg.append(labels_open())
pts = {f["properties"]["texto_normalizado"]: f["geometry"]["coordinates"] for f in ntv_p}
# rètols de línies
for n in AIGUA_LABEL:
    ls = [r for f in aigua if f["properties"]["texto_normalizado"] == n for l in lines_of(f["geometry"]) for r in clip_runs(l)]
    if ls:
        x, y, a = along(max(ls, key=len), FRAC.get(n, 0.5))
        svg.append(f'<g fill="#4c6373">{rlabel(G[f"aigua|{n}"], x, y, a)}</g>')
done = set()
for f in vp:
    n = f["properties"]["nomb_vp"]
    if n in COLADES and n not in done:
        done.add(n)
        runs = [r for l in lines_of(f["geometry"]) for r in clip_runs(l)]
        runs += [r for g in vp if g is not f and g["properties"]["nomb_vp"] == n for l in lines_of(g["geometry"]) for r in clip_runs(l)]
        if runs:
            x, y, a = along(max(runs, key=len), FRAC.get(n, 0.5))
            svg.append(rlabel(G[f"colada|{n}"], x, y, a, dy=-6))
for f in ntv_l:
    n = f["properties"]["texto_normalizado"]
    if n in SERRES:
        x, y, a = along(max(lines_of(f["geometry"]), key=len), FRAC.get(n, 0.5))
        svg.append(f'<g fill="{INK_SOFT}">{rlabel(G[f"serra|{n}"], x, y, a, dy=-4)}</g>')
# carretera
if cv:
    runs = [r for e in cv for r in clip_runs([(p["lon"], p["lat"]) for p in e["geometry"]])]
    x, y, a = along(max(runs, key=len), FRAC.get("cv12", 0.5))
    svg.append(f'<g fill="{INK_SOFT}">{rlabel(G["cv12"], x, y, a, dy=-6)}</g>')
# fonts
for k, src in FONTS:
    lon, lat = pts[src] if isinstance(src, str) else src
    x, y = proj(lon, lat)
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{PAPER}" stroke="#4c6373" stroke-width="1.2"/>'
               f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1" fill="#4c6373" stroke="none"/>')
    fdx, fdy, fanc = FONT_OFFSET.get(k, (6, 3.5, "start"))
    svg.append(f'<g fill="#4c6373">{label(G[f"font|{k}"], x + fdx, y + fdy, fanc)}</g>')
# ermites i escola
for key, name, (dx, dy, anc) in (("ermita", "Ermita de Sant Pere Màrtir", (0, -11, "middle")),
                                  ("isidre", "Sant Isidre", (7, -6, "start"))):
    x, y = proj(*pts[name])
    svg.append(f'<path d="M{x-4:.1f} {y-2:.1f}h8M{x:.1f} {y-7:.1f}v11" stroke="{INK}" stroke-width="1.8" fill="none"/>')
    svg.append(label(G[key], x + dx, y + dy, anc))
# masos
for k, _ in MASOS:
    lon, lat = EXTRA_POINTS[k] if k in EXTRA_POINTS else pts[NTV_NAME[k]]
    x, y = proj(lon, lat)
    s = 4.2 if k == "Julian" else 3
    svg.append(f'<rect x="{x - s:.1f}" y="{y - s:.1f}" width="{2 * s}" height="{2 * s}" fill="{INK}" stroke="{PAPER}" stroke-width="1"/>')
    dx, dy, anchor = OFFSET.get(k, (7, 4, "start"))
    svg.append(label(G[f"mas|{k}"], x + dx, y + dy, anchor))
svg.append('</g>')

# ---- llegenda, escala i nord --------------------------------------------------------------------------------------
lx, ly = MARGIN - 30, H - 42
svg.append(f'<g fill="{INK}" stroke="none">')
x = lx
for k, _ in LEG:
    if k == "mas":
        svg.append(f'<rect x="{x}" y="{ly - 3}" width="6" height="6"/>')
    elif k == "julian":
        svg.append(f'<rect x="{x - 1}" y="{ly - 4}" width="8" height="8"/>')
    elif k == "font":
        svg.append(f'<circle cx="{x + 3}" cy="{ly}" r="3" fill="{PAPER}" stroke="#4c6373" stroke-width="1.2"/>')
    elif k == "ermita":
        svg.append(f'<path d="M{x} {ly}h7M{x + 3.5} {ly - 5}v9" stroke="{INK}" stroke-width="1.6" fill="none"/>')
    elif k == "aigua":
        svg.append(f'<path d="M{x - 2} {ly}q5 -5 10 0t10 0" stroke="#6f8797" stroke-width="1.4" fill="none"/>')
    elif k == "cami":
        svg.append(f'<path d="M{x - 2} {ly}h20" stroke="{INK_SOFT}" stroke-width="0.9" stroke-dasharray="3 2" fill="none"/>')
    elif k == "colada":
        svg.append(f'<path d="M{x - 2} {ly}h20" stroke="{INK}" stroke-width="1.3" stroke-dasharray="7 3 1.5 3" fill="none"/>')
    elif k == "carretera":
        svg.append(f'<path d="M{x - 2} {ly}h20" stroke="{INK_SOFT}" stroke-width="1.8" fill="none"/>')
    wide = k in ("aigua", "cami", "colada", "carretera")
    svg.append(label(G[f"leg|{k}"], x + (24 if wide else 12), ly + 3.5, "start"))
    x += G[f"leg|{k}"]["width"] + (24 if wide else 12) + 22
# escala: 1 km en píxels
km_px = proj.scale / 111.32          # 1 km en píxels (1° de latitud ≈ 111,32 km; y = -lat·scale)
sx, sy = W - MARGIN - km_px - 10, H - 42
svg.append(f'<path d="M{sx:.1f} {sy - 4}v8M{sx:.1f} {sy}h{km_px:.1f}M{sx + km_px:.1f} {sy - 4}v8" stroke="{INK}" stroke-width="1.4" fill="none"/>')
svg.append(label(G["km"], sx + km_px / 2, sy - 8))
nx, ny = W - MARGIN + 20, MARGIN - 10
svg.append(f'<path d="M{nx} {ny + 26}L{nx} {ny + 2}" stroke="{INK}" stroke-width="1.4"/><path d="M{nx - 5} {ny + 9}L{nx} {ny}L{nx + 5} {ny + 9}Z"/>')
svg.append(label(G["N"], nx, ny + 42))
svg.append('</g></svg>')
OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size // 1024} KB")
