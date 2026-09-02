#!/usr/bin/env python3
"""Reconstruye content/*.md a partir de extract/text/book.xml (pdftohtml -xml).

Reglas principales (ver CLAUDE.md):
- Se descartan cabecera corrida y número de página; el número impreso se conserva como ancla <a id="pNN" class="pag" data-p="NN">
  (en línea, en el punto exacto del salto, si cae dentro de un párrafo).
- Fuentes → estilo: F*=cursiva, E*/H*/B*=negrita. Cuerpos: 24pt sans negrita = capítulo (H1),
  21pt sans negrita precedido por glifo Symbol = apartado numerado (H2), 18pt sans negrita = subapartado (H3),
  13pt cursiva = pie de figura, 13pt redonda tras un número sin enlace = nota al pie, ≤10pt con enlace = llamada
  de nota, 10pt sin enlace = exponente (Km²), Symbol 18 = viñeta, Calligraphic = cita en bloque.
- Párrafos: interlineado normal ≈ 20-21 px; un salto > PARA_GAP abre párrafo. Una línea que no llega al margen
  derecho y va seguida de otra a interlineado normal es un salto de línea manual del original (citas de prensa).
  Un párrafo continúa en la página siguiente si su última línea llega al margen derecho.
- Los números de apartado se perdieron en el PDF (glifo Symbol vacío); se reasignan en orden por capítulo y se
  verifican contra el índice de marcadores (<outline>) del propio PDF.
- Las notas al pie se renumeran correlativamente dentro de cada capítulo.
"""
import html
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XML = ROOT / "extract/text/book.xml"
OUT = ROOT / "content"
IMG = "../assets/images"

SKIP_PAGES = {1, 2, 3, 4, 5}          # portada, blanco, índice, portadilla
PAGE_OFFSET = 5                        # física - 5 = impresa
LINE_TOL = 4                           # px: fragmentos con |Δtop| ≤ tol están en la misma línea
PARA_GAP = 25                          # px: salto vertical mayor → párrafo nuevo
COL_WIDTH = 510                        # px: ancho de la caja de texto
SHORT = 15                             # px: una línea que acaba a más de esto del margen es "corta"

# Pies de figura → fichero en assets/images (None = ilustración perdida en el original)
FIGURES = [
    ("Mapa dels Ports", "01-mapa-dels-ports.svg"),
    ("Mas dels Llivis", "02-mas-dels-llivis.jpg"),
    ("Colada de la Serra dels Llivis", "03-colada-de-la-serra-dels-llivis.jpg"),
    ("Ermita de San", "04-ermita-de-sant-pere-martir.jpg"),
    ("Rotllo de la festa", "05-rotllo-de-la-festa-ermita-sant-pere.jpg"),
    ("Aixades i ganxo", "06-aixades-i-ganxo.jpg"),
    ("L’arada o aladre", "07-arada-o-aladre.jpg"),
    ("Forques", "08-forques.jpg"),
    ("Falç i zoqueta", "09-falc-i-zoqueta.jpg"),
    ("Dalla", None),
    ("Carratellet", "11-carratellet.jpg"),
    ("Carrejador", None),
    ("L’era del Mas de Julian", "13-era-del-mas-de-julian.jpg"),
    ("Trill", None),
    ("Garbells", None),
    ("Ramat en el Mas de Julian", "16-ramat-en-el-mas-de-julian.jpg"),
    ("Barraca de pastor", "17-barraca-de-pastor-serra-calduch.jpg"),
    ("Esquella", "18-esquella.jpg"),
    ("Corrals del Mas de Julian", "19-corrals-del-mas-de-julian.jpg"),
    ("Bassa del Mas de Julian", "20-bassa-del-mas-de-julian.jpg"),
    ("Mas de Julian", "21-mas-de-julian.jpg"),
    ("Pastador del Mas de Julian", "22-pastador-del-mas-de-julian.jpg"),
    ("La pastera", "23-la-pastera.jpg"),
    ("Formatge, flitera i brull", "24-formatge-flitera-i-brull.jpg"),
    ("Portera", "25-portera.jpg"),
    ("La trufa", "26-la-trufa.jpg"),
    ("Foto familiar", "27-foto-familiar-mas-de-julian-1925.jpg"),
    ("Romeria de la Dena", "28-romeria-de-la-dena-dels-llivis.jpg"),
    ("Tadeo Julian (1928)", "29-tadeo-julian-1928-dansa-dels-llauradors.jpg"),
    ("Carrer amb adornaments", "30-carrer-amb-adornaments-sexenni-1982.jpg"),
]

