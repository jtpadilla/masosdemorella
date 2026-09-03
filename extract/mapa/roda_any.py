#!/usr/bin/env python3
"""Genera assets/images/ed-roda-de-l-any.svg: la roda de l'any al mas (T-23), il·lustració nova d'esta edició.
Reuneix en un sol diagrama circular les dates i les faenes que el llibre dóna disperses pels capítols 3 a 7:
sembra, sega, esquiló, venda de corders, matança, mel, bolets, trufa, romeries, Sant Antoni, Sexenni, Fira...
Tot el que hi apareix està en el text (l'apartat s'indica en cada entrada de la taula MESOS); no s'hi afig res.
Uso: python3 extract/mapa/roda_any.py [dir node_modules con opentype.js; por defecto site/node_modules]
"""
import math, sys
from mapalib import ROOT, INK, INK_SOFT, PAPER, FILL, glyph_defs, label, svg_open, text_paths

OUT = ROOT / "assets/images/ed-roda-de-l-any.svg"
NODE_MODULES = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "site/node_modules")

# Categories i colors (tinta suau sobre paper)
CAT = {"camp": "#b0842e", "ramat": "#6e8a58", "casa": "#a8573a", "festa": "#5b7896"}
CAT_NOM = {"camp": "El camp", "ramat": "El ramat", "casa": "La casa", "festa": "Les festes"}

# Text de cada mes: (categoria, línia). Font entre parèntesis = apartat del llibre.
MESOS = [
    ("Gener", [
        ("casa", "Matança fins a Reis"),                       # 5.6
        ("festa", "5: bureo de Reis, es prova el panoli"),     # 7.3
        ("festa", "7: Sant Julià, patró de Morella"),          # 7.3
        ("festa", "16-17: Sant Antoni, fogueres als masos"),   # 7.3
        ("casa", "Carboneres: es talla la llenya"),            # 5.12
    ]),
    ("Febrer", [
        ("casa", "Adob d’aparells i ferramentes"),             # 5.8
        ("casa", "Llenya per al forn, segons la lluna"),       # 5.8
        ("casa", "Trufa, fins a març"),                        # 5.9
    ]),
    ("Març", [
        ("camp", "Creïlles d’hort, en lluna plena"),           # 3.6
        ("casa", "Blanquejar les parets amb calç"),            # 5.5
        ("casa", "Acaba la trufa"),                            # 5.9
    ]),
    ("Abril", [
        ("casa", "3: es paga l’arrendament, canvi de mas"),  # 6.4
        ("festa", "25: Sant Marc dels Castellons, rotllo"),    # 7.1
        ("festa", "29: Sant Pere Màrtir dels Llivis"),         # 2.1, 7.1
        ("festa", "De Pasqua a Pasqua Granada: la parròquia"),  # 6.4
    ]),
    ("Maig", [
        ("festa", "1r diumenge: rogatives"),                   # 7.2
        ("festa", "1: la Llàcua · 3: Santa Creu · 15: Sant Isidre"),  # 7.1
        ("casa", "Arreplegada de la mel, nous eixams"),        # 5.10
        ("ramat", "Esquiló (maig-juny)"),                      # 4.11
    ]),
    ("Juny", [
        ("camp", "1a quinzena: creïlles de secà i llegums"),   # 3.6
        ("camp", "Comença la sega"),                           # 3.8
        ("ramat", "Venda dels corders"),                       # 6.4
        ("festa", "13: Sant Antoni de la Vespa · 24: Sant Pere del Moll"),  # 7.1
        ("festa", "Del Corpus a l’Agost, sense festa al poble"),  # 6.4
    ]),
    ("Juliol", [
        ("camp", "Sega, garbes i batuda a l’era"),             # 3.8, 3.9
        ("ramat", "Venda dels corders"),                       # 6.4
        ("festa", "10: Sant Cristòfol, rotllo"),               # 7.1
    ]),
    ("Agost", [
        ("festa", "15: Mare de Déu d’Agost, els joves a Morella"),  # 6.4, 7.3
        ("festa", "L’Anunci, l’any abans del Sexenni"),        # 7.4
        ("festa", "Última setmana: entra el Sexenni (cada sis anys)"),  # 7.4
    ]),
    ("Setembre", [
        ("festa", "Sexenni: novenari, retaule i processons"),  # 7.4
        ("festa", "2n diumenge: Fira de Morella"),             # 7.5
    ]),
    ("Octubre", [
        ("camp", "Sembra dels cereals (octubre-novembre)"),    # 3.6
        ("casa", "Bolets: pebrassos, gírgoles, rovellons…"),   # 5.5
        ("casa", "Temps de caça"),                             # 6.4
        ("festa", "3a setmana: romeria a Vallivana (Sexenni)"),  # 7.4
    ]),
    ("Novembre", [
        ("camp", "Sembra, segons les fases de la lluna"),      # 6.4
        ("casa", "A finals de mes comença la trufa"),          # 5.9
    ]),
    ("Desembre", [
        ("casa", "Vespres de Nadal: la matança"),              # 5.6
        ("festa", "Bureos: guitarra, bandúrria i llaüt"),      # 5.6
        ("casa", "Carboneres (hivern)"),                       # 5.12
    ]),
]

