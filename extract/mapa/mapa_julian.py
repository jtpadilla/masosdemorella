#!/usr/bin/env python3
"""Genera assets/images/ed-mas-de-julian.svg: croquis de l'entorn del Mas de Julian amb les sis fotografies del llibre
fetes al mas (13 era, 16 ramat, 19 corrals, 20 bassa, 21 el mas, 22 pastador) i el lloc i la direcció des d'on es van
prendre. Il·lustració nova d'esta edició.

Base: ortofotografia PNOA (IGN, CC-BY 4.0) del punt "Mas de Julià" del Nomenclàtor (40.56883, -0.15797), sobre la qual
s'han traçat a mà la casa, l'edifici annex, l'hort tancat, l'era i les parets principals (Catastro no té l'edifici);
camí d'OpenStreetMap. Les posicions de càmera són aproximades (deduïdes de les pròpies fotografies); la de la bassa,
només aproximada. Uso: python3 extract/mapa/mapa_julian.py [dir node_modules con opentype.js; por defecto site/node_modules]
"""
import base64, json, math, sys
from mapalib import ROOT, FILL, INK, INK_SOFT, PAPER, glyph_defs, label, labels_open, svg_open, text_paths

OUT = ROOT / "assets/images/ed-mas-de-julian.svg"
NODE_MODULES = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "site/node_modules")
THUMBDIR = ROOT / "extract/mapa/llivis/thumbs"   # miniatures (360 px) de les fotos, generades amb ImageMagick
W, H = 1000, 880
ACCENT = "#8a3b1c"
WATER = "#6f8797"

# Ortofoto descarregada: bbox (lat 40.566130–40.571530, lon -0.161523 – -0.154415), 1400×1400 px; el traçat es fa
# sobre la finestra ampliada (500×500 px a partir de 430,470; ×2) → coordenades "z" de 0 a 1000.
ORTHO_BBOX = (40.566130, -0.161523, 40.571530, -0.154415)
ZOOM = (430, 470, 2.0)
PLAN_X, PLAN_Y, PLAN_S = 40, 40, 0.60           # z → paper


def z2p(zx, zy):
    return PLAN_X + zx * PLAN_S, PLAN_Y + zy * PLAN_S


def ll2z(lon, lat):
    lat1, lon1, lat2, lon2 = ORTHO_BBOX
    px = (lon - lon1) / (lon2 - lon1) * 1400
    py = (lat2 - lat) / (lat2 - lat1) * 1400
    return (px - ZOOM[0]) * ZOOM[2], (py - ZOOM[1]) * ZOOM[2]


def poly(pts, **attrs):
    d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in (z2p(*p) for p in pts)) + "Z"
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{d}" {a}/>'


def line(pts, **attrs):
    d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in (z2p(*p) for p in pts))
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{d}" fill="none" {a}/>'


# ---- traçat sobre l'ortofoto (coordenades z) --------------------------------------------------------------------
CASA = [(505, 400), (605, 405), (600, 500), (495, 495)]
CORRALS = [(600, 420), (645, 428), (642, 482), (600, 492)]
ANNEX = [(590, 608), (655, 598), (660, 655), (596, 665)]
HORT = [(555, 505), (600, 500), (605, 598), (560, 606)]
ERA = (215, 555, 62)
PARETS = [
    [(95, 150), (150, 110), (300, 80), (450, 95), (560, 160), (600, 250), (605, 330), (580, 392)],
    [(280, 545), (400, 510), (470, 485), (500, 470)],
    [(150, 600), (100, 640), (60, 720)],
    [(270, 612), (330, 650), (380, 705)],
    [(610, 690), (680, 760), (760, 860), (800, 960)],
    [(645, 440), (760, 500), (900, 560), (1000, 590)],
    [(150, 110), (60, 40)],
]
CAMI = [ll2z(*p) for p in json.load(open(ROOT / "extract/mapa/llivis/cami-julia.json"))]
CAMI2 = [(560, 20), (590, 150), (605, 300), (640, 330), (652, 400)]   # accés des del nord (traçat)