CHAPTER_SLUGS = {
    "PRÒLEG": "00-proleg",
    "1.": "01-marc-geografic",
    "2.": "02-historia",
    "3.": "03-agricultura",
    "4.": "04-ramaderia",
    "5.": "05-la-llar",
    "6.": "06-forma-de-vida-i-costums",
    "7.": "07-cicle-anual-de-festes",
    "8.": "08-literatura-oral",
    "CONCLUSIONS": "09-conclusions",
    "BIBLIOGRAFIA": "10-bibliografia",
    "INDEX D’IL·LUSTRACIONS": "11-index-d-illustracions",
}
INDEX_SLUG = "11-index-d-illustracions"

# Ilustraciones de esta edición (no existen en el original): se insertan tras el bloque indicado, como imagen
# Markdown con fichero ed-*.svg; el sitio las marca como editoriales (rehype-book) por el prefijo del fichero.
INSERTS = {   # clave = inicio del bloque tras el que se inserta
    "12. Dena del Muixacre.": "![Les dotze denes del terme de Morella, amb la Dena dels Llivis destacada]"
                              f"({IMG}/ed-mapa-de-les-denes.svg)",
    "Mas de Marín, d’Adell, de Cros": "![La Dena dels Llivis: els vint-i-un masos, les fonts, els barrancs, els camins "
                                       f"i les colades]({IMG}/ed-mapa-dena-llivis.svg)",
}


class Font:
    def __init__(self, el):
        fam = el.get("family")
        self.size = int(el.get("size"))
        self.family = fam
        self.italic = fam.startswith("FAAAAA")
        self.bold = fam.startswith(("EAAAAA", "HAAAAA", "BAAAAA"))
        self.sans = "Sans" in fam
        self.symbol = fam == "Symbol"
        self.callig = "Calligraphic" in fam
        self.gray = el.get("color") == "#989898"


class Run:
    def __init__(self, el, font):
        self.top = int(el.get("top"))
        self.left = int(el.get("left"))
        self.width = int(el.get("width"))
        self.font = font
        raw = ET.tostring(el, encoding="unicode")
        self.href = "<a " in raw
        self.text = inner_text(raw)
        self.kind = self.classify()

    @property
    def right(self):
        return self.left + self.width

    def classify(self):
        f = self.font
        if f.family.endswith("DejaVuSans"):
            return "pageno" if (f.gray and f.size == 12) else "skip"   # nº de página / cabecera / "iii"
        if f.symbol:
            return "secnum" if f.size == 24 else "bullet"
        if f.sans and f.bold:
            return {24: "h1", 21: "h2", 18: "h3"}.get(f.size, "body")
        if f.italic and f.size == 13:
            return "caption"
        if f.size <= 10 and self.href:
            return "ref"
        if f.size == 10:
            return "sup2"
        if f.size <= 9:
            return "noteno"
        if f.size == 13:
            return "footnote"
        if f.callig:
            return "quote"
        return "body"


def inner_text(raw):
    s = raw[raw.index(">") + 1:raw.rindex("<")]
    s = re.sub(r"</?a[^>]*>", "", s)
    s = re.sub(r"</?[ib]>", "", s)
    return html.unescape(s)


def md_escape(s):
    return s.replace("*", r"\*").replace("_", r"\_").replace("#", r"\#")


