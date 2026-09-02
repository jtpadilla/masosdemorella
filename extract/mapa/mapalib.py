"""Utilidades comunes de los mapas SVG del libro (mapa_ports.py, mapa_denes.py):
geometría OSM → anillos, proyección, simplificación, rótulos en EB Garamond como trazados (text2path.mjs)."""
import json, math, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER, FILL, FILL_HI, INK, INK_SOFT = "#fbf8f2", "#ece6d8", "#d3c7b0", "#2b2620", "#5b554b"


def rings_of(rel):
    """Encadena los tramos «outer» de una relación OSM en anillos cerrados de (lon, lat)."""
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
    """Douglas-Peucker sobre una polilínea abierta."""
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


def centroid(ring):
    """Centroide (área) de un anillo de puntos proyectados."""
    a = cx = cy = 0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        f = x1 * y2 - x2 * y1
        a += f; cx += (x1 + x2) * f; cy += (y1 + y2) * f
    a *= 3
    return (cx / a, cy / a) if a else ring[0]


class Projection:
    """Equirectangular centrada, escalada para encajar los puntos en (W × H) con margen."""

    def __init__(self, points, W, H, margin):
        lat0 = sum(p[1] for p in points) / len(points)
        self.kx = math.cos(math.radians(lat0))
        xs = [p[0] * self.kx for p in points]; ys = [-p[1] for p in points]
        self.scale = min((W - 2 * margin) / (max(xs) - min(xs)), (H - 2 * margin) / (max(ys) - min(ys)))
        self.ox = (W - (max(xs) - min(xs)) * self.scale) / 2 - min(xs) * self.scale
        self.oy = (H - (max(ys) - min(ys)) * self.scale) / 2 - min(ys) * self.scale

    def __call__(self, lon, lat):
        return (lon * self.kx * self.scale + self.ox, -lat * self.scale + self.oy)

    def ring(self, ring, tol=0.6):
        pp = [self(*p) for p in ring]
        h = len(pp) // 2                  # anillo cerrado: por mitades (DP degenera si inicio == fin)
        return simplify(pp[: h + 1], tol)[:-1] + simplify(pp[h:], tol)

    def path(self, rings, tol=0.6):
        return "".join("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in self.ring(r, tol)) + "Z" for r in rings)


def text_paths(items, node_modules):
    """items: [{id, text, size, weight, tracking}] → {id: {d, width}} vía text2path.mjs (opentype.js)."""
    res = subprocess.run(["node", str(ROOT / "extract/mapa/text2path.mjs"), node_modules],
                         input=json.dumps(items), capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


def label(glyph, x, y, anchor="middle"):
    tx = x - (glyph["width"] if anchor == "end" else glyph["width"] / 2 if anchor == "middle" else 0)
    return f'<path transform="translate({tx:.1f} {y:.1f})" d="{glyph["d"]}"/>'


def svg_open(W, H, title, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{desc}">',
            f'<title>{title}</title>', f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']


def regions(proj, polys, highlight=()):
    """polys: [(nombre, anillos)]. Contorno exterior grueso (debajo), rellenos con línea fina (encima)."""
    out = [f'<g fill="none" stroke="{INK}" stroke-width="4" stroke-linejoin="round">']
    out += [f'<path d="{proj.path(r)}"/>' for _, r in polys]
    out.append(f'</g><g stroke="{INK_SOFT}" stroke-width="0.9" stroke-linejoin="round">')
    out += [f'<path d="{proj.path(r)}" fill="{FILL_HI if n in highlight else FILL}"/>' for n, r in polys]
    out.append('</g>')
    return out


def labels_open():
    return f'<g fill="{INK}" stroke="{PAPER}" stroke-width="3" stroke-linejoin="round" paint-order="stroke">'