# ---- fotografies: (número, fitxer, càmera z, direcció de mira en graus (0 = est, 90 = nord), obertura, peu curt)
FOTOS = [
    (21, "21-mas-de-julian", (555, 740), 92, 40, "El mas, des del sud"),
    (13, "13-era-del-mas-de-julian", (262, 560), 195, 45, "L’era; al fons, Cinctorres"),
    (16, "16-ramat-en-el-mas-de-julian", (700, 560), 118, 42, "El ramat; al fons, la Mola de la Garumba"),
    (19, "19-corrals-del-mas-de-julian", (665, 462), 165, 40, "Els corrals"),
    (20, "20-bassa-del-mas-de-julian", (578, 560), None, None, "La bassa (posició aproximada)"),
    (22, "22-pastador-del-mas-de-julian", (522, 452), None, None, "El pastador i el forn (interior)"),
]

# ---- rètols ---------------------------------------------------------------------------------------------------------
req = [{"id": "casa", "text": "Mas de Julian", "size": 12, "weight": 600, "tracking": 0.3},
       {"id": "corrals", "text": "corrals", "size": 10, "weight": 400, "tracking": 0.2},
       {"id": "annex", "text": "edifici annex", "size": 10, "weight": 400, "tracking": 0.2},
       {"id": "hort", "text": "hort", "size": 10, "weight": 400, "tracking": 0.2},
       {"id": "era", "text": "l’era", "size": 11, "weight": 500, "tracking": 0.3},
       {"id": "cami", "text": "camí", "size": 9.5, "weight": 400, "tracking": 0.4},
       {"id": "nord", "text": "cap a la Mola de la Garumba (5 km) i Morella", "size": 9.5, "weight": 400, "tracking": 0.3},
       {"id": "oest", "text": "cap a Cinctorres (5 km)", "size": 9.5, "weight": 400, "tracking": 0.3},
       {"id": "calduch", "text": "cap al Mas de Racó, per la Serra Calduch", "size": 9.5, "weight": 400, "tracking": 0.3},
       {"id": "m50", "text": "50 m", "size": 10, "weight": 500, "tracking": 0.5},
       {"id": "N", "text": "N", "size": 12, "weight": 600, "tracking": 0},
       {"id": "titol", "text": "Les fotografies del llibre fetes al mas", "size": 11, "weight": 500, "tracking": 1.2}]
req += [{"id": f"n{n}", "text": str(n), "size": 11, "weight": 600, "tracking": 0} for n, *_ in FOTOS] + [{"id": "n27", "text": "27", "size": 11, "weight": 600, "tracking": 0}]
PEUS = {n: peu.split("; ") for n, _, _, _, _, peu in FOTOS}
PEUS[27] = ["La família del mas (1925).", "Retrat d’estudi, sense localització."]
NOTA = ["Els números remeten a l’índex d’il·lustracions.", "El sector indica cap a on mira cada fotografia;", "les posicions són aproximades."]
for n, parts in PEUS.items():
    req += [{"id": f"peu{n}|{i}", "text": t, "size": 9.5, "weight": 400, "tracking": 0.2} for i, t in enumerate(parts)]
req += [{"id": f"nota|{i}", "text": t, "size": 9.5, "weight": 400, "tracking": 0.2} for i, t in enumerate(NOTA)]
G0 = text_paths(req, NODE_MODULES)
G = dict(G0)
for n, parts in PEUS.items():
    G[f"peu{n}"] = [G0[f"peu{n}|{i}"] for i in range(len(parts))]
G["nota"] = [G0[f"nota|{i}"] for i in range(len(NOTA))]

svg = svg_open(W, H, "El Mas de Julian", "Croquis de l'entorn del Mas de Julian amb les fotografies del llibre i el lloc des d'on es van fer")
svg.append(glyph_defs())
# fons del croquis (i retall de tot el que es dibuixa dins)
PX, PY, PW = PLAN_X - 10, PLAN_Y - 10, 1000 * PLAN_S + 20
svg.append(f'<defs><clipPath id="marc"><rect x="{PX}" y="{PY}" width="{PW:.0f}" height="{PW:.0f}"/></clipPath></defs>')
svg.append(f'<rect x="{PX}" y="{PY}" width="{PW:.0f}" height="{PW:.0f}" fill="{FILL}"/>')
svg.append('<g clip-path="url(#marc)">')
# parets, camins
for p in PARETS:
    svg.append(line(p, stroke=INK_SOFT, stroke_width=1.1, stroke_linejoin="round"))