class Converter:
    def __init__(self):
        self.chapters = []
        self.cur = None
        self.h1_num = None
        self.h2_count = 0
        self.para = []            # líneas del párrafo en construcción: listas de (texto, cursiva, negrita)
        self.para_kind = None
        self.para_page = None     # página en la que empezó el párrafo en construcción
        self.last_top = None
        self.last_short = False
        self.colright = 0
        self.colleft = 0
        self.page_no = None
        self.pending_anchor = ""
        self.page_continues = False
        self.ref_counter = 0      # llamadas de nota en el cuerpo
        self.note_counter = 0     # definiciones al pie

    # --- salida -----------------------------------------------------------
    def start_chapter(self, title):
        key = next((k for k in CHAPTER_SLUGS if title.startswith(k)), None)
        if key is None:
            sys.exit(f"capítulo desconocido: {title!r}")
        m = re.match(r"(\d+)\.", title)
        self.h1_num = int(m.group(1)) if m else None
        self.h2_count = 0
        self.note_counter = self.ref_counter = 0
        self.cur = {"slug": CHAPTER_SLUGS[key], "title": title, "blocks": [], "notes": [], "pages": []}
        self.chapters.append(self.cur)
        self.emit(f"# {title}")

    def emit(self, text):
        if self.pending_anchor:
            self.cur["blocks"].append(self.pending_anchor)
            self.pending_anchor = ""
        if self.cur["pages"][-1:] != [self.page_no]:
            self.cur["pages"].append(self.page_no)
        self.cur["blocks"].append(text)

    def flush(self):
        if not self.para:
            self.para_kind = None
            return
        kind = self.para_kind
        text = join_lines(self.para, plain=kind in ("h1", "h2", "h3", "caption"))
        self.para, self.para_kind = [], None
        if not text.strip():
            return
        anchor = ""
        if self.pending_anchor and self.para_page != self.page_no and kind != "h1":
            anchor, self.pending_anchor = self.pending_anchor, ""   # el párrafo venía de la página anterior
        self._emit_block(kind, text)
        if anchor:
            self.pending_anchor = anchor + self.pending_anchor

    def _emit_block(self, kind, text):
        if kind == "h1":
            self.start_chapter(text)
        elif kind == "h2":
            self.h2_count += 1
            num = f"{self.h1_num}.{self.h2_count} " if self.h1_num else ""
            self.emit(f"## {num}{text}")
        elif kind == "h3":
            self.emit(f"### {text}")
        elif kind == "caption":
            self.emit(figure(text))
        elif kind == "quote":
            self.emit("> " + text.replace("\\\n", "\\\n> "))
        elif kind == "bullet":
            self.emit("- " + text)
        elif kind == "footnote":
            self.cur["notes"].append((self.note_counter, text))
        else:
            text = re.sub(r"^(Ingredients|Preparació):", r"**\1:**", text)
            text = re.sub(r"^((?:<a id=\"p\d+\"[^>]*></a>)*)-(\s)", r"\1\\-\2", text, flags=re.M)   # raya de diálogo, no lista
            if self.cur["slug"] == INDEX_SLUG:
                text = "- " + re.sub(r"\s*\.{3,}\s*(\d+)$", r" — \1", text)
            self.emit(text)

    # --- entrada ----------------------------------------------------------
    def page(self, pnum, runs):
        if pnum in SKIP_PAGES:
            return
        runs.sort(key=lambda r: (r.top, r.left))
        lines = []
        for r in runs:
            tol = 8 if r.kind in ("ref", "sup2", "noteno") else LINE_TOL
            if lines and abs(r.top - lines[-1][0].top) <= tol:
                lines[-1].append(r)
            else:
                lines.append([r])
        self.page_no = pnum - PAGE_OFFSET
        self.pending_anchor += f'<a id="p{self.page_no}" class="pag" data-p="{self.page_no}"></a>'
        colleft = min((r.left for r in runs if r.kind == "body"), default=0)
        self.colleft = colleft
        self.colright = colleft + COL_WIDTH
        self.last_top = None
        self.last_short = False
        for line in lines:
            line.sort(key=lambda r: r.left)
            self.line(line)
        # fin de página: el párrafo sigue en la siguiente solo si la última línea está llena
        if self.para_kind not in ("body", "quote") or self.last_short:
            self.flush()
        else:
            self.page_continues = True

    def line(self, runs):
        kinds = {r.kind for r in runs}
        if kinds <= {"skip", "pageno", "secnum"}:
            return
        top = runs[0].top
        gap = None if self.last_top is None else top - self.last_top
        if gap is None and self.page_continues:
            gap = 0                                   # el párrafo venía de la página anterior
        self.page_continues = False
        prev_short = self.last_short
        self.last_top = top
        self.last_short = runs[-1].right < self.colright - SHORT
        if runs[0].kind == "noteno":
            self.flush()
            self.note_counter += 1
            self.para_kind = "footnote"
            self.para = [self.styled(runs[1:])]
            return
        if self.para_kind == "footnote" and gap is not None and gap <= PARA_GAP and all(r.font.size == 13 for r in runs):
            self.para.append(self.styled(runs))
            return
        main = next((r for r in runs if r.kind not in ("ref", "sup2", "bullet", "body")), runs[0])
        kind = main.kind
        dash_item = (runs[0].kind == "body" and runs[0].left > self.colleft + 12
                     and (re.match(r"-\s", runs[0].text.lstrip()) or runs[0].text.strip() == "-"))
        if "bullet" in kinds or dash_item:
            kind = "bullet"
            if dash_item:
                runs[0].text = re.sub(r"^\s*-\s*", "", runs[0].text)
        elif kind in ("body", "ref", "sup2"):
            kind = "body"
        continuing = gap is not None and gap <= PARA_GAP
        if kind == "body" and self.para_kind in ("quote", "bullet") and continuing:
            kind = self.para_kind
        new_para = kind != self.para_kind or "bullet" in kinds or dash_item or not continuing
        if kind == "h1" and self.para_kind == "h1" and gap is not None and gap < 35:
            new_para = False
        if self.cur and self.cur["slug"] == INDEX_SLUG and kind == "body":
            new_para = True
        if new_para:
            self.flush()
            self.para_kind = kind
            self.para_page = self.page_no
        line = self.styled([r for r in runs if r.kind != "bullet"])
        if self.pending_anchor and kind in ("body", "quote"):
            line.insert(0, (self.pending_anchor, False, False))
            self.pending_anchor = ""
        dash = bool(runs[0].text.strip()) and re.match(r"-\s", runs[0].text.lstrip()) is not None
        if not new_para and (prev_short or dash) and kind in ("body", "quote"):
            line.insert(0, ("\n", False, False))      # salto de línea manual del original
        self.para.append(line)

    def styled(self, runs):
        out = []
        prev_right = None
        for r in runs:
            t = re.sub(r"\s+", " ", r.text)
            if prev_right is not None and r.left - prev_right > 3 and out and not out[-1][0].endswith(" ") and not t.startswith(" "):
                out.append((" ", None, None))
            prev_right = r.right
            if r.kind == "sup2":
                out.append(("²", None, None))
            elif r.kind == "ref":
                self.ref_counter += 1
                out.append((f"[^{self.ref_counter}]", None, None))
            else:
                out.append((md_escape(t), r.font.italic, r.font.bold))
        return out