# Arcs del cercle: (anell, categoria, dia inicial, dia final [0-365, pot passar de cap d'any])
M = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]   # inici de cada mes (dia de l'any)
ARCS = [
    ("camp", "camp", M[2], M[3]),          # creïlles d'hort (març)
    ("camp", "camp", M[5], M[5] + 15),     # creïlles de secà i llegums (1a quinzena de juny)
    ("camp", "camp", M[5], M[7]),          # sega (juny-juliol)
    ("camp", "camp", M[9], M[11]),         # sembra de cereals (octubre-novembre)
    ("ramat", "ramat", M[4], M[6]),        # esquiló (maig-juny)
    ("ramat", "ramat", M[5], M[7]),        # venda dels corders (juny-juliol)
    ("casa", "casa", M[4], M[5]),          # mel (maig)
    ("casa", "casa", M[8] + 20, M[10] + 15),  # bolets (tardor)
    ("casa", "casa", M[11] + 15, 365 + 6),    # matança (Nadal-Reis)
    ("casa2", "casa", M[10] + 20, 365 + 68),  # trufa (finals de novembre - primers de març)
    ("festa", "festa", M[3] + 24, M[6] + 10),   # romeries de les denes (25 abril - 10 juliol)
    ("festa", "festa", M[7], M[7] + 21),        # l'Anunci (tres primers caps de setmana d'agost)
    ("festa", "festa", M[7] + 24, M[8] + 7),    # Sexenni (última setmana d'agost - principi de setembre)
    ("festa", "festa", M[8] + 8, M[8] + 14),    # Fira (2n diumenge de setembre)
    ("festa", "festa", M[9] + 15, M[9] + 21),   # romeria a Vallivana (3a setmana d'octubre)
    ("festa", "festa", M[11] + 24, 365 + 6),    # Nadal - Reis: bureos
]
# Dies fixos (punts sobre l'anell de festes)
DIES = [4, 6, 16, M[3] + 2, M[3] + 24, M[3] + 28, M[4], M[4] + 2, M[4] + 14, M[5] + 12, M[5] + 23, M[6] + 9, M[7] + 14]
ESTACIONS = [("Hivern", 355, 365 + 79), ("Primavera", 79, 171), ("Estiu", 171, 265), ("Tardor", 265, 355)]

W, H = 1300, 1090
CX, CY = 650, 555
R_BLOC = 405                                   # radi on s'ancoren els blocs de text de cada mes
R_MES = (298, 322)                             # anell dels noms dels mesos
ANELLS = {"camp": (268, 290), "ramat": (242, 262), "casa": (216, 236), "casa2": (194, 212), "festa": (160, 186)}
R_EST = 140                                    # radi de les estacions


def ang(d):
    return -90 + 360 * (d % 365) / 365 if d != 365 else 270


def pol(r, a):
    return CX + r * math.cos(math.radians(a)), CY + r * math.sin(math.radians(a))


def sector(r1, r2, d1, d2):
    a1, a2 = -90 + 360 * d1 / 365, -90 + 360 * d2 / 365
    big = 1 if a2 - a1 > 180 else 0
    x1, y1 = pol(r2, a1); x2, y2 = pol(r2, a2); x3, y3 = pol(r1, a2); x4, y4 = pol(r1, a1)
    return (f"M{x1:.1f} {y1:.1f}A{r2} {r2} 0 {big} 1 {x2:.1f} {y2:.1f}L{x3:.1f} {y3:.1f}"
            f"A{r1} {r1} 0 {big} 0 {x4:.1f} {y4:.1f}Z")


def tangent(glyph, r, a):
    """Rètol tangent a l'anell en l'angle a (graus); es gira perquè es llija sense capgirar."""
    x, y = pol(r, a)
    rot = a + 90 if math.sin(math.radians(a)) < 0 else a - 90
    dy = 4 if math.sin(math.radians(a)) < 0 else -1
    return f'<g transform="rotate({rot:.1f} {x:.1f} {y:.1f})">{label(glyph, x, y + dy)}</g>'


# --- rètols ---------------------------------------------------------------------------------------------------
req = [{"id": "titol", "text": "L’ANY AL MAS", "size": 20, "weight": 600, "tracking": 2.5}]
req += [{"id": f"mes|{i}", "text": nom.upper(), "size": 11, "weight": 600, "tracking": 2} for i, (nom, _) in enumerate(MESOS)]
req += [{"id": f"cap|{i}", "text": nom, "size": 13, "weight": 600, "tracking": 0.3} for i, (nom, _) in enumerate(MESOS)]
req += [{"id": f"l|{i}|{j}", "text": t, "size": 11.5, "weight": 400, "tracking": 0}
        for i, (_, linies) in enumerate(MESOS) for j, (_, t) in enumerate(linies)]