svg.append(line(CAMI, stroke=INK_SOFT, stroke_width=0.9, stroke_dasharray="4 2.5"))
svg.append(line(CAMI2, stroke=INK_SOFT, stroke_width=0.9, stroke_dasharray="4 2.5"))
# hort i era
svg.append(poly(HORT, fill="#dfe0c9", stroke=INK_SOFT, stroke_width=0.9))
ex, ey = z2p(ERA[0], ERA[1]); er = ERA[2] * PLAN_S
svg.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{er:.1f}" fill="{PAPER}" stroke="{INK}" stroke-width="1.4"/>'
           f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{er - 4:.1f}" fill="none" stroke="{INK_SOFT}" stroke-width="0.6"/>')
# edificis
svg.append(poly(CORRALS, fill="#b8ab93", stroke=INK, stroke_width=1))
svg.append(poly(CASA, fill=INK, stroke=INK, stroke_width=1))
svg.append(poly(ANNEX, fill="#7a7062", stroke=INK, stroke_width=1))
# cons de visió
for n, _, cam, ang, ap, _ in FOTOS:
    if ang is None:
        continue
    cx, cy = z2p(*cam)
    r = 62
    a1, a2 = math.radians(ang - ap / 2), math.radians(ang + ap / 2)
    x1, y1 = cx + r * math.cos(a1), cy - r * math.sin(a1)
    x2, y2 = cx + r * math.cos(a2), cy - r * math.sin(a2)
    svg.append(f'<path d="M{cx:.1f} {cy:.1f}L{x1:.1f} {y1:.1f}A{r} {r} 0 0 0 {x2:.1f} {y2:.1f}Z" fill="{ACCENT}" opacity="0.13"/>')
    svg.append(f'<path d="M{x1:.1f} {y1:.1f}L{cx:.1f} {cy:.1f}L{x2:.1f} {y2:.1f}" fill="none" stroke="{ACCENT}" stroke-width="0.7" opacity="0.6"/>')
svg.append('</g>')
# rètols del croquis
svg.append(labels_open())
cx, cy = z2p(552, 380); svg.append(label(G["casa"], cx, cy))
cx, cy = z2p(622, 458); svg.append(f'<g stroke="none">{label(G["corrals"], cx, cy + 3)}</g>')
cx, cy = z2p(668, 632); svg.append(label(G["annex"], cx, cy + 3, "start"))
cx, cy = z2p(580, 540); svg.append(label(G["hort"], cx, cy + 3))
svg.append(label(G["era"], ex, ey + 4))
cx, cy = z2p(*CAMI2[2]); svg.append(label(G["cami"], cx + 8, cy, "start"))
svg.append(f'<g fill="{INK_SOFT}">{label(G["calduch"], PLAN_X + 1000 * PLAN_S - 14, PLAN_Y + 1000 * PLAN_S - 40, "end")}</g>'
           f'<path d="M{PLAN_X + 1000 * PLAN_S - 4} {PLAN_Y + 1000 * PLAN_S - 44}l-8 -5v10z" fill="{INK_SOFT}"/>')
# fletxes de direcció als marges
svg.append(f'<g fill="{INK_SOFT}">{label(G["nord"], PLAN_X + 300, PLAN_Y + 8)}'
           f'<g transform="translate({PLAN_X + 6} {PLAN_Y + 300}) rotate(-90)">{label(G["oest"], 0, 0)}</g></g>')
svg.append(f'<path d="M{PLAN_X + 300} {PLAN_Y - 6}l-5 8h10z" fill="{INK_SOFT}"/><path d="M{PLAN_X - 7} {PLAN_Y + 300}l8 -5v10z" fill="{INK_SOFT}"/>')
svg.append('</g>')
# marcadors de càmera
for n, _, cam, ang, _, _ in FOTOS:
    cx, cy = z2p(*cam)
    dash = ' stroke-dasharray="2 2"' if ang is None else ""
    svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" fill="{PAPER}" stroke="{ACCENT}" stroke-width="1.6"{dash}/>')
    svg.append(f'<g fill="{ACCENT}">{label(G[f"n{n}"], cx, cy + 4)}</g>')