def merge_runs(runs):
    """Fusiona fragmentos contiguos del mismo estilo. Espacios y marcadores heredan el estilo vecino; la puntuación
    también, si sus dos vecinos coinciden. Un fragmento alfabético pegado a la palabra siguiente (p. ej. "L" +
    "*laurà*", cursiva parcial del original) adopta el estilo del fragmento más largo."""
    runs = [(t, i, b) for t, i, b in runs if t]
    fixed = []
    for k, (t, i, b) in enumerate(runs):
        if t.strip() == "":
            i = b = None
        elif not re.search(r"[0-9A-Za-zÀ-ÿ]", t):
            prev = runs[k - 1][1:] if k else None
            nxt = runs[k + 1][1:] if k + 1 < len(runs) else None
            if prev is None or nxt is None or prev == nxt:
                i = b = (None, None) if (prev is not None and nxt is not None) else (False, False)
                i, b = i[0], b[1]
        fixed.append((t, i, b))
    merged = []
    for t, i, b in fixed:
        if merged:
            pt, pi, pb = merged[-1]
            if (pi == i or i is None or pi is None) and (pb == b or b is None or pb is None):
                merged[-1] = (pt + t, pi if pi is not None else i, pb if pb is not None else b)
                continue
        merged.append((t, i, b))
    for k in range(len(merged) - 1):
        t, i, b = merged[k]
        nt, ni, nb = merged[k + 1]
        m1 = re.search(r"(?<![^\s])([A-Za-zÀ-ÿ]+)$", t)
        m2 = re.match(r"([A-Za-zÀ-ÿ]+)(?![^\s])", nt)
        if m1 and m2 and (i, b) != (ni, nb):
            if len(m1.group(1)) <= len(m2.group(1)):
                merged[k] = (t[: m1.start()], i, b)
                merged[k + 1] = (m1.group(1) + nt, ni, nb)
            else:
                merged[k] = (t + m2.group(1), i, b)
                merged[k + 1] = (nt[m2.end():], ni, nb)
    return [m for m in merged if m[0]]