req += [{"id": f"est|{n}", "text": n.upper(), "size": 10, "weight": 500, "tracking": 2.5} for n, _, _ in ESTACIONS]
req += [{"id": f"cat|{k}", "text": v, "size": 11.5, "weight": 500, "tracking": 0} for k, v in CAT_NOM.items()]
req.append({"id": "peu", "text": "Dates i faenes tal com les dóna el llibre (capítols 3 a 7). Any per any, «una altra vegada a començar».",
            "size": 11, "weight": 400, "tracking": 0})
G = text_paths(req, NODE_MODULES)

svg = svg_open(W, H, "L’any al mas",
               "Roda de l’any al mas: faenes del camp, del ramat i de la casa i festes de cada mes, segons el llibre")
svg.append(glyph_defs())

# --- cercle: sectors dels mesos, anells i arcs ------------------------------------------------------------------
svg.append(f'<g fill="none" stroke="{INK_SOFT}" stroke-width="0.8">')
for i in range(12):
    svg.append(f'<path d="{sector(R_MES[0], R_MES[1], M[i], M[i + 1])}" fill="{FILL if i % 2 else PAPER}"/>')
    x1, y1 = pol(ANELLS["festa"][0], ang(M[i])); x2, y2 = pol(R_MES[0], ang(M[i]))
    svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke-dasharray="2 3"/>')
svg.append(f'<circle cx="{CX}" cy="{CY}" r="{ANELLS["festa"][0]}"/>')
svg.append('</g>')
svg.append('<g stroke="none">')
for anell, cat, d1, d2 in ARCS:
    r1, r2 = ANELLS[anell]
    svg.append(f'<path d="{sector(r1, r2, d1, d2)}" fill="{CAT[cat]}" fill-opacity="0.8"/>')
for d in DIES:
    x, y = pol(sum(ANELLS["festa"]) / 2, ang(d))
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{CAT["festa"]}" stroke="{PAPER}" stroke-width="1.2"/>')
svg.append('</g>')

# --- rètols del cercle -------------------------------------------------------------------------------------------
svg.append(f'<g fill="{INK}">')
for i, (nom, _) in enumerate(MESOS):
    svg.append(tangent(G[f"mes|{i}"], sum(R_MES) / 2, -90 + 360 * (M[i] + M[i + 1]) / 2 / 365))
for n, d1, d2 in ESTACIONS:
    svg.append(tangent(G[f"est|{n}"], R_EST, -90 + 360 * ((d1 + d2) / 2 % 365) / 365))
svg.append(label(G["titol"], CX, CY - 22))
# llegenda de categories, dins del cercle
for k, key in enumerate(CAT):
    y = CY + 4 + k * 17
    g = G[f"cat|{key}"]
    svg.append(f'<rect x="{CX - g["width"] / 2 - 4:.1f}" y="{y - 9}" width="12" height="9" rx="1.5" fill="{CAT[key]}" fill-opacity="0.8"/>')
    svg.append(label(g, CX + 8, y, "middle"))
svg.append('</g>')

# --- blocs de text de cada mes, al voltant ---------------------------------------------------------------------
svg.append(f'<g fill="{INK}">')
LH = 15.5
for i, (nom, linies) in enumerate(MESOS):
    a = -90 + 360 * (M[i] + M[i + 1]) / 2 / 365
    x, y = pol(R_BLOC, a)
    c = math.cos(math.radians(a))
    if c > 0.35:
        anchor = "start"
    elif c < -0.35:
        anchor = "end"
    else:                       # dalt i baix: es desplaça cap al costat perquè no xoque amb el mes veí
        anchor, x = ("start", CX + 28) if c > 0 else ("end", CX - 28)
    n = len(linies) + 1
    y0 = y - (n - 1) * LH / 2 + 4
    svg.append(label(G[f"cap|{i}"], x, y0, anchor))
    for j, (cat, _) in enumerate(linies):
        g = G[f"l|{i}|{j}"]
        yy = y0 + (j + 1) * LH
        bx = x + 6 if anchor == "start" else x - g["width"] - 6
        svg.append(f'<circle cx="{bx:.1f}" cy="{yy - 4:.1f}" r="3" fill="{CAT[cat]}" fill-opacity="0.85"/>')
        svg.append(label(g, x + 14 if anchor == "start" else x, yy, anchor))
svg.append(f'<g fill="{INK_SOFT}">{label(G["peu"], CX, H - 18)}</g>')
svg.append('</g></svg>')
OUT.write_text("\n".join(svg), encoding="utf-8")
print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size // 1024} KB")