# ---- miniatures: tira inferior; retrat de família a la dreta ---------------------------------------------------
TW, TH, GAP = 156, 104, 8
tx, ty = 12, PLAN_Y + 1000 * PLAN_S + 36
for n, fn, cam, ang, _, peu in FOTOS:
    data = base64.b64encode((THUMBDIR / f"{fn}.jpg").read_bytes()).decode()
    svg.append(f'<image x="{tx}" y="{ty}" width="{TW}" height="{TH}" preserveAspectRatio="xMidYMid slice" '
               f'xlink:href="data:image/jpeg;base64,{data}" href="data:image/jpeg;base64,{data}"/>')
    svg.append(f'<rect x="{tx}" y="{ty}" width="{TW}" height="{TH}" fill="none" stroke="{INK_SOFT}" stroke-width="0.8"/>')
    svg.append(f'<circle cx="{tx + 12}" cy="{ty + 12}" r="9" fill="{PAPER}" stroke="{ACCENT}" stroke-width="1.4"/>')
    svg.append(f'<g fill="{ACCENT}">{label(G[f"n{n}"], tx + 12, ty + 16)}</g>')
    for i, part in enumerate(G[f"peu{n}"]):
        svg.append(f'<g fill="{INK}">{label(part, tx + TW / 2, ty + TH + 14 + i * 12)}</g>')
    tx += TW + GAP
# retrat de família (fig. 27), sense localització
RX, RY, RW = 690, 96, 296
data = base64.b64encode((THUMBDIR / "27-foto-familiar-mas-de-julian-1925.jpg").read_bytes()).decode()
RH = int(RW * 1675 / 2362)
svg.append(f'<g fill="{INK}">{label(G["titol"], RX + RW / 2, 54)}</g>')
svg.append(f'<image x="{RX}" y="{RY}" width="{RW}" height="{RH}" xlink:href="data:image/jpeg;base64,{data}" href="data:image/jpeg;base64,{data}"/>')
svg.append(f'<rect x="{RX}" y="{RY}" width="{RW}" height="{RH}" fill="none" stroke="{INK_SOFT}" stroke-width="0.8"/>')
svg.append(f'<circle cx="{RX + 12}" cy="{RY + 12}" r="9" fill="{PAPER}" stroke="{ACCENT}" stroke-width="1.4"/><g fill="{ACCENT}">{label(G["n27"], RX + 12, RY + 16)}</g>')
for i, part in enumerate(G["peu27"]):
    svg.append(f'<g fill="{INK}">{label(part, RX + RW / 2, RY + RH + 16 + i * 13)}</g>')
for i, part in enumerate(G["nota"]):
    svg.append(f'<g fill="{INK_SOFT}">{label(part, RX + RW / 2, RY + RH + 60 + i * 13)}</g>')

# ---- escala i nord -------------------------------------------------------------------------------------------------
m_per_z = (ORTHO_BBOX[3] - ORTHO_BBOX[1]) / 1400 * 111320 * math.cos(math.radians(ORTHO_BBOX[0])) / ZOOM[2]
px50 = 50 / m_per_z * PLAN_S
sx, sy = PLAN_X + 1000 * PLAN_S - px50 - 14, PLAN_Y + 1000 * PLAN_S - 18
svg.append(f'<g fill="{INK}"><path d="M{sx} {sy - 4}v8M{sx} {sy}h{px50:.1f}M{sx + px50:.1f} {sy - 4}v8" stroke="{INK}" stroke-width="1.4" fill="none"/>'
           f'{label(G["m50"], sx + px50 / 2, sy - 8)}')
nx, ny = PLAN_X + 1000 * PLAN_S - 20, PLAN_Y + 30
svg.append(f'<path d="M{nx} {ny + 26}L{nx} {ny + 2}" stroke="{INK}" stroke-width="1.4"/><path d="M{nx - 5} {ny + 9}L{nx} {ny}L{nx + 5} {ny + 9}Z"/>{label(G["N"], nx, ny + 42)}</g>')
svg.append('</svg>')
OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size // 1024} KB")