def render_runs(runs):
    s = ""
    for t, i, b in merge_runs(runs):
        m = re.match(r"^([\s,.;:!?)”»…]*)(.*?)([\s,.;:!?(”»…]*)$", t, flags=re.S)
        lead, core, trail = m.group(1), m.group(2), m.group(3)
        if not core:
            s += t
            continue
        if b:
            core = f"**{core}**"
        if i:
            core = f"*{core}*"
        s += lead + core + trail
    return s


def plain_runs(runs):
    return "".join(t for t, _, _ in runs)


def join_lines(lines, plain=False):
    text = ""
    for ln in lines:
        p = plain_runs(ln) if plain else render_runs(ln)
        if p.startswith("\n"):
            text += "\\\n" + p[1:].strip()
            continue
        p = p.strip()
        if False:
            pass
        elif not text:
            text = p
        elif text.endswith("-"):
            text += p
        else:
            text += " " + p
    text = re.sub(r"(?<=\S) ([.,;:!?])(?=\s|$)", r"\1", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\*\*? \*\*?", " ", text)      # "*a* *b*" → "*a b*" (mismo estilo, separado por espacio)
    text = text.replace("383.549 Km2", "383.549 Km²")   # el PDF pinta el 2 en superíndice pero lo guarda en línea
    return text


def figure(caption):
    for prefix, fn in FIGURES:
        if caption.startswith(prefix):
            if fn is None:
                return (f'<figure class="perduda"><div class="placeholder">Il·lustració perduda en l’original</div>'
                        f"<figcaption>{caption}</figcaption></figure>")
            return f"![{caption}]({IMG}/{fn})"
    sys.exit(f"pie de figura sin correspondencia: {caption!r}")


def assemble(blocks):
    """Une bloques con línea en blanco; convierte «**Ingredients:** - a» + «\\- b» en lista."""
    out = []
    in_list = False
    for blk in blocks:
        m = re.match(r"\*\*Ingredients:\*\* - (.*)", blk)
        if m:
            out += ["", "**Ingredients:**", "", "- " + m.group(1)]
            in_list = True
            continue
        if in_list and blk.startswith("\\- "):
            out.append("- " + blk[3:])
            continue
        in_list = False
        if out:
            out.append("")
        out.append(blk)
        for key, fig in INSERTS.items():
            if blk.startswith(key):
                out += ["", fig]
    return "\n".join(out).lstrip("\n")


def check_outline(chapters, tree):
    """Los H2 reasignados deben coincidir con los marcadores del PDF."""
    want = [re.sub(r"^(\d+\.\d+)\. ", r"\1 ", it.text) for it in tree.iter("item") if re.match(r"\d+\.\d+\. ", it.text)]
    got = [b[3:] for ch in chapters for b in ch["blocks"] if b.startswith("## ")]
    if want != got:
        sys.exit("los apartados no coinciden con el índice del PDF:\n" + "\n".join(f"{a!r} != {b!r}" for a, b in zip(want, got) if a != b))


def main():
    tree = ET.parse(XML)
    fonts = {}
    conv = Converter()
    for page in tree.getroot().iter("page"):
        for fs in page.iter("fontspec"):
            fonts[fs.get("id")] = Font(fs)
        conv.page(int(page.get("number")), [Run(t, fonts[t.get("font")]) for t in page.iter("text")])
    conv.flush()
    if conv.pending_anchor:
        conv.emit("")
    check_outline(conv.chapters, tree)

    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.md"):
        old.unlink()
    for n, ch in enumerate(conv.chapters):
        body = assemble(ch["blocks"]).rstrip() + "\n"
        if ch["notes"]:
            body += "\n" + "\n".join(f"[^{k}]: {t}" for k, t in ch["notes"]) + "\n"
        refs = len(set(re.findall(r"\[\^(\d+)\]", body)))
        if refs != len(ch["notes"]):
            sys.exit(f"{ch['slug']}: {refs} llamadas de nota pero {len(ch['notes'])} notas")
        pages = ch["pages"]
        fm = f"---\ntitle: \"{ch['title']}\"\norder: {n}\npages: [{pages[0]}, {pages[-1]}]\n---\n\n"
        (OUT / f"{ch['slug']}.md").write_text(fm + body, encoding="utf-8")
        print(f"{ch['slug']:32} págs {pages[0]:>3}-{pages[-1]:<3} notas={len(ch['notes'])}")


if __name__ == "__main__":
    main()
